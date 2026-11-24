"""Rosie, the cowgirl beside the board, cut into the pieces of her live rig - each piece redrawn on its own full canvas
by the image model from the chosen figure (art/broadway-src/rosie/rosie_v1.png), so what one piece hides of another
(the shirt behind the guitar, her hair under the hat, the thighs under the skirt, the strings under her hand) is real
drawing, not a smear. Same method as Voodoo's Doc v2 (tools/broadway/doc_regen.py), but the figure is the layout: the
canvas is the figure's own 1024 x 1536, and the model is asked to keep the piece where it is.

  gen  [part,..]   art/broadway-src/rosie/parts_raw/<part>.png, one call each (OpenRouter; the key is never printed)
  faces [name,..]  the reaction faces: the redrawn head with only its expression changed
  fit  [part,..]   each raw piece laid back over the figure (SIFT similarity, RANSAC; box fallback), enlarged x4
                   (Real-ESRGAN, tools/broadway/upscale4k.py's binary) and brought to the plate scale (PLATE x the art)
                   -> art/broadway-src/rosie_parts/<part>.png + face_<name>.png + parts.json
  sheet            art/broadway-src/rosie/_parts_sheet.jpg: the figure against the re-assembled pieces
usage: python tools/broadway/rosie_parts.py gen|faces|fit|sheet [names]"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import orimg

ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "art", "broadway-src")
FIG = os.path.join(SRC, "rosie", "rosie_v1.png")
RAW = os.path.join(SRC, "rosie", "parts_raw")
OUT = os.path.join(SRC, "rosie_parts")
MODEL = "openai/gpt-image-2.6-sunburst"
ART = (1024, 1536)
PLATE = 2.0                                        # plate px per art px (the game's densest atlas is 1.5)

HEADER = ("Image 1 is a cartoon character drawn for a slot game. She will be animated as a cut-out puppet, so she is "
          "being separated into pieces. EDIT image 1: keep ONLY the piece described below, exactly where it is on the "
          "canvas, at exactly the same size, angle and shape, with the same linework and colours; erase everything "
          "else to a fully transparent background. Where other pieces covered parts of this piece, draw the hidden "
          "parts in fully, as clean finished drawing in the same style. ")
STYLE = (" Crisp clean flat cartoon linework with the same thick black outlines, flat colours with one hard-edged "
         "shade, no blur, no smudges, no gradients, no painterly texture. Transparent background. Draw ONLY this one "
         "piece: no other body parts, no other characters, no text, no ground, no shadow, no border.")
BOOT = ("Redesign the boot (both boots match): a red leather cowboy boot with white swirl stitching, a white star on a "
        "round royal-blue medallion on the shaft, a row of white studs along the scalloped top edge, a pointed toe and "
        "a brown stacked heel - no diagonal stripe, no flag pattern.")
PARTS = {   # back to front is ORDER
    "hair_back": "The piece: the BACK MASS of her big glossy auburn curls ONLY - the voluminous hair that hangs behind "
                 "her head and falls down behind her shoulders on both sides. Draw it complete as one big shape, "
                 "including everything hidden behind her face, neck, hat and shoulders (fill the middle with hair "
                 "where her head was). No face, no hat, no shirt, no guitar.",
    "leg_l": "The piece: her LEG ON THE VIEWER'S LEFT ONLY, from the top of the thigh down to the sole of the boot. "
             "The skirt and guitar covered the top of the thigh: draw the whole bare thigh right up to a flat top edge "
             "at the hip, well above the skirt's hem line. " + BOOT,
    "leg_r": "The piece: her LEG ON THE VIEWER'S RIGHT ONLY, from the top of the thigh down to the sole of the boot. "
             "The skirt covered the top of the thigh: draw the whole bare thigh right up to a flat top edge at the hip, "
             "well above the skirt's hem line. " + BOOT,
    "fret_arm": "The piece: her ARM ON THE VIEWER'S RIGHT ONLY, from the shoulder to the WRIST, WITHOUT the hand: the "
                "rolled-up royal-blue sleeve with its white fringe and pearl snap, and the bare forearm, bent at the "
                "elbow exactly as posed. The guitar neck crossed in front of the sleeve: draw the sleeve complete. The "
                "sleeve was cut off at the shoulder: finish its top as a smooth rounded shoulder cap of blue shirt. "
                "End the arm at the wrist with a clean rounded end. No hand, no guitar, no strap.",
    "torso": "The piece: her TORSO ONLY - the fitted royal-blue western shirt with white piping, the white fringe across "
             "the chest yoke, little white stars and pearl snaps, from the open collar (an empty neck opening, no neck) "
             "down to the brown tooled-leather belt with its silver star buckle, and the guitar's brown tooled-leather "
             "strap running diagonally across her chest up over her shoulder. NO head, NO neck, NO arms, NO guitar, NO "
             "skirt. Draw the shirt and belt that the guitar and her arms covered. Each shoulder ends in a smooth "
             "rounded cap of blue shirt cloth where the sleeve was taken off.",
    "skirt": "The piece: her SHORT FLARED RED SKIRT ONLY, pleated, with its white trim at the hem, from the waist (just "
             "under the belt) down to the hem. Draw the whole skirt including the part the guitar covered. No belt, no "
             "legs, no guitar.",
    "guitar": "The piece: the RED ELECTRIC GUITAR ONLY, with its rose decals and gold scrolls, the cream pickguard, "
              "pickups, knobs, the whole neck with its frets and dot inlays, and the headstock with its six tuners. "
              "Draw the whole guitar complete, including everything her hands and arms covered (the strings and "
              "pickups under her strumming hand, the neck under her fretting hand). No hands, no arms, no strap, no body.",
    "strum_arm": "The piece: her ARM ON THE VIEWER'S LEFT ONLY (her strumming arm): the rolled-up royal-blue sleeve "
                 "with white fringe at the shoulder, the bare upper arm and forearm reaching across, and her hand "
                 "strumming with a small guitar pick held between thumb and finger, exactly as posed. The sleeve was "
                 "cut off at the shoulder: finish its top as a smooth rounded shoulder cap of blue shirt. No guitar, no "
                 "strings, nothing behind the hand.",
    "fret_hand": "The piece: her HAND ON THE VIEWER'S RIGHT ONLY (the fretting hand gripping the guitar neck) with a "
                 "short piece of the wrist, exactly as posed: the fingers curled forward as if around a guitar neck, "
                 "the thumb. Do NOT draw the guitar neck: where the neck passed through her grip is empty and "
                 "transparent. No sleeve, no guitar.",
    "head": "The piece: her HEAD, NECK AND FRONT HAIR ONLY, WITHOUT the hat: her face with exactly the same pretty "
            "expression, the ears, the gold hoop earrings, the glossy auburn hair on top of her head and the curls that "
            "frame her face down to the jaw, and the neck down to a flat cut at the collarbone. Draw the top of her head "
            "that the hat hid: smooth glossy auburn hair with a side parting and soft volume. Do NOT draw the big mass "
            "of curls behind her shoulders (that is another piece). No hat, no shirt, no collar.",
    "hat": "The piece: her SKY-BLUE COWBOY HAT ONLY, with its studded band and big white star, the crown and the whole "
           "curled brim. Complete the brim and the crown's base where her hair and face overlapped them; we see the "
           "hat from the front at eye level, the underside of the brim only where it shows in image 1. No hair, no "
           "head, no face.",
}
ORDER = ["hair_back", "leg_l", "leg_r", "fret_arm", "torso", "skirt", "guitar", "strum_arm", "fret_hand", "head", "hat"]
FACES = {
    "blink": "both eyes gently CLOSED in a relaxed blink (long lashes on curved closed eyelid lines), the same sweet smirk",
    "smile": "a big delighted SMILE with the lips parted showing her upper teeth, eyes bright and wide open, eyebrows raised",
    "whoo": "a joyful 'WOO!': mouth open wide in a round cheering shape, eyes squeezed shut in happy crescents, eyebrows high",
    "wink": "a flirty WINK: the eye on the viewer's left closed in a curved line with lashes, the other eye open, a confident lopsided grin",
    "wow": "SURPRISED and excited: eyes wide open, eyebrows raised high, lips in a small round 'oh!'",
    "solo": "lost in a blazing guitar solo: eyes closed, eyebrows pinched together in concentration, biting her lower lip in a fierce grin",
    "pout": "a playful aw-shucks POUT: lips pushed into a little pout to one side, eyebrows tilted up in the middle, eyes glancing sideways",
}


def gen(part):
    os.makedirs(RAW, exist_ok=True)
    try:
        _, cost = orimg.generate(os.path.join(RAW, part + ".png"), HEADER + PARTS[part] + STYLE, aspect="2:3",
                                 refs=[FIG], model=MODEL)
        return f"OK {part} {cost}"
    except RuntimeError as e:
        return f"FAIL {part} {e}"


def face(name):
    p = (f"Redraw the attached image EXACTLY - the same cartoon woman's head, neck and hair, the same face shape, the "
         f"same hair, the same earrings, the same outlines and colours, the same position and size on the canvas, "
         f"transparent background - changing ONLY her facial expression (eyes, eyelids, eyebrows, mouth) to: "
         f"{FACES[name]}. She stays pretty and glamorous. Crisp clean flat cartoon linework, no other changes, no hat, "
         f"no other characters, no text.")
    try:
        _, cost = orimg.generate(os.path.join(RAW, f"face_{name}.png"), p, aspect="2:3",
                                 refs=[os.path.join(RAW, "head.png")], model=MODEL)
        return f"OK face {name} {cost}"
    except RuntimeError as e:
        return f"FAIL face {name} {e}"


# ------------------------------------------------------------------------------------------------ fit
def rgba(p):
    return np.asarray(Image.open(p).convert("RGBA")).astype(np.float32)


def over(im, bg=128.0):
    a = im[..., 3:4] / 255.
    return ((im[..., :3] * a + bg * (1 - a)) @ np.float32([.3, .59, .11])).clip(0, 255).astype(np.uint8)


def tidy(im):
    """The model's transparent pictures carry a faint haze round the ink: only what is on or by the solid drawing keeps
    its alpha."""
    a = im[..., 3]
    near = ndimage.binary_dilation(a > 128, iterations=3)
    im[..., 3] = np.where(near, a, 0)
    return im


# where each piece's middle roughly is on the figure (art px, read off a grid): the match must land near it
PRIOR = {"hair_back": (400, 390), "leg_l": (255, 1240), "leg_r": (600, 1240), "fret_arm": (650, 620),
         "torso": (440, 640), "skirt": (560, 920), "guitar": (585, 640), "strum_arm": (265, 700),
         "fret_hand": (810, 520), "head": (455, 300), "hat": (420, 150)}
PRIOR_R = 150


# Pieces the model redrew too freely for the automatic match (zoomed, re-proportioned): placed by landmarks read off
# grids of the raw piece and of the figure (art px). "aff": three raw points -> three figure points (an affine, so a
# piece drawn a little taller or longer is brought back to the figure's proportions); "st": scale + offset.
MANUAL = {
    "torso": ("aff", [(415, 520), (550, 1222), (95, 560)], [(405, 520), (575, 800), (225, 545)]),
    "strum_arm": ("aff", [(440, 290), (118, 685), (650, 1130)], [(250, 505), (160, 630), (370, 770)]),
    "fret_arm": ("aff", [(170, 395), (365, 1000), (885, 640)], [(600, 505), (685, 718), (800, 595)]),
    "fret_hand": ("aff", [(772, 465), (877, 595), (572, 942)], [(800, 472), (852, 518), (715, 650)]),
    "leg_l": ("st", .44, 86, 850),
    "leg_r": ("st", .44, 394, 854),
    "hair_back": ("st", .53, 122, 42),
    "skirt": ("st", .54, 234, 372),
}


def manual_M(name):
    m = MANUAL[name]
    if m[0] == "aff":
        return cv2.getAffineTransform(np.float32(m[1]), np.float32(m[2]))
    _, k, tx, ty = m
    return np.float32([[k, 0, tx], [0, k, ty]])


def edges(g):
    e = cv2.Canny(g.astype(np.uint8), 30, 90).astype(np.float32)
    return cv2.GaussianBlur(e, (0, 0), 1.6)


def register(raw, fig, name=None):
    """Where the model's drawing of a piece sits on the figure: it often draws a piece bigger than it is (zoomed in),
    so a multi-scale masked template match on the two pictures' EDGES (flat colour matches anything; ink lines do
    not), coarse at 1/4 size then fine, kept near the piece's place on the figure (PRIOR), then an ECC refinement.
    Returns M (2x3, raw px -> figure px) and the match score."""
    g_fig = over(fig).astype(np.float32)
    g_raw = over(raw).astype(np.float32)
    e_fig, e_raw = edges(g_fig), edges(g_raw)
    a = raw[..., 3]
    ys, xs = np.nonzero(a > 40)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    tpl = e_raw[y0:y1, x0:x1]
    msk = ndimage.binary_dilation(a[y0:y1, x0:x1] > 40, iterations=4).astype(np.float32)
    pc = PRIOR.get(name)

    def match(scale, ef, q):
        w, h = int(round(tpl.shape[1] * scale * q)), int(round(tpl.shape[0] * scale * q))
        if w < 10 or h < 10 or w >= ef.shape[1] or h >= ef.shape[0]:
            return -1, None
        t = cv2.resize(tpl, (w, h), interpolation=cv2.INTER_AREA)
        m = (cv2.resize(msk, (w, h), interpolation=cv2.INTER_AREA) > .5).astype(np.float32)
        r = cv2.matchTemplate(ef, t, cv2.TM_CCORR_NORMED, mask=m)
        r[~np.isfinite(r)] = -1
        if pc is not None:                      # only places that put the piece's middle near its prior
            yy, xx = np.mgrid[0:r.shape[0], 0:r.shape[1]]
            cx = (xx + w / 2) / q
            cy = (yy + h / 2) / q
            # the middle of the PIECE's box, moved by how far the raw's box middle is from its ink middle: use the box
            r[np.hypot(cx - pc[0], cy - pc[1]) > PRIOR_R] = -1
        _, mv, _, ml = cv2.minMaxLoc(r)
        return mv, (ml[0] / q, ml[1] / q)
    q = .25
    eq = cv2.resize(e_fig, None, fx=q, fy=q, interpolation=cv2.INTER_AREA)
    best = (-1, 1, None)
    lo, hi = globals().get("SCALES") or (.30, 1.14)
    for sc in np.arange(lo, hi, max(.01, (hi - lo) / 40)):
        mv, ml = match(sc, eq, q)
        if mv > best[0]:
            best = (mv, sc, ml)
    sc0 = best[1]
    best = (-1, sc0, None)
    for sc in np.arange(sc0 - .025, sc0 + .026, .005):
        mv, ml = match(sc, e_fig, 1.0)
        if mv > best[0]:
            best = (mv, sc, ml)
    score, sc, (lx, ly) = best
    M = np.float32([[sc, 0, lx - sc * x0], [0, sc, ly - sc * y0]])
    try:
        warped = cv2.warpAffine(g_raw, M, (fig.shape[1], fig.shape[0]), flags=cv2.INTER_LINEAR, borderValue=128)
        wm = cv2.warpAffine((a > 40).astype(np.uint8), M, (fig.shape[1], fig.shape[0]), flags=cv2.INTER_NEAREST)
        wm = (wm & (fig[..., 3] > 40)).astype(np.uint8)
        E = np.eye(2, 3, dtype=np.float32)
        _, E = cv2.findTransformECC(g_fig, warped, E, cv2.MOTION_EUCLIDEAN,
                                    (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), wm, 5)
        if abs(E[0, 2]) < 25 and abs(E[1, 2]) < 25 and abs(E[1, 0]) < .06:
            E3 = np.vstack([E, [0, 0, 1]])
            M = (np.linalg.inv(E3) @ np.vstack([M, [0, 0, 1]]))[:2].astype(np.float32)
    except cv2.error:
        pass
    return M, float(score)


def esrgan_x4(im):
    """Real-ESRGAN x4 of an RGBA float picture, through upscale4k.up4 (colour on the bled RGB, alpha as its own grey)."""
    import upscale4k
    return np.asarray(upscale4k.up4(Image.fromarray(im.clip(0, 255).astype(np.uint8), "RGBA"))).astype(np.float32)


def fit_one(name, fig, P_head=None):
    raw = tidy(rgba(os.path.join(RAW, name + ".png")))
    if raw.shape[:2] != fig.shape[:2]:
        raw = cv2.resize(raw, (fig.shape[1], fig.shape[0]), interpolation=cv2.INTER_AREA)
    if P_head is not None:                         # a face: laid back on the head it was drawn from (ECC), then the head's fit
        head = tidy(rgba(os.path.join(RAW, "head.png")))
        warp = np.eye(2, 3, dtype=np.float32)
        try:
            _, warp = cv2.findTransformECC(over(head).astype(np.float32), over(raw).astype(np.float32), warp,
                                           cv2.MOTION_EUCLIDEAN, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6),
                                           None, 5)
        except cv2.error:
            pass
        W3 = np.vstack([warp, [0, 0, 1]])
        M = (np.vstack([P_head, [0, 0, 1]]) @ np.linalg.inv(W3))[:2]
        how = f"face ecc {warp[0, 2]:+.1f},{warp[1, 2]:+.1f}"
    else:
        if name in MANUAL:
            M, how = manual_M(name), "manual"
        else:
            M, score = register(raw, fig, name)
            how = f"match {score:.3f}"
    M = np.float32(M)
    up = esrgan_x4(raw)                            # 4096 x 6144
    Q = M.copy()
    Q[:, 2] *= PLATE                               # art px -> plate px; the x4 picture is 4 px per raw px
    Q[:, :2] *= PLATE / 4.0
    Wp, Hp = int(ART[0] * PLATE), int(ART[1] * PLATE)
    pm = up.copy()
    pm[..., :3] *= pm[..., 3:4] / 255.
    out = cv2.warpAffine(pm, Q, (Wp, Hp), flags=cv2.INTER_AREA, borderValue=(0, 0, 0, 0))
    al = out[..., 3:4].clip(0, 255)
    out[..., :3] = np.where(al > 1, out[..., :3] * 255. / np.maximum(al, 1), 0)
    out = out.clip(0, 255)
    ys, xs = np.nonzero(out[..., 3] > 6)
    x0, y0, x1, y1 = max(0, xs.min() - 6), max(0, ys.min() - 6), min(Wp, xs.max() + 7), min(Hp, ys.max() + 7)
    crop = out[y0:y1, x0:x1]
    s = float(np.hypot(M[0, 0], M[1, 0]))
    return crop, [int(x0), int(y0), int(x1 - x0), int(y1 - y0)], M, f"{how}  scale {s:.3f} shift {M[0, 2]:+.1f},{M[1, 2]:+.1f}"


def fit(names):
    os.makedirs(OUT, exist_ok=True)
    fig = rgba(FIG)
    mp = os.path.join(OUT, "parts.json")
    meta = json.load(open(mp)) if os.path.exists(mp) else {}
    meta.update({"art": list(ART), "scale": PLATE, "size": [int(ART[0] * PLATE), int(ART[1] * PLATE)],
                 "order": ORDER})
    meta.setdefault("parts", {})
    meta.setdefault("faces", {})
    meta.setdefault("fits", {})
    for nm in names:
        if nm.startswith("face_"):
            continue
        if not os.path.exists(os.path.join(RAW, nm + ".png")):
            print("missing", nm); continue
        crop, box, M, note = fit_one(nm, fig)
        Image.fromarray(crop.astype(np.uint8), "RGBA").save(os.path.join(OUT, nm + ".png"))
        meta["parts"][nm] = {"box": box}
        meta["fits"][nm] = M.tolist()
        print(f"{nm:10s} box {box}  {note}", flush=True)
    if "head" in meta["fits"]:
        P_head = np.float32(meta["fits"]["head"])
        for f in [n[5:] for n in names if n.startswith("face_")] or []:
            if not os.path.exists(os.path.join(RAW, f"face_{f}.png")):
                continue
            crop, box, M, note = fit_one(f"face_{f}", fig, P_head)
            Image.fromarray(crop.astype(np.uint8), "RGBA").save(os.path.join(OUT, f"face_{f}.png"))
            meta["faces"][f] = {"box": box}
            print(f"face {f:6s} box {box}  {note}", flush=True)
    json.dump(meta, open(mp, "w"), indent=1)


def figure(skip=()):
    meta = json.load(open(os.path.join(OUT, "parts.json")))
    Wp, Hp = meta["size"]
    can = Image.new("RGBA", (Wp, Hp), (0, 0, 0, 0))
    for nm in meta["order"]:
        if nm in skip or nm not in meta["parts"]:
            continue
        im = Image.open(os.path.join(OUT, nm + ".png")).convert("RGBA")
        tmp = Image.new("RGBA", (Wp, Hp), (0, 0, 0, 0))
        tmp.paste(im, tuple(meta["parts"][nm]["box"][:2]))
        can = Image.alpha_composite(can, tmp)
    return can


def sheet():
    a = Image.open(FIG).convert("RGBA").resize((512, 768), Image.LANCZOS)
    b = figure().resize((512, 768), Image.LANCZOS)
    s = Image.new("RGBA", (1024 + 512, 768), (235, 235, 240, 255))
    s.alpha_composite(a, (0, 0))
    s.alpha_composite(b, (512, 0))
    # the pieces spread out, each on its own tile
    meta = json.load(open(os.path.join(OUT, "parts.json")))
    names = [n for n in meta["order"] if n in meta["parts"]]
    cols = 3
    cell = 512 // cols
    for k, nm in enumerate(names):
        im = Image.open(os.path.join(OUT, nm + ".png")).convert("RGBA")
        im.thumbnail((cell - 4, cell * 1.4 - 4))
        x, y = 1024 + (k % cols) * cell, (k // cols) * int(cell * 1.4)
        s.alpha_composite(im, (x + 2, y + 2))
    s.convert("RGB").save(os.path.join(SRC, "rosie", "_parts_sheet.jpg"), quality=88)
    print("sheet", os.path.join(SRC, "rosie", "_parts_sheet.jpg"))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "sheet"
    names = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    if cmd == "gen":
        with ThreadPoolExecutor(6) as ex:
            for r in ex.map(gen, names or ORDER):
                print(r, flush=True)
    elif cmd == "faces":
        with ThreadPoolExecutor(6) as ex:
            for r in ex.map(face, names or list(FACES)):
                print(r, flush=True)
    elif cmd == "fit":
        fit(names or ORDER + [f"face_{f}" for f in FACES])
    elif cmd == "sheet":
        sheet()
