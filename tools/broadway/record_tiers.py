"""The Gold Record (M) in a metal per Multi value tier - the record certifications: copies of its Blender renders and
its flat icon with the gold disc recoloured (its red label, black outline, white glints and the halo stay as drawn).
  M  x1.25-2 bronze   M2 up to x5 silver   M3 up to x20 GOLD (as drawn)   M4 up to x100 platinum (icy)   M5 above x100 diamond (pink-violet)
The game picks the tier from the value (potionId in index.html). The gold renders are kept as art/blender/renders/M_gold
(made from M the first time this runs) - M itself becomes the bronze record.
The recolour maps each gold pixel's brightness onto the metal's ramp (dark / mid / light), weighted by a soft mask on
gold's hue (25-58 deg), saturation and value, smoothed so no lone pixel flips.
usage: python tools/broadway/record_tiers.py   (after symanim.py has rendered M and pack_frames.py packed the rest;
       after re-rendering M, delete art/blender/renders/M_gold so the new gold becomes the source)"""
import glob, json, os, shutil, subprocess, sys
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REN = os.path.join(ROOT, "art", "blender", "renders")
PARTS = os.path.join(ROOT, "art", "blender", "parts")
SYM = os.path.join(ROOT, "frontend", "assets", "sym")
FLAT = os.path.join(ROOT, "frontend", "assets", "flat")
GOLD_FLAT = os.path.join(ROOT, "art", "broadway-src", "flat_M_gold.webp")
RAMPS = {   # tier: (dark, mid, light) at brightness .25 / .6 / .95
    "M": ((74, 30, 10), (156, 78, 34), (226, 142, 88)),
    "M2": ((54, 58, 72), (142, 150, 168), (232, 236, 246)),
    "M3": None,
    "M4": ((30, 72, 128), (110, 176, 232), (214, 240, 255)),
    "M5": ((86, 12, 106), (212, 44, 190), (255, 166, 244)),
}


def ramp(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def recolour(im, stops):
    a = np.asarray(im.convert("RGBA")).astype(np.float32) / 255
    rgb, al = a[..., :3], a[..., 3:]
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn + 1e-6
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.where(mx == r, (g - b) / d % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 0, d / (mx + 1e-6), 0)
    w = ramp(h, 22, 30) * (1 - ramp(h, 56, 64)) * ramp(s, .3, .45) * ramp(mx, .12, .22)
    w = ndimage.gaussian_filter(w, .8)
    L = rgb @ np.float32([.3, .59, .11])
    L = np.clip(L / .9, 0, 1)                              # gold's brightest face reads as the metal's light end
    dk, md, lt = [np.float32(c) / 255 for c in stops]
    t1 = np.clip((L - .25) / .35, 0, 1)[..., None]
    t2 = np.clip((L - .6) / .35, 0, 1)[..., None]
    out = np.where(L[..., None] < .6, dk + (md - dk) * t1, md + (lt - md) * t2)
    rgb2 = rgb * (1 - w[..., None]) + out * w[..., None]
    return Image.fromarray((np.dstack([rgb2, al]) * 255).round().clip(0, 255).astype(np.uint8), "RGBA")


def main():
    src = os.path.join(REN, "M_gold")
    if not os.path.isdir(src):                                # the gold renders become the source, once
        shutil.copytree(os.path.join(REN, "M"), src)          # (after re-rendering M in Blender: delete M_gold first)
        shutil.copyfile(os.path.join(FLAT, "M.webp"), GOLD_FLAT)
    clips = sorted(c for c in os.listdir(src) if os.path.isdir(os.path.join(src, c)))
    for t, stops in RAMPS.items():
        dst = os.path.join(REN, t)
        if t != "M" and os.path.isdir(dst):
            shutil.rmtree(dst)
        if t == "M":
            shutil.rmtree(dst)
        for c in clips:
            os.makedirs(os.path.join(dst, c))
            for f in sorted(glob.glob(os.path.join(src, c, "*.png"))):
                im = Image.open(f)
                (recolour(im, stops) if stops else im).save(os.path.join(dst, c, os.path.basename(f)))
        if t != "M":                                          # pack_frames reads the icon's size from here
            os.makedirs(os.path.join(PARTS, t), exist_ok=True)
            shutil.copyfile(os.path.join(PARTS, "M", "parts.json"), os.path.join(PARTS, t, "parts.json"))
        print("rendered", t, flush=True)
    man = json.load(open(os.path.join(SYM, "manifest.json")))
    dens = ",".join(str(x) for x in man["densities"])
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "blender", "pack_frames.py"), ",".join(RAMPS), dens], check=True)
    flat = Image.open(GOLD_FLAT)
    for t, stops in RAMPS.items():
        (recolour(flat, stops) if stops else flat).save(os.path.join(FLAT, t + ".webp"), "WEBP", quality=92,
                                                        alpha_quality=100, method=6)
    print("flat", len(RAMPS))


if __name__ == "__main__":
    main()
