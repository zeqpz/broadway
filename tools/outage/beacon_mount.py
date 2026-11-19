"""The Xtreme room's alarm beacon, fixed to the wall (owner pass 5, 2026-11-19: "the alarm drawing should look connected
to the wall, not floating").

The red room's painting (art/outage-src/bg_xtreme_v1.png and its phone redraw) has the beacon hovering in front of the
cornice. This draws its mounting into the painting, in the painting's own flat style (maroon steel, black outline, one
lighter rim): a shelf bracket under the lamp's base - the shelf, a wall plate with two bolts, two struts - and a conduit
pipe from its cap up to the ceiling. Then the game's files are written from the result:
  frontend/assets/bonus_wall_xtreme.webp (3840x2160), mobile/bg_landscape_xtreme.webp, mobile/bg_portrait_xtreme.webp
The untouched paintings are kept as *_orig.png and always read from, so this can be run again.
The beacon's light (frontend/bgscene.js) turns about the lamp's glass: LAMP below, written to assets/bg/scene.json by
tools/outage/bg_layers.py.
usage: python tools/outage/beacon_mount.py"""
import os, shutil, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "art", "outage-src")
A = os.path.join(ROOT, "frontend", "assets")
SS = 6
INK = (14, 4, 8, 255)
# name: (lamp centre x, its base's bottom y, the base's half width, the cap's top y, scale) - read off each painting
LAMPS = {"bg_xtreme_v1": (977, 79, 24, 12, 1.0), "bg_xtreme_mobile_v1": (291, 86, 30, 14, 1.2)}
LAMP = (977, 43)            # the desktop lamp's glass centre (px of 1536 x 864): the beacon light's pivot


