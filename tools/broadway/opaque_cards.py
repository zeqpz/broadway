"""The image model draws some 'solid' cards slightly see-through (alpha 210-250 where it left a smudge), so the room
shows through as grey wisps. Make each card's interior fully opaque: the silhouette (alpha > 128) with its holes
filled, shrunk a few px so the anti-aliased rim keeps its softness. Not for the frame (its opening must stay clear).
usage: python tools/broadway/opaque_cards.py <png>..."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
for p in sys.argv[1:]:
    im = Image.open(p).convert("RGBA")
    a = np.asarray(im).copy()
    solid = ndimage.binary_fill_holes(a[..., 3] > 128)
    inner = ndimage.binary_erosion(solid, iterations=max(2, im.width // 400))
    before = int((a[..., 3][inner] < 255).sum())
    a[..., 3][inner] = 255
    Image.fromarray(a, "RGBA").save(p)
    print(p.split("/")[-1], "opaque px fixed", before)
