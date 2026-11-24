"""Broadway on Nashville: the honky-tonk bar behind the board (tools/broadway/gen_bg_bar.py), cut into the layers
frontend/bgscene.js keeps alive.

From two drawings of the same room - every light on (art/broadway-src/bg_v1.png) and the same picture with every light
switched off (bg_unlit_v1.png, an image-model edit that kept everything else in place) - the difference is exactly the
light. The lit room is the painting (assets/bonus_wall.webp, 3840 x 2160). Cut from the pair:
  off_<k>.webp    one "off" patch per neon sign (the unlit pixels of the sign and its near glow, feathered): the page
                  shows it for a moment to make that sign flicker or die
  bulbs_<g>.webp  the string of party bulbs under the ceiling, in three chase groups
  foot_<g>.webp   the stage's footlights, in three chase groups
  juke.webp       the jukebox's lit tubes, cut out LIT, so the page can run them through the colours
and written with them (assets/bg/scene.json "props", fractions of the picture): where the pieces the page draws live
go - the ceiling fans, the two stage lights and their beams, the dust in them, the glints on the bottles, the steam
off the coffee pot (PROPS below, read off grids of the painting) and the gold records (found by their colour).
  Xtreme: assets/bonus_wall_xtreme.webp (the rooftop, 4K) - its fireworks are drawn live by bgscene.js.
  Phones: assets/mobile/bg_portrait(_xtreme).webp and bg_landscape(_xtreme).webp (plates only, no layers).
usage: python tools/broadway/bg_layers_bw.py"""
import json, os, sys, time
import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import upscale4k

ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "art", "broadway-src")
A = os.path.join(ROOT, "frontend", "assets")
BG = os.path.join(A, "bg")
W4, H4 = 3840, 2160
# ---- the painting's px (1536 x 864), read off grids of art/broadway-src/bg4/bar_pick.png
SIGNS = {                                 # each neon sign's box (x0, y0, x1, y1), with a little room round it
    "live_music": (80, 120, 384, 212),
    "guitar": (434, 160, 534, 436),
    "honky_tonk": (636, 92, 892, 180),
    "boot": (1426, 86, 1536, 292),
    "bar": (1426, 294, 1536, 372),
}
GLOW = 20                                 # px of near glow kept round a sign's tubes
BULB_BAND = (66, 118, 0, 1536)            # rows y0..y1, columns x0..x1 the string of party bulbs hangs in
FOOT_BAND = (636, 676, 0, 430)            # and the stage's footlights
JUKE = (1426, 380, 1536, 626)             # the jukebox: light inside this box is its own (colour-cycled)
PROPS = {
    "fans": [[232, 46, 124], [1296, 46, 124]],            # ceiling fans: hub x, y and blade radius
    "beams": [[77, 110, -24, "#FF4FB0"], [370, 110, 22, "#4FB4FF"]],   # stage lights: lens x, y, lean (deg; + swings the far end left), colour
    "beam_len": 520,                                       # how far a beam reaches (px)
    "cone": [70, 190, 310, 390],                           # where the beams cross over the stage (dust drifts there)
    "glints": [1162, 286, 222, 124],                       # the two shelves of bottles
    "glint_rows": [0.1, 0.66],                             # the bottles' shoulders, as shares of that box's height
    "steam": [1280, 424],                                  # the kettle's lid
}


def up(name, size):
    p4 = os.path.join(SRC, "4k", name + ".png")
    if not os.path.exists(p4):
        im = Image.open(os.path.join(SRC, name + ".png")).convert("RGBA")
        upscale4k.up4(im, size, model="realesrgan-x4plus-anime").convert("RGB").save(p4)
    return Image.open(p4).convert("RGB")


def save(im, path, **kw):
    """Windows now and then refuses a write in the repo for a moment: try a few times."""
    for _ in range(5):
        try:
            im.save(path, "WEBP", **kw)
            return
        except OSError:
            time.sleep(.6)
    im.save(path, "WEBP", **kw)


