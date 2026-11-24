"""The voodoo multiplier glyphs and border (Multi values on potions and cells): art/broadway-src/ui/vnum.png (a 4x3 sheet:
x 0 1 2 / 3 4 5 6 / 7 8 9 .) and vborder.png -> Real-ESRGAN x2 -> frontend/assets/vnum/<g>.webp (256 px tall, each glyph
cropped to its ink, sitting on a shared baseline) and assets/vnum/border.webp, plus assets/vnum/glyphs.css (one class
per glyph with its aspect ratio). The page writes values through vNum() (index.html).
usage: python tools/broadway/vnum.py"""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import upscale4k

ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "art", "broadway-src", "ui")
OUT = os.path.join(ROOT, "frontend", "assets", "vnum")
os.makedirs(OUT, exist_ok=True)
NAMES = ["x", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "dot"]
sheet = upscale4k.up4(Image.open(os.path.join(SRC, "vnum.png")).convert("RGBA"), long_edge=2048)
W, H = sheet.size
cw, ch = W / 4, H / 3
TALL = 256
cells = []
for i, n in enumerate(NAMES):
    c = sheet.crop((round((i % 4) * cw), round((i // 4) * ch), round((i % 4 + 1) * cw), round((i // 4 + 1) * ch)))
    a = np.asarray(c.getchannel("A")) > 20
    from scipy import ndimage
    lab, nlab = ndimage.label(a)
    if nlab > 1:                                  # only the glyph itself: no sliver of a neighbouring cell's glyph
        sz = ndimage.sum(a, lab, range(1, nlab + 1))
        a = np.isin(lab, 1 + np.nonzero(sz >= sz.max() * .08)[0])
        c = c.copy(); al = np.asarray(c.getchannel("A")).copy(); al[~a] = 0; c.putalpha(Image.fromarray(al))
    ys, xs = np.nonzero(a)
    cells.append((n, c, xs.min(), xs.max() + 1, ys.min(), ys.max() + 1))
# each row of the sheet sits a little differently in its cells: scale every row so its digits are TALL px, and stand
# every glyph on the baseline (its offset from its own row's digit baseline kept, so the x and the dot sit right)
css = []
k = 0
for r in range(3):
    row = cells[r * 4:(r + 1) * 4]
    dg = [e for e in row if e[0].isdigit()]
    kr = TALL / np.median([e[5] - e[4] for e in dg])
    rb = np.median([e[5] for e in dg])
    k = max(k, kr)
    for n, c, x0, x1, y0, y1 in row:
        g = c.crop((x0, y0, x1, y1))
        g = g.resize((max(1, round(g.width * kr)), max(1, round(g.height * kr))), Image.LANCZOS)
        lift = max(0, round((rb - y1) * kr))
        if n == "dot":                            # the drawn full stop is huge: a third of a digit, on the baseline
            f = TALL * .36 / g.height
            g = g.resize((max(1, round(g.width * f)), max(1, round(g.height * f))), Image.LANCZOS)
            lift = round(TALL * .02)
        if n.isdigit():
            g = g.resize((g.width, TALL), Image.LANCZOS) if abs(g.height - TALL) > 2 else g
            lift = 0
        canvas = Image.new("RGBA", (g.width, TALL), (0, 0, 0, 0))
        canvas.alpha_composite(g, (0, max(0, TALL - g.height - lift)))
        canvas.save(os.path.join(OUT, n + ".webp"), "WEBP", quality=92, alpha_quality=100, method=6)
        css.append(f'.vg.g-{n} {{ background-image: url("{n}.webp"); aspect-ratio: {canvas.width} / {canvas.height}; }}')
border = upscale4k.up4(Image.open(os.path.join(SRC, "vborder.png")).convert("RGBA"), long_edge=1024)
bb = border.getchannel("A").getbbox()
border.crop(bb).save(os.path.join(OUT, "border.webp"), "WEBP", quality=90, alpha_quality=100, method=6)
open(os.path.join(OUT, "glyphs.css"), "w").write("/* tools/broadway/vnum.py */\n" + "\n".join(css) + "\n")
print("glyphs", len(NAMES), "k", round(k, 3), "border", border.crop(bb).size)
