"""Fit owner-pass-2 art (tools/outage/gen_pass2.py) into frontend/assets."""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import upscale4k
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "art", "outage-src", "ui")
A = os.path.join(ROOT, "frontend", "assets")


def contain(im, size):
    bb = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    im = im.crop(bb)
    W, H = size
    k = min(W / im.width, H / im.height) * .98
    sm = im.convert("RGBa").resize((round(im.width * k), round(im.height * k)), Image.LANCZOS).convert("RGBA")
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.alpha_composite(sm, ((W - sm.width) // 2, (H - sm.height) // 2))
    return out


sign = upscale4k.up4(Image.open(os.path.join(RAW, "logo_sign3.png")).convert("RGBA"), long_edge=2400)
contain(sign, (1200, 900)).save(os.path.join(A, "logo_sign.webp"), "WEBP", quality=90, alpha_quality=100, method=6)
icon = upscale4k.up4(Image.open(os.path.join(RAW, "bonus_icon.png")).convert("RGBA"), long_edge=1600)
contain(icon, (640, 640)).save(os.path.join(A, "bonus_icon.webp"), "WEBP", quality=90, alpha_quality=100, method=6)
for n in ("banner_fs", "banner_xfs", "banner_boost"):
    Image.open(os.path.join(RAW, n + "2.png")).convert("RGB").resize((1440, 810), Image.LANCZOS).save(
        os.path.join(A, "bonus", n + ".webp"), "WEBP", quality=88, method=6)
print("fit: logo_sign, bonus_icon, 3 banners")
