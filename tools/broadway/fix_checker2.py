"""Second pass for fix_checker.py: the checker's darker squares left as dots - any light colourless blob that touches
the navy is background too (the art's own white highlights sit inside black outlines, never against the navy)."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
NAVY = np.array([22, 29, 58])
for p in sys.argv[1:]:
    im = np.asarray(Image.open(p).convert("RGB")).astype(np.float32)
    for _ in range(3):
        mx, mn = im.max(-1), im.min(-1)
        navy = (np.abs(im - NAVY).max(-1) < 6)
        grey = (mx - mn < 34) & (mx > 70) & ~navy
        lab, n = ndimage.label(grey)
        touch = np.unique(lab[ndimage.binary_dilation(navy, iterations=2) & grey])
        bg = np.isin(lab, touch[touch > 0])
        im[bg] = NAVY
    Image.fromarray(im.clip(0, 255).astype(np.uint8)).save(p)
    print(p, "navy", round((np.abs(im - NAVY).max(-1) < 6).mean(), 3))
