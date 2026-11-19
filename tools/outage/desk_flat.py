"""The desk's fronts, painted flat (owner, 2026-11-19: "there's still a black box around the bonus button").

Nothing on the button draws that box. The room's desk is painted with recessed panels - a dark rectangle inside a
lighter frame - and at laptop-sized windows the bonus emblem sits right in front of one: the panel reads as a box
round the emblem. So the panels come out of the paintings: each face of the desk (between its top moulding, its
corner posts and its plinth, all kept) is filled with one flat board - a plane of colour fitted to the face's own
boards, so the candle's light across it stays.
Done on the two desktop rooms (the same desk, the same place in both); the phone's upright paintings have the desk
behind the board and the emblem far below it, and its landscape ones are made from the desktop rooms.
The untouched paintings are kept as *_panels.png and always read from, so this can be run again.
  bg_v1.png              -> then: upscale4k.py bg (bonus_wall.webp), make_mobile_art.py
  bg_xtreme_v1_orig.png  -> then: beacon_mount.py (mounts the lamp and exports the red room)
usage: python tools/outage/desk_flat.py [--preview]"""
import os, shutil, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(os.path.dirname(HERE)), "art", "outage-src")
# the desk's faces (px of the 1536 x 864 paintings), each just inside its own outline: left front, the middle
# pedestal's face, the right pedestal's face, the far end
FACES = [
    [(14, 549), (179, 549), (179, 678), (14, 678)],
    [(224, 553), (280, 547), (280, 664), (224, 679)],
    [(313, 549), (384, 539), (384, 636), (313, 657)],
    [(401, 518), (454, 510), (454, 601), (401, 618)],
]
PAINTINGS = ["bg_v1", "bg_xtreme_v1_orig"]
LUM = np.array([.299, .587, .114], np.float32)


def flatten(im):
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    out = a.copy()
    for poly in FACES:
        m = Image.new("L", (W * 4, H * 4), 0)
        ImageDraw.Draw(m).polygon([(x * 4, y * 4) for x, y in poly], fill=255)
        m = np.asarray(m.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(.7))).astype(np.float32) / 255
        inside = m > .98
        lum = a[inside] @ LUM
        lo, hi = np.percentile(lum, [45, 97])               # the boards: not the outlines, not the dark insets
        pick = inside & ((a @ LUM) >= lo) & ((a @ LUM) <= hi)
        A = np.stack([np.ones(pick.sum(), np.float32), xx[pick], yy[pick]], 1)
        coef, *_ = np.linalg.lstsq(A, a[pick], rcond=None)   # a plane of colour: c = c0 + cx x + cy y
        plane = coef[0] + xx[..., None] * coef[1] + yy[..., None] * coef[2]
        out = out * (1 - m[..., None]) + plane * m[..., None]
    return Image.fromarray(np.clip(out + .5, 0, 255).astype(np.uint8), "RGB")


def main():
    for name in PAINTINGS:
        keep = os.path.join(SRC, name.replace("_orig", "") + "_panels.png")
        if not os.path.exists(keep):
            shutil.copyfile(os.path.join(SRC, name + ".png"), keep)
        flat = flatten(Image.open(keep))
        flat.save(os.path.join(SRC, name + ".png"))
        if "--preview" in sys.argv:
            c = flat.crop((0, 480, 480, 740))
            x = np.asarray(c).astype(np.float32) / 255
            Image.fromarray((np.clip(x ** .5 * 1.5, 0, 1) * 255).astype(np.uint8)).resize((c.width * 3, c.height * 3), Image.LANCZOS).save(
                os.path.join(SRC, "_" + name + "_desk.png"))
        print("flat desk:", name)


if __name__ == "__main__":
    main()
