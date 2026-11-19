"""Take the painted spark (a flat yellow star) off the frayed wire at the frame's top-right corner, so the page can
throw real sparks from the wire instead (owner pass 4, 2026-11-18). Idempotent: run it after tools/outage/frame_cable.py.

  assets/frame.webp     the star (its yellow and the black outline that belongs only to it) made transparent; the
                        wires, their copper strands and the frame untouched
  assets/spark.json     where the sparks fly from (frame px): the red wire's copper tip that the star sat on, plus the
                        two other frayed ends for the small crackles in between, and the frame's size
usage: python tools/outage/frame_spark.py"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = os.path.join(ROOT, "frontend", "assets")
FR = os.path.join(A, "frame.webp")
im = np.asarray(Image.open(FR).convert("RGBA")).astype(np.int32)
H, W, _ = im.shape
r, g, b, a = (im[..., i] for i in range(4))
lum = (r + g + b) / 3
sat = im[..., :3].max(-1) - im[..., :3].min(-1)
zone = np.zeros((H, W), bool)
zone[:int(H * .17), int(W * .86):] = True

yellow = zone & (r > 200) & (g > 170) & (b < 130) & (a > 100)
copper = zone & (r > 180) & (g > 90) & (g < 175) & (b < 110) & (a > 100)
redw = zone & (r > 140) & (g < 90) & (b < 90) & (a > 100)
wirefill = zone & (lum > 30) & (lum < 100) & (sat < 30) & (a > 200)
wl, wn = ndimage.label(wirefill)                       # a wire's grey core is big; the star's grey edge is not
wsz = ndimage.sum(wirefill, wl, range(1, wn + 1))
wirefill = np.isin(wl, 1 + np.nonzero(wsz > 1500)[0])
# only copper that is joined to a wire is a wire's strands (the star's own orange edge looks like copper too)
wire = redw | wirefill
clab, cn = ndimage.label(copper)
attached = np.zeros_like(copper)
near_wire = ndimage.binary_dilation(wire, iterations=4)
for k in range(1, cn + 1):
    comp = clab == k
    if (comp & near_wire).any():
        attached |= comp
keep = ndimage.binary_dilation(wire | attached, iterations=6)
# everything round the star that isn't a wire, its copper or the ink right on them
star = zone & (a > 0) & ndimage.binary_dilation(yellow, iterations=22) & ~keep
spark = {"frame": [W, H]}
if yellow.sum() > 200:
    cy, cx = [float(v) for v in ndimage.center_of_mass(yellow)]
    out = im.copy()
    out[star, 3] = 0
    # and any small fragment of its outline left floating, not joined to the wires or the frame
    lab, n = ndimage.label(zone & (out[..., 3] > 0))
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    for k in range(1, n + 1):
        if sizes[k - 1] < 1500 and not (keep & (lab == k)).any():
            out[lab == k, 3] = 0
    Image.fromarray(out.astype(np.uint8), "RGBA").save(FR, "WEBP", quality=92, alpha_quality=100, method=6)
    # the copper tip the star sat on: the copper pixel nearest the star's centre
    cys, cxs = np.nonzero(copper)
    d = np.hypot(cxs - cx, cys - cy)
    i = int(np.argmin(d))
    spark["origin"] = [int(cxs[i]), int(cys[i])]
    spark["star_centre"] = [round(cx), round(cy)]
    # the other frayed ends: the copper clusters furthest from that tip
    lab, n = ndimage.label(ndimage.binary_dilation(copper, iterations=4))
    tips = []
    for k in range(1, n + 1):
        ys, xs = np.nonzero((lab == k) & copper)
        if len(xs) < 60:
            continue
        j = int(np.argmin(ys))                       # each cluster's top-most strand end
        tips.append([int(xs[j]), int(ys[j])])
    tips.sort(key=lambda p: -np.hypot(p[0] - spark["origin"][0], p[1] - spark["origin"][1]))
    spark["others"] = tips[:2]
    # the top bar sparks can land on: its top edge (read at the bar's middle) and its right end (the cord's bar)
    col = np.nonzero(out[:, W // 2, 3] > 40)[0]
    spark["bar_top"] = int(col.min())
    cj = os.path.join(A, "cable.json")
    spark["bar_right"] = json.load(open(cj))["bar_right"] if os.path.exists(cj) else W * .93
    json.dump(spark, open(os.path.join(A, "spark.json"), "w"), indent=1)
    print("star removed:", int(star.sum()), "px; spark", spark)
else:
    print("no painted star left (already removed)", json.load(open(os.path.join(A, "spark.json"))) if os.path.exists(os.path.join(A, "spark.json")) else "")