def mount(im, cx, by, hw, cap, k):
    """Draw the bracket and the conduit round the lamp at (cx, base bottom by)."""
    # maroon steel under the red light: a mid tone, its shade and a lit rim (the lamp's own base is nearly black)
    fill, dark, lite = (128, 26, 34, 255), (78, 14, 22, 255), (214, 74, 70, 255)
    pad = int(60 * k)
    x0, y0, x1, y1 = cx - hw - pad, 0, cx + hw + pad, by + int(48 * k)
    W, H = (x1 - x0) * SS, (y1 - y0) * SS
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    X = lambda x: (x - x0) * SS
    Y = lambda y: (y - y0) * SS
    ow = max(2, round(2.2 * k * SS))                                      # the painting's outline weight
    # the conduit: a pipe from the cap up to the ceiling, with a collar where it meets the cap
    pw = 4.2 * k
    d.rectangle([X(cx - pw), Y(-2), X(cx + pw), Y(cap + 2)], fill=INK)
    d.rectangle([X(cx - pw) + ow, Y(-2), X(cx + pw) - ow, Y(cap + 2)], fill=dark)
    d.rectangle([X(cx - pw) + ow, Y(-2), X(cx - pw * .2), Y(cap + 2)], fill=fill)
    d.rounded_rectangle([X(cx - pw * 1.9), Y(cap - 3.5 * k), X(cx + pw * 1.9), Y(cap + 2.5 * k)], radius=2 * SS, fill=INK)
    d.rounded_rectangle([X(cx - pw * 1.9) + ow, Y(cap - 3.5 * k) + ow, X(cx + pw * 1.9) - ow, Y(cap + 2.5 * k) - ow], radius=SS, fill=fill)
    # the wall plate under the shelf, bolted to the wall
    pl = [cx - 13 * k, by - 2 * k, cx + 13 * k, by + 31 * k]
    d.rounded_rectangle([X(pl[0]), Y(pl[1]), X(pl[2]), Y(pl[3])], radius=4 * SS, fill=INK)
    d.rounded_rectangle([X(pl[0]) + ow, Y(pl[1]) + ow, X(pl[2]) - ow, Y(pl[3]) - ow], radius=3 * SS, fill=dark)
    d.rounded_rectangle([X(pl[0]) + ow, Y(pl[1]) + ow, X(cx - 3 * k), Y(pl[3]) - ow], radius=3 * SS, fill=fill)
    for byy in (by + 12 * k, by + 24 * k):                                # its bolts
        r = 2.6 * k
        d.ellipse([X(cx - r) - ow * .6, Y(byy - r) - ow * .6, X(cx + r) + ow * .6, Y(byy + r) + ow * .6], fill=INK)
        d.ellipse([X(cx - r), Y(byy - r), X(cx + r), Y(byy + r)], fill=lite)
    # the struts: from the shelf's ends down to the plate
    for sgn in (-1, 1):
        a = [(cx + sgn * (hw + 3 * k), by + 6 * k), (cx + sgn * (hw - 6 * k), by + 6 * k), (cx + sgn * 11 * k, by + 27 * k), (cx + sgn * 15 * k, by + 22 * k)]
        d.polygon([(X(x), Y(y)) for x, y in a], fill=INK)
        d.line([(X(x), Y(y)) for x, y in a] + [(X(a[0][0]), Y(a[0][1]))], fill=INK, width=ow * 2, joint="curve")
        inner = [(cx + sgn * (hw + 1.4 * k), by + 7 * k), (cx + sgn * (hw - 4.6 * k), by + 7 * k), (cx + sgn * 12 * k, by + 24.6 * k), (cx + sgn * 14 * k, by + 22 * k)]
        d.polygon([(X(x), Y(y)) for x, y in inner], fill=dark if sgn > 0 else fill)
    # the shelf the lamp stands on
    sh = [cx - hw - 6 * k, by - 1 * k, cx + hw + 6 * k, by + 8 * k]
    d.rounded_rectangle([X(sh[0]), Y(sh[1]), X(sh[2]), Y(sh[3])], radius=3 * SS, fill=INK)
    d.rounded_rectangle([X(sh[0]) + ow, Y(sh[1]) + ow, X(sh[2]) - ow, Y(sh[3]) - ow], radius=2 * SS, fill=fill)
    d.rounded_rectangle([X(sh[0]) + ow, Y(sh[1]) + ow, X(sh[2]) - ow, Y(sh[1]) + ow + 1.6 * k * SS], radius=SS, fill=lite)
    small = ov.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    # the lamp itself stays in front of the pipe's collar and the shelf's back edge: put the painting's own lamp back
    out = im.convert("RGBA")
    lamp = out.crop((cx - hw - 3, cap, cx + hw + 3, by - 1))
    out.alpha_composite(small, (x0, y0))
    out.alpha_composite(lamp, (cx - hw - 3, cap))
    return out.convert("RGB")


def main():
    sys.path.insert(0, HERE)
    import upscale4k
    made = {}
    for name, (cx, by, hw, cap, k) in LAMPS.items():
        orig = os.path.join(SRC, name + "_orig.png")
        if not os.path.exists(orig):
            shutil.copyfile(os.path.join(SRC, name + ".png"), orig)
        made[name] = mount(Image.open(orig), cx, by, hw, cap, k)
        made[name].save(os.path.join(SRC, name + ".png"))
        c = made[name].crop((cx - 110, 0, cx + 110, by + 70))
        c.resize((c.width * 3, c.height * 3), Image.LANCZOS).save(os.path.join(SRC, "_" + name + "_mount.png"))
    if "--no-export" in sys.argv:
        return
    up = upscale4k.up4(made["bg_xtreme_v1"].convert("RGBA"), (3840, 2160), model="realesrgan-x4plus-anime").convert("RGB")
    up.save(os.path.join(A, "bonus_wall_xtreme.webp"), "WEBP", quality=90, method=6)
    up.resize((1920, 1080), Image.LANCZOS).save(os.path.join(A, "mobile", "bg_landscape_xtreme.webp"), "WEBP", quality=86, method=6)
    made["bg_xtreme_mobile_v1"].resize((1024, 1536), Image.LANCZOS).save(os.path.join(A, "mobile", "bg_portrait_xtreme.webp"), "WEBP", quality=86, method=6)
    print("mounted; exported the red room (desktop 4K, phone landscape and portrait)")


if __name__ == "__main__":
    main()
