"""QA Rosie's rig renders (art/blender/chars/rosie_rig/renders/<clip>/####.png):
  _qa/<clip>_sheet.jpg   every rendered frame, on a mid navy, numbered
  _qa/joints_<clip>.jpg  2x crops of the joints (neck, both shoulders, both elbows, waist, knees, wrists) on the
                         clip's frames that move most - seams, gaps and smears show here
  report                 per clip: the frames that differ most from the one before (pops), and alpha holes inside
                         the figure (a pixel enclosed by ink that went transparent: a gap opened at a seam)
usage: python tools/broadway/qa_rosie.py [clip,..]"""
import glob, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REN = os.path.join(ROOT, "art", "blender", "chars", "rosie_rig", "renders")
QA = os.path.join(REN, "_qa")
BG = (40, 44, 78)
# joints in the QA render's px (760 x 1080 at ortho 16.4, cam z -.2): art px -> render px
SC = 1080 / 1640.0
def rp(x, y):
    return (380 + (x - 512) * SC, 540 + (y - 788) * SC)
JOINTS = {"neck": (405, 470), "shoulder_s": (235, 532), "shoulder_f": (600, 546), "elbow_s": (165, 690),
          "elbow_f": (700, 700), "wrist_f": (795, 598), "wrist_s": (335, 765), "waist": (520, 840),
          "knee_l": (310, 1140), "knee_r": (592, 1120)}


def load(f):
    return np.asarray(Image.open(f).convert("RGBA")).astype(np.float32)


def holes(a):
    solid = a > 200
    filled = ndimage.binary_fill_holes(solid)
    gap = filled & (a < 60)
    lab, n = ndimage.label(gap)
    sizes = ndimage.sum(gap, lab, range(1, n + 1)) if n else []
    return int(sum(s for s in sizes if s >= 6))


def run(clip):
    fs = sorted(glob.glob(os.path.join(REN, clip, "*.png")))
    if not fs:
        return f"{clip}: no renders"
    os.makedirs(QA, exist_ok=True)
    ims = [load(f) for f in fs]
    cols = 8
    cw, ch = 190, 270
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw, rows * ch), BG)
    d = ImageDraw.Draw(sheet)
    for k, (f, im) in enumerate(zip(fs, ims)):
        pic = Image.fromarray(im.astype(np.uint8), "RGBA").resize((cw, ch), Image.LANCZOS)
        bgc = Image.new("RGBA", pic.size, BG + (255,))
        bgc.alpha_composite(pic)
        sheet.paste(bgc.convert("RGB"), ((k % cols) * cw, (k // cols) * ch))
        d.text(((k % cols) * cw + 3, (k // cols) * ch + 2), os.path.basename(f)[:4], fill=(255, 255, 255))
    sheet.save(os.path.join(QA, f"{clip}_sheet.jpg"), quality=84)
    diffs = [float(np.abs(ims[k][..., 3] - ims[k - 1][..., 3]).mean()) for k in range(1, len(ims))]
    order = np.argsort(diffs)[::-1][:4] + 1
    pick = sorted(set(int(k) for k in order))
    tiles = []
    for k in pick:
        im = Image.fromarray(ims[k].astype(np.uint8), "RGBA")
        bgc = Image.new("RGBA", im.size, BG + (255,))
        bgc.alpha_composite(im)
        for nm, (x, y) in JOINTS.items():
            cx, cy = rp(x, y)
            crop = bgc.crop((int(cx - 48), int(cy - 48), int(cx + 48), int(cy + 48))).resize((192, 192), Image.LANCZOS)
            tiles.append((f"{os.path.basename(fs[k])[:4]} {nm}", crop))
    if tiles:
        cols2 = len(JOINTS)
        rows2 = (len(tiles) + cols2 - 1) // cols2
        J = Image.new("RGB", (cols2 * 192, rows2 * 206), BG)
        dj = ImageDraw.Draw(J)
        for k, (lab, t) in enumerate(tiles):
            J.paste(t.convert("RGB"), ((k % cols2) * 192, (k // cols2) * 206 + 14))
            dj.text(((k % cols2) * 192 + 2, (k // cols2) * 206), lab, fill=(255, 255, 255))
        J.save(os.path.join(QA, f"joints_{clip}.jpg"), quality=86)
    hs = [holes(im[..., 3]) for im in ims]
    worst = int(np.argmax(hs))
    return (f"{clip:13s} frames {len(ims):3d}  biggest pops at {[os.path.basename(fs[k])[:4] for k in order]}  "
            f"holes: max {max(hs)} px at {os.path.basename(fs[worst])[:4]}")


if __name__ == "__main__":
    clips = sys.argv[1].split(",") if len(sys.argv) > 1 else sorted(d for d in os.listdir(REN) if not d.startswith("_"))
    for c in clips:
        print(run(c), flush=True)
