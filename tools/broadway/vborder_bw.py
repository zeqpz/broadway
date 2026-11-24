"""The Multi value's ring (assets/vnum/border.webp): a round neon tube - a thick black outline, a hot-pink tube, a white-hot
core line - drawn at 4x and averaged down, the middle clear. usage: python tools/broadway/vborder_bw.py"""
import os
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S, K = 512, 4
N = S * K
im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
c, r = N / 2, N * .43
for w, col in ((.135, (17, 17, 17, 255)), (.095, (255, 63, 164, 255)), (.03, (255, 236, 248, 255))):
    t = N * w / 2
    d.ellipse([c - r - t, c - r - t, c + r + t, c + r + t], outline=col, width=int(2 * t))
im = im.resize((S, S), Image.LANCZOS)
im.save(os.path.join(ROOT, "frontend", "assets", "vnum", "border.webp"), "WEBP", quality=94, alpha_quality=100, method=6)
print("border", im.size)
