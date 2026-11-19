"""Take the frame's dangling power cord out of the picture so the page can swing it with physics (owner pass 3, 2026-11-18).

From frontend/assets/frame.webp (after tools/outage/frame_lever.py):
  assets/plug.webp        the plug (and the last bit of cord going into it), cropped
  assets/frame.webp       the frame without the cord and the plug (the clamp on the right bar stays: the cord comes
                          out from under it)
  assets/cable.json       the cord's drawn centreline from the clamp to the plug (frame px, the rope's starting shape),
                          its thickness, the plug's box and the point on it the cord goes into, the frame's size
The page (frontend/cable.js) draws the cord as a rope of points under gravity and hangs the plug off its end.
usage: python tools/outage/frame_cable.py   (keeps art/outage-src/frame_precable.webp the first time)"""
import json, os, shutil
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = os.path.join(ROOT, "frontend", "assets")
FR = os.path.join(A, "frame.webp")
KEEP = os.path.join(ROOT, "art", "outage-src", "frame_precable.webp")
if not os.path.exists(KEEP):                 # (frame_lever.py writes it; this is only for a frame made without it)
    shutil.copyfile(FR, KEEP)
src = Image.open(KEEP).convert("RGBA")
im = np.asarray(src).astype(np.int32)
H, W, _ = im.shape
a = im[..., 3]
lum = im[..., :3].mean(-1)
yy, xx = np.mgrid[0:H, 0:W]

# what belongs to the cord and the plug: everything opaque right of the bar below the clamp, and below the frame
PLUG_Y = int(H * .876)                               # the frame's bottom edge: below it only the plug hangs
cord_zone = (((xx > W * .94) & (yy > H * .726)) | ((xx > W * .933) & (yy > H * .757))) & (yy < PLUG_Y)
plug_zone = (yy >= PLUG_Y) & (xx > W * .84)
take = (a > 8) & (cord_zone | plug_zone)

# the cord's centreline: per row, the middle of the cord's run (its grey core and black outline), top to bottom
pts = []
for y in range(int(H * .726), PLUG_Y + 40, 12):
    xs = np.nonzero(take[y] & (lum[y] < 120))[0]
    xs = xs[xs > W * .93]
    if len(xs) < 4:
        continue
    runs = np.split(xs, np.nonzero(np.diff(xs) > 3)[0] + 1)
    run = max(runs, key=len)
    pts.append([float(run.mean()), float(y), int(len(run))])
pts = np.array(pts)
thick = float(np.median(pts[:, 2]))
line = [[round(x, 1), round(y, 1)] for x, y, _ in pts]

# the plug sprite: the opaque pixels below the frame's bottom edge (with the cord's last few px going into it)
pm = (a > 8) & plug_zone
ys, xs = np.nonzero(pm)
px0, py0, px1, py1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
plug = np.zeros_like(im)
plug[pm] = im[pm]
Image.fromarray(plug.astype(np.uint8), "RGBA").crop((px0, py0, px1, py1)).save(
    os.path.join(A, "plug.webp"), "WEBP", quality=92, alpha_quality=100, method=6)
# where the cord goes into it: the cord's centre on the plug's top row
top = np.nonzero(pm[py0 + 2])[0]
neck = [float(top.mean()), float(py0)]

out = im.copy()
out[take, 3] = 0
Image.fromarray(out.astype(np.uint8), "RGBA").save(FR, "WEBP", quality=92, alpha_quality=100, method=6)
# the bar the cord hangs beside (cable.js keeps the rope out of it): its right edge below the clamp, and its foot
oa = out[..., 3] > 40
rights = [int(np.nonzero(oa[y])[0].max()) for y in range(int(H * .775), int(H * .85), 6) if oa[y].any()]
bar_right = float(np.median(rights))
foot = int(np.nonzero(oa[:, int(bar_right) - 40])[0].max())
info = {"frame": [W, H], "line": line, "thick": round(thick, 1), "plug": [px0, py0, px1 - px0, py1 - py0], "neck": neck,
        "bar_right": bar_right, "frame_bottom": foot}
json.dump(info, open(os.path.join(A, "cable.json"), "w"), indent=1)
print("cord points", len(line), "thickness", thick, "plug", info["plug"], "neck", neck, "bar right", bar_right, "foot", foot)
