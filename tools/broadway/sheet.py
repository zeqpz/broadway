"""Contact sheet for picking art. usage: python tools/broadway/sheet.py out.jpg cols cell file... [--bg r,g,b]"""
import os, sys
from PIL import Image, ImageDraw

args = sys.argv[1:]
bg = (52, 50, 70)
if "--bg" in args:
    i = args.index("--bg"); bg = tuple(int(v) for v in args[i + 1].split(",")); del args[i:i + 2]
out, cols, cell = args[0], int(args[1]), int(args[2])
fs = args[3:]
rows = (len(fs) + cols - 1) // cols
s = Image.new("RGBA", (cols * cell, rows * (cell + 18)), bg + (255,))
d = ImageDraw.Draw(s)
for k, f in enumerate(fs):
    im = Image.open(f).convert("RGBA")
    im.thumbnail((cell, cell))
    x, y = (k % cols) * cell, (k // cols) * (cell + 18)
    s.alpha_composite(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2))
    d.text((x + 4, y + cell + 2), os.path.basename(f), fill=(255, 255, 255, 255))
s.convert("RGB").save(out, quality=85)
print(out, s.size)
