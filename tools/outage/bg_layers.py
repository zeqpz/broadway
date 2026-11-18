"""Power Outage: the layers that keep the blacked-out office alive (frontend/assets/bg/, read by frontend/bgscene.js).

From the painting (art/outage-src/bg_v1.png, 1536 x 864; the game's plate is its 4K upscale):
  sky.webp      the window sky (and the moon and the stars) as one flat pale-blue shape, cut to the windows' box: the
                lightning flashes it, and the clouds drifting past the moon are masked by it (so they pass behind the
                dark towers and in front of the moon)
  scene.json    where everything sits, as fractions of the painting: the candle flames (each a live flat cartoon flame),
                their flat light pools, the moon, the chandelier, the sky box, and lit windows for the dead skyline
usage: python tools/outage/bg_layers.py"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "art", "outage-src", "bg_v1.png")
OUT = os.path.join(ROOT, "frontend", "assets", "bg")
im = np.asarray(Image.open(SRC).convert("RGB")).astype(int)
H, W, _ = im.shape
r, g, b = im[..., 0], im[..., 1], im[..., 2]

# the windows' region (hand-placed round the three windows) and the sky inside it: deep navy, darker towers excluded
X0, Y0, X1, Y1 = 360, 120, 1110, 462
box = np.zeros((H, W), bool)
box[Y0:Y1, X0:X1] = True
blue = box & (r < 20) & (b > g + 12) & (b >= 26)
# the sky lightens toward the horizon and the towers are only a shade darker than it: compare each pixel with its own
# row's sky (the row's bright blues), not with one fixed colour
ref = np.zeros(H)
for y in range(Y0, Y1):
    v = b[y][blue[y]]
    ref[y] = np.percentile(v, 85) if len(v) > 20 else 255
refm = ref[:, None]
sky = blue & (b >= refm * .86)
moon = box & (r > 200) & (g > 170)
sky = ndimage.binary_closing(sky | moon, iterations=2)          # the stars' dots close up
lab, n = ndimage.label(sky)
sizes = ndimage.sum(sky, lab, range(1, n + 1))
sky = np.isin(lab, 1 + np.nonzero(sizes > 300)[0])               # panes only, no stray specks
ys, xs = np.nonzero(sky)
sx0, sy0, sx1, sy1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
a = (sky[sy0:sy1, sx0:sx1] * 255).astype(np.uint8)
rgb = np.zeros((sy1 - sy0, sx1 - sx0, 3), np.uint8)
rgb[...] = (214, 232, 255)
os.makedirs(OUT, exist_ok=True)
k = 2.5                                                          # the plate is 2.5x the painting
skyim = Image.fromarray(np.dstack([rgb, a]), "RGBA").resize((round((sx1 - sx0) * k), round((sy1 - sy0) * k)), Image.LANCZOS)
skyim.save(os.path.join(OUT, "sky.webp"), "WEBP", quality=90, alpha_quality=90, method=6)

# the dead skyline: building pixels in the windows (dark, below the moon's line), a few lit windows to blink
tower = blue & (b < refm * .8)
tower[:300] = False
tower[405:] = False                                              # the tree line below the towers stays dark
tower = ndimage.binary_erosion(tower, np.ones((7, 5), bool))
cand = np.argwhere(tower)
rng = np.random.default_rng(7)
lights = []
for _ in range(400):
    if len(lights) >= 18 or not len(cand):
        break
    y, x = cand[rng.integers(len(cand))]
    if all(abs(x - lx) > 14 or abs(y - ly) > 10 for lx, ly in lights):
        lights.append((int(x), int(y)))

f = lambda x, y: [round(x / W, 5), round(y / H, 5)]
scene = {
    "size": [W, H],
    "sky": [round(sx0 / W, 5), round(sy0 / H, 5), round((sx1 - sx0) / W, 5), round((sy1 - sy0) / H, 5)],
    "moon": f(719, 238) + [round(32 / W, 5)],
    # flames: [x, y of the flame's base, height] (the painted flame is covered by a live one); pools: [x, y, radius]
    "flames": [f(255, 446) + [round(30 / H, 5)], f(1210, 276) + [round(28 / H, 5)],
               f(1238, 257) + [round(31 / H, 5)], f(1266, 272) + [round(28 / H, 5)]],
    "pools": [f(255, 432) + [round(42 / W, 5)], f(1238, 252) + [round(92 / W, 5)]],
    "chandelier": f(763, 84) + [round(150 / W, 5)],
    "lights": [f(x, y) for x, y in lights],
}
json.dump(scene, open(os.path.join(OUT, "scene.json"), "w"), indent=1)
print("sky", skyim.size, "lights", len(lights), "->", OUT)
