"""The image model sometimes paints a fake transparency checkerboard behind an opaque picture: flood it from the
picture's edges (light, colourless pixels) and paint it flat midnight navy. usage: python tools/broadway/fix_checker.py <png>..."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
NAVY = np.array([22, 29, 58])
for p in sys.argv[1:]:
    im = np.asarray(Image.open(p).convert("RGB")).astype(np.float32)
    mx, mn = im.max(-1), im.min(-1)
    grey = (mx - mn < 18) & (mx > 140)
    lab, _ = ndimage.label(grey)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    bg = ndimage.binary_closing(bg, iterations=2) & ~((mx - mn >= 18) | (mx < 60))   # the squares' seams too
    bg = ndimage.binary_dilation(bg, iterations=1) & (mx > 120) & (mx - mn < 30)
    out = im.copy()
    out[bg] = NAVY
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(p)
    print(p, "background", round(bg.mean(), 3))