def main():
    os.makedirs(BG, exist_ok=True)
    for old in os.listdir(BG):
        os.remove(os.path.join(BG, old))
    os.makedirs(os.path.join(SRC, "4k"), exist_ok=True)
    lit4 = up("bg_v1", (W4, H4))
    off4 = up("bg_unlit_v1", (W4, H4))
    save(lit4, os.path.join(A, "bonus_wall.webp"), quality=90, method=6)
    # the light: where the two drawings differ (measured at 1536 px, after checking the unlit one has not moved)
    a = np.asarray(Image.open(os.path.join(SRC, "bg_v1.png")).convert("RGB")).astype(np.float32)
    b = np.asarray(Image.open(os.path.join(SRC, "bg_unlit_v1.png")).convert("RGB").resize((a.shape[1], a.shape[0]))).astype(np.float32)
    H, W = a.shape[:2]
    ea = cv2.Canny(a.mean(-1).astype(np.uint8), 40, 120).astype(np.float32)   # (their lighting differs: line art is compared)
    eb = cv2.Canny(b.mean(-1).astype(np.uint8), 40, 120).astype(np.float32)
    warp = np.eye(2, 3, dtype=np.float32)
    try:
        _, warp = cv2.findTransformECC(cv2.GaussianBlur(ea, (0, 0), 2), cv2.GaussianBlur(eb, (0, 0), 2), warp, cv2.MOTION_TRANSLATION,
                                       (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 1e-5), None, 5)
    except cv2.error:
        pass
    print("unlit drawing offset", np.round(warp[:, 2], 2))
    if abs(warp[0, 2]) > 6 or abs(warp[1, 2]) > 6:
        raise SystemExit("the unlit drawing moved: redraw it")
    diff = np.abs(a - b).max(-1)
    strong = diff > 90
    off_np = np.asarray(off4).astype(np.uint8)
    lit_np = np.asarray(lit4).astype(np.uint8)
    fx, fy = lambda v: round(v / W, 5), lambda v: round(v / H, 5)
    scene = {"size": [W4, H4], "signs": [], "bulbs": [], "foot": [], "sky": None, "props": {
        "fans": [[fx(x), fy(y), fx(r)] for x, y, r in PROPS["fans"]],
        "beams": [[fx(x), fy(y), deg, col] for x, y, deg, col in PROPS["beams"]],
        "beam_len": fy(PROPS["beam_len"]),
        "cone": [fx(PROPS["cone"][0]), fy(PROPS["cone"][1]), fx(PROPS["cone"][2]), fy(PROPS["cone"][3])],
        "glints": [fx(PROPS["glints"][0]), fy(PROPS["glints"][1]), fx(PROPS["glints"][2]), fy(PROPS["glints"][3])],
        "glint_rows": PROPS["glint_rows"],
        "steam": [fx(PROPS["steam"][0]), fy(PROPS["steam"][1])],
        "records": [],
    }}

    def patch(mask, name, half=False, src=None, blur=2.2):
        m4 = cv2.resize(mask.astype(np.uint8) * 255, (W4, H4), interpolation=cv2.INTER_LINEAR).astype(np.float32)
        m4 = cv2.GaussianBlur(m4, (0, 0), blur)
        ys, xs = np.nonzero(m4 > 8)
        x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        rgba = np.dstack([(off_np if src is None else src)[y0:y1, x0:x1], m4[y0:y1, x0:x1].clip(0, 255).astype(np.uint8)])
        im = Image.fromarray(rgba, "RGBA")
        if half:                                        # small lights: half the pixels, drawn twice the size (a quarter of the memory)
            im = im.resize((max(1, im.width // 2), max(1, im.height // 2)), Image.LANCZOS)
        save(im, os.path.join(BG, name), quality=88, alpha_quality=90, method=6)
        return [round(x0 / W4, 5), round(y0 / H4, 5), round((x1 - x0) / W4, 5), round((y1 - y0) / H4, 5)]

    # ---- the round lights in a row (party bulbs, footlights): each a bright core with its halo, in three chase groups
    def row_of_lights(band, key, stem):
        y0, y1, x0, x1 = band
        win = np.zeros((H, W), bool)
        win[y0:y1, x0:x1] = True
        lab, n = ndimage.label((diff > 110) & win)
        found = []
        for i in range(1, n + 1):
            ys, xs = np.nonzero(lab == i)
            w_, h_ = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
            if not (60 <= len(xs) <= 700 and w_ < 56 and h_ >= 12):      # (a sign's edge is wide or thin)
                continue
            if any(abs(xs.mean() - bx) < 36 and abs(ys.mean() - by) < 32 for bx, by, _, _ in PROPS["beams"]):
                continue                                                 # a stage light's lens: it stays lit
            halo = ndimage.binary_dilation(lab == i, iterations=10) & (diff > 34) & win
            found.append((xs.mean(), halo))
        found.sort(key=lambda t: t[0])
        for g in range(3):
            m = np.zeros((H, W), bool)
            for j, (_, hm) in enumerate(found):
                if j % 3 == g:
                    m |= hm
            if m.any():
                scene[key].append({"src": f"bg/{stem}_{g}.webp", "box": patch(m, f"{stem}_{g}.webp", half=True, blur=5)})
        return len(found)

    n_bulbs = row_of_lights(BULB_BAND, "bulbs", "bulbs")
    n_foot = row_of_lights(FOOT_BAND, "foot", "foot")
    # ---- the neon signs, each in its own box: its tubes (the strong difference) and the glow near them
    for k, (name, (x0, y0, x1, y1)) in enumerate(SIGNS.items()):
        box = np.zeros((H, W), bool)
        box[y0:y1, x0:x1] = True
        tubes = strong & box
        if tubes.sum() < 300:
            print("  no light found for", name)
            continue
        m = ndimage.binary_dilation(tubes, iterations=GLOW) & box
        m = ndimage.binary_fill_holes(m)
        scene["signs"].append({"name": name, "src": f"bg/off_{k}.webp", "box": patch(m, f"off_{k}.webp", blur=14),
                               "area": int(tubes.sum()), "cx": round((x0 + x1) / 2 / W, 3)})
    # ---- the jukebox's lit tubes, as painted: the page turns their hue
    jb = np.zeros((H, W), bool)
    jb[JUKE[1]:JUKE[3], JUKE[0]:JUKE[2]] = True
    juke = ndimage.binary_closing((diff > 60) & jb, iterations=2)
    if juke.sum() > 300:
        scene["juke"] = {"src": "bg/juke.webp", "box": patch(ndimage.binary_dilation(juke, iterations=2), "juke.webp", src=lit_np, blur=4)}
    # ---- the framed gold records, found by their colour: a shine sweeps each disc now and then
    gold = (a[..., 0] > 170) & (a[..., 1] > 100) & (a[..., 1] < 215) & (a[..., 2] < 120) & (a[..., 0] - a[..., 2] > 90)
    gold[:200] = False                                # (not the amber neon sign over them)
    gold[340:] = False
    gold[:, :540] = False
    gold[:, 1010:] = False
    gl, gn = ndimage.label(ndimage.binary_closing(gold, iterations=3))
    for i in range(1, gn + 1):
        disc = ndimage.binary_fill_holes(gl == i)
        ys, xs = np.nonzero(disc)
        w_, h_ = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        round_ = len(xs) / (3.14159 * (w_ / 2) * (h_ / 2))           # a disc fills its ellipse (a hat or a guitar does not)
        if len(xs) > 2500 and .88 < w_ / h_ < 1.14 and round_ > .9:
            scene["props"]["records"].append([fx((xs.min() + xs.max()) / 2), fy((ys.min() + ys.max()) / 2), fx((w_ + h_) / 4)])
    scene["props"]["records"].sort()
    json.dump(scene, open(os.path.join(BG, "scene.json"), "w"), indent=1)
    print(f"signs {len(scene['signs'])} of {len(SIGNS)}  bulbs {n_bulbs}  footlights {n_foot}  records {len(scene['props']['records'])}  "
          f"jukebox {'yes' if 'juke' in scene else 'no'}")
    # ---- Xtreme rooftop + phone plates
    save(up("bg_xtreme_v1", (W4, H4)), os.path.join(A, "bonus_wall_xtreme.webp"), quality=90, method=6)
    os.makedirs(os.path.join(A, "mobile"), exist_ok=True)
    for name, out in (("bg_mobile_v1", "bg_portrait.webp"), ("bg_xtreme_mobile_v1", "bg_portrait_xtreme.webp")):
        im = Image.open(os.path.join(SRC, name + ".png")).convert("RGB")      # 1024 x 1536, as Power Outage's (phone memory)
        save(im.resize((1024, 1536), Image.LANCZOS), os.path.join(A, "mobile", out), quality=88, method=6)
    save(lit4.resize((1920, 1080), Image.LANCZOS), os.path.join(A, "mobile", "bg_landscape.webp"), quality=86, method=6)
    save(Image.open(os.path.join(SRC, "4k", "bg_xtreme_v1.png")).convert("RGB").resize((1920, 1080), Image.LANCZOS),
         os.path.join(A, "mobile", "bg_landscape_xtreme.webp"), quality=86, method=6)
    print("plates written")


if __name__ == "__main__":
    main()
