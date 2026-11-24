"""Make the Multi numerals recolourable (owner pass 3, 2026-11-18: "the text the colour of the multiplier, green to red
to purple for max wins, glowing slightly from the text").

Each glyph (frontend/assets/vnum/<g>.webp: a cyan fill, a deep-blue shade, a white shine, a black outline) is split
into an INK layer - every pixel as black or white over the fill: a pixel p on the line from black to the fill colour F
is black at alpha 1 - t (t = p.F / F.F), one brighter than F is white - written to vnum/ink_<g>.webp. The page draws
each glyph as that ink over a gradient of the value's own colour (--heat), masked by the glyph's own silhouette (the
original file's alpha), so the outline, shade and shine stay and only the colour changes.
Prints the glyphs' sizes (the CSS aspect ratios, read by tools/broadway/reskin_outage.py from the files themselves).
usage: python tools/broadway/vnum_ink.py   (after tools/broadway/vnum.py)"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, "frontend", "assets", "vnum")
NAMES = ["x", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "dot"]
for n in NAMES:
    im = np.asarray(Image.open(os.path.join(D, n + ".webp")).convert("RGBA")).astype(np.float32)
    rgb, a = im[..., :3], im[..., 3] / 255
    sat = rgb.max(-1) - rgb.min(-1)
    pick = (a > .95) & (sat > 120) & (rgb.mean(-1) > 150)
    F = np.median(rgb[pick], axis=0) if pick.sum() > 50 else np.array([63., 224., 255.])
    t = (rgb @ F) / float(F @ F)
    ink = np.zeros_like(im)
    dark = t < 1
    ink[..., 3] = np.where(dark, np.clip(1 - t, 0, 1), np.clip((t - 1.02) / .14, 0, 1)) * a * 255
    ink[..., :3] = np.where(dark[..., None], 0, 255)
    Image.fromarray(ink.round().clip(0, 255).astype(np.uint8), "RGBA").save(
        os.path.join(D, "ink_" + n + ".webp"), "WEBP", quality=94, alpha_quality=100, method=6)
    w, h = Image.open(os.path.join(D, n + ".webp")).size
    print(n, w, h, "fill", F.round())
