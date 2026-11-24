"""Measure the frame's opening (frontend/assets/frame.webp) and write the fractions the page places it by
(art/broadway-src/frame_fit.json, read by tools/broadway/reskin_outage.py):
  fw, fh   the opening's width / height as a fraction of the frame picture's
  kx, ky   the frame's left / top edge before the opening, as a fraction of the opening's width / height
  mx, my   the board's margin: how far the frame (and what hangs off it) reaches past the opening, as a fraction of it
The opening is the see-through region round the centre (alpha < 110), flood-filled; its inner rectangle is the
largest box fully inside it (rows/columns at least 97% open), so ragged cable tips poking in don't shrink it.
usage: python tools/broadway/frame_fit.py"""
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
       # (owner pass 4, 2026-11-18: "make the board bigger") the board's margins, each side its own, as fractions of
       # the board's box - just what the frame needs past it (overhang x the opening, less the 18 px the opening sits
       # inside the board): top .262 shows the cable loop and leaves the frayed wire's sparks room; bottom .12 is the
       # hazard bar; right .185 is the breaker box; left .155 the cables (an upright phone lets them run off its
       # edge: .08, the bar alone). The symmetric .19 / .23 of before left 86 px of air under the frame.
       "mt": .262, "mb": .12, "ml": .155, "mr": .185, "ml_phone": .08,
       "opening_px": [int(ox0), int(oy0), int(ow), int(oh)], "frame_px": [W, H], "overhang": over}
out = os.path.join(ROOT, "art", "broadway-src", "frame_fit.json")
json.dump(fit, open(out, "w"), indent=1)
print(json.dumps(fit, indent=1))
