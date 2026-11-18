"""Make the frame's breaker switch throwable (owner pass 2, 2026-11-18).

From the frame as fitted (art/outage-src/frame_prelever.webp, a copy of tools/outage/gen_ui.py's frame.webp):
  - the red handle is cut out as its own sprite (assets/lever.webp): the red shaft and knob, their white shine and
    their black ink outline (only ink right next to the red, so none of the box's own outlines come with it)
  - an empty switch box (art/outage-src/ui/switchbox.png, drawn by tools/outage/gen_switchbox.py to match) is laid
    over the old box and handle in the frame (assets/frame.webp), so nothing of the old handle shows
  - art/outage-src/lever.json: the sprite's box in the frame picture and its pivot (the new box's slot), as fractions
The page mirrors the handle about that pivot to throw the switch: down = OFF (the board idle), up = ON (a round playing).
usage: python tools/outage/frame_lever.py"""
import json, os, shutil
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = os.path.join(ROOT, "frontend", "assets")
FR = os.path.join(A, "frame.webp")
KEEP = os.path.join(ROOT, "art", "outage-src", "frame_prelever.webp")
if not os.path.exists(KEEP):
    shutil.copyfile(FR, KEEP)
src = Image.open(KEEP).convert("RGBA")
im = np.asarray(src).astype(np.int32)
H, W, _ = im.shape
r, g, b, a = (im[..., i] for i in range(4))
lum = (r + g + b) / 3
sat = im[..., :3].max(-1) - im[..., :3].min(-1)

# ---- the handle
zone = np.zeros((H, W), bool)
zone[int(H * .38):int(H * .66), int(W * .84):] = True
red = zone & (r > 120) & (g < 110) & (b < 110) & (r - g > 60) & (a > 128)
lab, n = ndimage.label(red)
sz = ndimage.sum(red, lab, range(1, n + 1))
red = np.isin(lab, 1 + np.nonzero(sz > sz.max() * .02)[0])
redfill = ndimage.binary_fill_holes(ndimage.binary_closing(red, iterations=6))   # shaft + knob with the shine inside
hl = redfill & ~red & (lum > 200)
ink = ndimage.binary_dilation(redfill, iterations=11) & ~redfill & (lum < 70) & (a > 128)
handle = redfill | hl | ink
handle = ndimage.binary_dilation(handle, iterations=1) & (a > 0)
ys, xs = np.nonzero(handle)
hx0, hy0, hx1, hy1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
sprite = np.zeros_like(im)
sprite[handle] = im[handle]
spr = Image.fromarray(sprite.astype(np.uint8), "RGBA").crop((hx0, hy0, hx1, hy1))
# the shaft's top end (where it leaves the slot): the centre of the red's top rows
ry, rx = np.nonzero(red)
top = ry.min()
tx = rx[ry < top + 10].mean()

# ---- the empty box laid over the old switch: the old box + handle's extent, padded
oldbox = zone & (a > 200) & ((sat < 40) | handle) & (np.arange(W)[None, :] > hx0 - 140)
oy, ox = np.nonzero(oldbox | handle)
bx0, by0, bx1, by1 = int(ox.min()) - 6, int(oy.min()) - 6, min(W, int(ox.max()) + 10), int(oy.max()) + 6
box = Image.open(os.path.join(ROOT, "art", "outage-src", "ui", "switchbox.png")).convert("RGBA")
box = box.crop(box.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox())
bw = bx1 - bx0
bh = round(bw * box.height / box.width)
cy = (by0 + by1) / 2
by0n = round(cy - bh / 2)
boxr = box.resize((bw, bh), Image.LANCZOS)
out = src.copy()
out.alpha_composite(boxr, (bx0, by0n))
# the new slot (the darkest wide bar in the box's upper third), where the handle's top end goes
ba = np.asarray(boxr).astype(np.int32)
dark = (ba[..., :3].mean(-1) < 50) & (ba[..., 3] > 200)
dark[int(bh * .45):] = False
dark[:int(bh * .08)] = False
dlab, dn = ndimage.label(dark)
best, bestw = None, 0
for i, sl in enumerate(ndimage.find_objects(dlab)):
    w = sl[1].stop - sl[1].start
    if w > bestw and w < bw * .85 and (sl[0].stop - sl[0].start) < bh * .12:
        best, bestw = sl, w
sy = (best[0].start + best[0].stop) / 2 + by0n
sx = (best[1].start + best[1].stop) / 2 + bx0
out.save(FR, "WEBP", quality=92, alpha_quality=100, method=6)

# ---- the handle's place: its top end on the slot's centre
ox_, oy_ = sx - (tx - hx0), sy - (top - hy0)
spr.save(os.path.join(A, "lever.webp"), "WEBP", quality=92, alpha_quality=100, method=6)
info = {"box": [ox_ / W, oy_ / H, spr.width / W, spr.height / H],
        "pivot": [(tx - hx0) / spr.width, (top - hy0) / spr.height],
        "switchbox_px": [bx0, by0n, bw, bh], "slot_px": [round(sx), round(sy)], "frame_px": [W, H]}
json.dump(info, open(os.path.join(ROOT, "art", "outage-src", "lever.json"), "w"), indent=1)
print(json.dumps(info))
