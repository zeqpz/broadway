"""Measure the frame's opening (frontend/assets/frame.webp) and write the fractions the page places it by
(art/outage-src/frame_fit.json, read by tools/outage/reskin_outage.py):
  fw, fh   the opening's width / height as a fraction of the frame picture's
  kx, ky   the frame's left / top edge before the opening, as a fraction of the opening's width / height
  mx, my   the board's margin: how far the frame (and what hangs off it) reaches past the opening, as a fraction of it
The opening is the see-through region round the centre (alpha < 110), flood-filled; its inner rectangle is the
largest box fully inside it (rows/columns at least 97% open), so ragged cable tips poking in don't shrink it.
usage: python tools/outage/frame_fit.py"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
im = Image.open(os.path.join(ROOT, "frontend", "assets", "frame.webp")).convert("RGBA")
W, H = im.size
al = np.asarray(im.getchannel("A"))
clear = al < 110
lab, _ = ndimage.label(clear)
hole = lab == lab[H // 2, W // 2]
if hole[0].any() or hole[-1].any() or hole[:, 0].any() or hole[:, -1].any():
    raise SystemExit("the opening leaks to the frame's edge")
rows = hole.mean(1)
cols = hole.mean(0)
ys = np.nonzero(rows > rows.max() * .97)[0]
xs = np.nonzero(cols > cols.max() * .97)[0]
oy0, oy1, ox0, ox1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
ow, oh = ox1 - ox0, oy1 - oy0
solid = al > 40
sy, sx = np.nonzero(solid)
over = dict(left=(ox0 - sx.min()) / ow, right=(sx.max() + 1 - ox1) / ow, top=(oy0 - sy.min()) / oh, bottom=(sy.max() + 1 - oy1) / oh)
fit = {"fw": ow / W, "fh": oh / H, "kx": ox0 / ow, "ky": oy0 / oh,
       # the board's margin covers the steel bars (about .11-.14 of the opening) plus a little: the cables at the
       # top-left, the lever box and the dangling plug may hang past it (they are decoration, not the frame)
       "mx": .19, "my": .23,   # (review: the lever ran off a phone, the spark off the top at every desktop size)
       "opening_px": [int(ox0), int(oy0), int(ow), int(oh)], "frame_px": [W, H], "overhang": over}
out = os.path.join(ROOT, "art", "outage-src", "frame_fit.json")
json.dump(fit, open(out, "w"), indent=1)
print(json.dumps(fit, indent=1))
