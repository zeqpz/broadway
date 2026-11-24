"""The neon title sign's layers (index.html #logosign), cut from two drawings of the same sign: every tube lit
(art/broadway-src/ui/logo_sign.png) and every tube off (logo_sign_unlit.png, an image-model edit that kept the rest).
The word ON has a loose contact (the page stutters it; --ge = how lit it is):
  assets/logo_sign.webp          the sign with ON dark (its unlit tubes), everything else lit
  assets/logo_sign_ge.webp       ON lit, alone on a clear canvas (laid over the sign)
  assets/logo_sign_glow.webp     the light the lit tubes and bulbs throw (their colours, blurred; screen-blended)
  assets/logo_sign_ge_glow.webp  ON's own light
All 1200 x 900 (the sign's box). ON is found as the difference between the drawings inside ON_BOX.
usage: python tools/broadway/sign_layers_bw.py"""
import os, sys
import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import upscale4k

ROOT = os.path.dirname(os.path.dirname(HERE))
UI = os.path.join(ROOT, "art", "broadway-src", "ui")
A = os.path.join(ROOT, "frontend", "assets")
SIZE = (1200, 900)
ON_BOX = (130, 820, 400, 1035)          # px on the 1536 x 1152 drawing: the word ON


def main():
    lit = Image.open(os.path.join(UI, "logo_sign.png")).convert("RGBA")
    off = Image.open(os.path.join(UI, "logo_sign_unlit.png")).convert("RGBA").resize(lit.size)
    a, b = np.asarray(lit).astype(np.float32), np.asarray(off).astype(np.float32)
    # lay the unlit drawing back on the lit one (it may sit a px or two off)
    warp = np.eye(2, 3, dtype=np.float32)
    try:
        _, warp = cv2.findTransformECC(a[..., :3].mean(-1), b[..., :3].mean(-1), warp, cv2.MOTION_EUCLIDEAN,
                                       (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 1e-5), None, 5)
        b = cv2.warpAffine(b, warp, (b.shape[1], b.shape[0]), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
    except cv2.error:
        pass
    print("unlit offset", np.round(warp[:, 2], 2))
    light = (np.abs(a[..., :3] - b[..., :3]).max(-1) > 40) & (a[..., 3] > 128)
    light = ndimage.binary_closing(ndimage.binary_opening(light, iterations=1), iterations=2)
    on = np.zeros_like(light)
    x0, y0, x1, y1 = ON_BOX
    on[y0:y1, x0:x1] = light[y0:y1, x0:x1]
    on = ndimage.binary_dilation(on, iterations=3) & (a[..., 3] > 20)
    soft = cv2.GaussianBlur(on.astype(np.float32), (0, 0), 1.0)[..., None]
    base = a * (1 - soft) + b * soft
    base[..., 3] = a[..., 3]
    ge = a.copy()
    ge[..., 3] = a[..., 3] * soft[..., 0]

    def glow(mask):
        g = np.zeros_like(a)
        g[..., :3] = a[..., :3] * mask[..., None]
        k = max(6, round(lit.width / 90))
        g[..., :3] = cv2.GaussianBlur(g[..., :3], (0, 0), k) * 1.6
        lum = g[..., :3].max(-1)
        g[..., 3] = np.clip(lum * 1.1, 0, 255)
        g[..., :3] = np.where(lum[..., None] > 1, g[..., :3] * 255 / np.maximum(lum[..., None], 1), 0)
        return g

    out = {"logo_sign": base, "logo_sign_ge": ge, "logo_sign_glow": glow(light.astype(np.float32)),
           "logo_sign_ge_glow": glow(on.astype(np.float32))}
    for name, im in out.items():
        pic = Image.fromarray(im.clip(0, 255).astype(np.uint8), "RGBA")
        if name in ("logo_sign", "logo_sign_ge"):
            pic = upscale4k.up4(pic, long_edge=max(SIZE) * 2)
        pic = pic.convert("RGBa").resize(SIZE, Image.LANCZOS).convert("RGBA")
        pic.save(os.path.join(A, name + ".webp"), "WEBP", quality=90, alpha_quality=100, method=6)
        print("wrote", name, pic.size)
    print("ON pixels", int(on.sum()), " lit pixels", int(light.sum()))


if __name__ == "__main__":
    main()
