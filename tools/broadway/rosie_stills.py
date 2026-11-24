"""Rosie for phones: a phone shows no character canvas (iOS memory - charrig.js is desktop only), so it gets a few still
poses from her rig's renders instead, swapped on her reactions (index.html, html.mob #rosiephone):
  assets/mobile/rosie_idle.webp, rosie_cheer.webp, rosie_solo.webp, rosie_wow.webp   (her top 68% - hat to mid-thigh -
  500 px tall: the crop's edge sits behind the frame's top bar, so nothing of her reaches into the reels (review))
usage: python tools/broadway/rosie_stills.py   (after rosie_rig.py rendered its clips)"""
import os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REN = os.path.join(ROOT, "art", "blender", "chars", "rosie_rig", "renders")
OUT = os.path.join(ROOT, "frontend", "assets", "mobile")
PICK = {"idle": ("idle", 0), "cheer": ("big_win", 51), "solo": ("solo", 60), "wow": ("anticipation", 27)}
frames = {k: Image.open(os.path.join(REN, c, f"{f:04d}.png")).convert("RGBA") for k, (c, f) in PICK.items()}
box = None                                           # one box for all of them, so a swap never jumps
for im in frames.values():
    b = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
box = (box[0], box[1], box[2], box[1] + int((box[3] - box[1]) * .68))
for k, im in frames.items():
    c = im.crop(box)
    h = 500
    c = c.convert("RGBa").resize((round(c.width * h / c.height), h), Image.LANCZOS).convert("RGBA")
    c.save(os.path.join(OUT, f"rosie_{k}.webp"), "WEBP", quality=88, alpha_quality=90, method=6)
    print(k, c.size)
print("box", box)
