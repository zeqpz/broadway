"""Flatten a generated card's empty face to one colour (the model sometimes leaves a grey placeholder smudge in it):
flood the low-saturation light region from the face's centre and paint it the face's own clean colour.
usage: python tools/broadway/flatten_face.py <ui name> [cx cy as fractions, default .5 .58]"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
name = sys.argv[1]
cx, cy = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (.5, .58)
p = os.path.join(ROOT, "art", "broadway-src", "ui", name + ".png")
im = np.asarray(Image.open(p).convert("RGBA")).astype(np.float32)
rgb = im[..., :3]
mx, mn = rgb.max(-1), rgb.min(-1)
sat = (mx - mn) / (mx + 1e-6)
light = (mx > 90) & (sat < .22) & (im[..., 3] > 200)
lab, _ = ndimage.label(light)
H, W = light.shape
region = lab == lab[int(H * cy), int(W * cx)]
assert region.any() and region.mean() < .8, "face not found"
face = rgb[region]
lum = face.mean(-1)
clean = np.median(face[lum >= np.percentile(lum, 70)], axis=0)       # the brightest part is the untouched face
inner = ndimage.binary_erosion(region, iterations=3)
out = im.copy()
out[inner, :3] = clean
Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBA").save(p)
print(name, "face", region.sum(), "px ->", clean.round())
