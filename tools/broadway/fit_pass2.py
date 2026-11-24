"""Fit owner-pass-2 art (tools/broadway/gen_pass2.py) into frontend/assets."""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import upscale4k
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "art", "broadway-src", "ui")
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


# (owner pass 5) the title sign is no longer fitted here: assets/logo_sign.webp and its glow / lit-GE layers are all cut
# from one picture (ui/logo_sign_led.png) by tools/broadway/sign_layers.py, so they line up to the pixel
icon = upscale4k.up4(Image.open(os.path.join(RAW, "bonus_icon.png")).convert("RGBA"), long_edge=1600)
contain(icon, (640, 640)).save(os.path.join(A, "bonus_icon.webp"), "WEBP", quality=90, alpha_quality=100, method=6)
for n in ("banner_fs", "banner_xfs", "banner_boost"):
    Image.open(os.path.join(RAW, n + "2.png")).convert("RGB").resize((1440, 810), Image.LANCZOS).save(
        os.path.join(A, "bonus", n + ".webp"), "WEBP", quality=88, method=6)
print("fit: bonus_icon, 3 banners")
