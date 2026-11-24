"""Rosie v2's rig pieces, CUT from the figure (art/broadway-src/rosie2/rosie_v2.png) instead of redrawn (owner,
2026-11-22: "the body parts are not cut correctly"). v1 asked the image model to redraw each piece on its own, and it
drew them at their own scales and proportions; here every visible pixel of a piece is the figure's own pixel, so the
pieces fit back together exactly, and the model is used only to fill what another piece hid.

  cut       A cartoon is flat colour areas closed by black ink. Every flat area is labelled; each goes to the first piece
            (in PRIORITY order) whose guide shape (POLY, loose, figure px) holds its middle - skin only to pieces that
            have skin - and every ink pixel goes to the front-most piece whose areas lie within INK_REACH of it (an
            outline belongs to the shape in front). -> art/broadway-src/rosie2/cut/<part>.png + _cut_debug.jpg
  complete  each cut piece redrawn by the model on its own canvas with its hidden parts completed (one call each)
            -> rosie2/complete/<part>.png
  fit       the completion laid back on the cut (multi-scale edge match + ECC), used ONLY where the piece was hidden
            (the figure's ink belonging to pieces in front of it), the cut's own pixels kept; enlarged x4 and brought
            to the plate scale -> art/broadway-src/rosie_parts/ (the same layout blender/rosie_rig.py reads)
  faces     reaction faces: the head piece redrawn with only its expression changed, laid back on it (ECC)
usage: python tools/broadway/rosie_cut.py cut|complete|fit|faces|sheet [names]"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import orimg
import rosie_parts as RP

ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "art", "broadway-src")
D2 = os.path.join(SRC, "rosie2")
FIG = os.path.join(D2, "rosie_v2.png")
CUT = os.path.join(D2, "cut")
COMP = os.path.join(D2, "complete")
OUT = os.path.join(SRC, "rosie_parts")
MODEL = "openai/gpt-image-2.6-sunburst"
ART = (1024, 1536)
PLATE = 2.0
ORDER = ["hair_back", "leg_l", "leg_r", "torso", "fret_arm", "skirt", "guitar", "strum_arm", "fret_hand", "head", "hat"]   # back to front
# the fret hand is cut off its arm along this shape (the arm and hand are one skin area): the hand grips the neck in
# front of it, the arm goes behind the guitar, so the elbow the neck hides stays hidden whatever the arm does
HAND_CUT = [(752, 455), (850, 455), (850, 610), (742, 610), (735, 560)]
PRIORITY = ["hat", "head", "guitar", "fret_arm", "strum_arm", "skirt", "leg_l", "leg_r", "torso", "hair_back"]
SKIN_OK = {"head", "fret_arm", "strum_arm", "torso", "leg_l", "leg_r"}
INK_REACH = 6
POLY = {   # loose guide shapes, figure px (1024 x 1536)
    "hat": [[(255, 0), (650, 0), (650, 125), (560, 165), (470, 192), (395, 205), (330, 215), (285, 225), (250, 212)]],
    "head": [[(372, 140), (545, 135), (562, 250), (545, 350), (470, 385), (410, 378), (375, 320), (365, 230)]],
    "guitar": [[(250, 650), (400, 610), (520, 610), (575, 640), (585, 700), (565, 800), (480, 850), (380, 935), (250, 935)],
               [(530, 620), (900, 368), (978, 398), (962, 472), (870, 502), (600, 692), (560, 702)]],
    "fret_arm": [[(555, 418), (622, 418), (652, 520), (690, 556), (758, 466), (845, 466), (845, 602), (700, 622), (618, 602), (575, 520)]],
    "strum_arm": [[(160, 420), (345, 420), (350, 520), (300, 560), (300, 620), (470, 690), (470, 830), (370, 830), (170, 660)]],
    "skirt": [[(262, 598), (655, 598), (668, 892), (245, 892)]],
    "leg_l": [[(195, 868), (445, 868), (425, 1200), (355, 1545), (185, 1545)]],
    "leg_r": [[(478, 868), (690, 868), (770, 1545), (535, 1545), (555, 1200)]],
    "torso": [[(285, 365), (605, 365), (615, 625), (275, 625)]],
    "hair_back": [[(215, 110), (405, 110), (425, 570), (215, 570)], [(515, 120), (610, 120), (610, 410), (515, 410)]],
}
HEADER = ("Image 1 is ONE cut-out piece of a cartoon character for a slot game (image 2 is the whole character, for "
          "reference). Redraw image 1 EXACTLY - the same piece, the same pose, the same SIZE and the SAME POSITION on the "
          "canvas, the same black line weight and flat colours, every visible part unchanged - and COMPLETE the parts "
          "that were hidden behind other pieces, as clean finished drawing in the same style: ")
TAIL = (" Transparent background. Draw ONLY this piece: no other body parts, no guitar unless asked, no text, no "
        "shadow. Crisp, flat, clean TV-animation linework; no blur, no gradients.")
COMPLETE = {
    "hair_back": "the back mass of her auburn curls - fill in all the hair hidden behind her head, neck, shoulders and "
                 "hat as one complete mass of curls (where her face and neck were, draw hair).",
    "leg_l": "her leg on the viewer's left - draw the whole bare thigh up to a flat top edge at the hip, well above "
             "where the skirt's hem and the guitar covered it.",
    "leg_r": "her leg on the viewer's right - draw the whole bare thigh up to a flat top edge at the hip, well above "
             "where the skirt's hem covered it.",
    "torso": "her torso in the tight royal-blue western shirt - complete the shirt and the belt everywhere her arms, the "
             "guitar, the strap and her hair covered them, keep the neck and the V of skin at the collar, and finish "
             "each shoulder as a smooth rounded cap of blue shirt where the sleeve joins.",
    "skirt": "her tight red mini skirt - complete the whole skirt, including everything the guitar covered.",
    "guitar": "the red electric guitar - complete the whole guitar (body, pickguard, pickups, strings, the neck under her "
              "fretting hand and the body under her strumming hand). No hands.",
    "fret_hand": "her hand on the viewer's right curled round a guitar neck that is NOT drawn - complete the fingers and "
                 "the thumb the neck hid, leaving the space inside the grip empty.",
    "fret_arm": "her arm on the viewer's right with its short blue sleeve - complete the top of the sleeve as a smooth "
                "rounded shoulder cap, and the fingers and thumb of the hand that were hidden by the guitar neck, as a "
                "hand curled round a neck that is not drawn.",
    "strum_arm": "her arm on the viewer's left with its short blue sleeve - complete the top of the sleeve as a smooth "
                 "rounded shoulder cap and anything of the arm and hand hidden by the guitar.",
    "head": "her head and neck - complete the top of her head that the hat hid (smooth auburn hair) and the neck down "
            "to a flat cut below the collar line.",
    "hat": "her sky-blue cowboy hat - complete the brim and crown where her hair covered them.",
}


def rgba(p):
    return np.asarray(Image.open(p).convert("RGBA")).astype(np.float32)


def poly_mask(polys, shape):
    m = Image.new("L", (shape[1], shape[0]), 0)
    d = ImageDraw.Draw(m)
    for p in polys:
        d.polygon(p, fill=255)
    return np.asarray(m) > 0


def is_skin(rgb):
    r, g, b = rgb
    return r > 190 and 120 < g < 215 and 80 < b < 175 and r - b > 55


def colour_class(rgb):
    """The flat colour an area is painted in, as the cut's colour gates see it (hue / saturation / value)."""
    import colorsys
    r, g, b = [float(v) / 255 for v in rgb]
    h, sat, v = colorsys.rgb_to_hsv(r, g, b)
    h *= 360
    if is_skin(rgb):
        return "skin"
    if v < .3:
        return "dark"
    if v > .8 and sat < .2:
        return "white"
    if 190 <= h < 228 and sat > .3 and v > .7:
        return "lightblue"
    if 200 <= h < 265 and sat > .4:
        return "blue"
    if (h < 10 or h > 340) and sat > .5:
        return "red"
    if 10 <= h < 40 and sat > .78 and v < .75:
        return "hair"
    if 10 <= h < 55 and v < .85:
        return "brown"
    return "grey"


# hand-placed exceptions, read off zoomed grids of the figure: an area smaller than `most` px whose middle is inside the
# box and whose colour is in the set goes to that piece - the bits of the red belt and its buckle that peek out under
# the guitar's horn belong to the torso, a hair lock beside the strumming sleeve to the back hair
OVERRIDE = [((395, 598, 492, 662), "torso", {"red", "white", "grey"}, 1500),
            ((330, 455, 395, 548), "hair_back", {"hair", "brown", "dark"}, 5000)]

# which flat colours each piece may take (an area of any other colour is never given to it, whatever its guide holds)
ACCEPT = {
    "hat": {"lightblue", "blue", "white", "dark", "grey"},
    "head": {"skin", "hair", "white", "red", "dark", "grey", "blue_small", "brown"},
    "hair_back": {"hair", "dark", "brown"},
    "torso": {"blue", "white", "brown", "skin", "grey", "dark", "red"},
    "skirt": {"red", "dark"},
    "guitar": {"red", "white", "grey", "brown", "skin", "dark"},
    "fret_arm": {"skin", "blue", "white", "dark"},
    "strum_arm": {"skin", "blue", "white", "dark"},
    "leg_l": {"skin", "red", "white", "blue", "brown", "dark", "grey"},
    "leg_r": {"skin", "red", "white", "blue", "brown", "dark", "grey"},
}


def load_fig():
    """The figure with the image model's faint alpha haze cleared (only ink and fills, and their own soft rim)."""
    fig = RP.tidy(rgba(FIG))
    fig[..., 3] = np.where(fig[..., 3] > 24, fig[..., 3], 0)
    return fig


def cut():
    os.makedirs(CUT, exist_ok=True)
    fig = load_fig()
    a = fig[..., 3]
    lum = fig[..., :3] @ np.float32([.3, .59, .11])
    chroma = fig[..., :3].max(-1) - fig[..., :3].min(-1)
    ink = (a > 128) & (lum < 62) & (chroma < 45)               # black line work (dark auburn hair shade is not ink)
    flat = (a > 128) & ~ink
    lab, n = ndimage.label(flat)
    polys = {p: poly_mask(POLY[p], a.shape) for p in POLY}
    neck = poly_mask(POLY["guitar"][1:], a.shape)
    owner = np.full(n + 1, -1, int)
    objs = ndimage.find_objects(lab)
    cen = ndimage.center_of_mass(flat, lab, range(1, n + 1))
    # each area goes to the guide shape that holds the largest share of it; shares within .15 of the best go to the
    # piece earliest in PRIORITY (the guitar's body lies inside the skirt's guide too, the skirt round it does not)
    for i in range(1, n + 1):
        sl = objs[i - 1]
        m = lab[sl] == i
        if m.sum() < 2:
            continue
        col = np.median(fig[sl][m][:, :3], axis=0)
        cc = colour_class(col)
        if cc == "blue" and m.sum() < 400:
            cc_head = "blue_small"                         # an iris may stay on the head; a collar may not
        else:
            cc_head = cc
        hh, ww = m.shape
        belt = cc == "red" and hh < 34 and ww > 80                # the thin red belt: the torso's, not the guitar's or skirt's
        share = {}
        for p in PRIORITY:
            if (cc_head if p == "head" else cc) not in ACCEPT[p]:
                continue
            if belt and p != "torso":
                continue
            if p == "guitar" and cc == "brown":                    # brown on the guitar is only its neck (the strap is the torso's)
                share[p] = float((neck[sl] & m).sum()) / m.sum()
                continue
            share[p] = float((polys[p][sl] & m).sum()) / m.sum()
        if not share or max(share.values()) <= 0:
            continue
        best = max(share.values())
        for p in PRIORITY:
            if p in share and share[p] >= best - .15:
                owner[i] = ORDER.index(p)
                break
        cy, cx = cen[i - 1]
        for (x0, y0, x1, y1), p, ok, most in OVERRIDE:
            if x0 <= cx < x1 and y0 <= cy < y1 and cc in ok and m.sum() < most:
                owner[i] = ORDER.index(p)
    # areas no guide holds: the nearest assigned area's piece
    assigned = owner[lab] >= 0
    if (~assigned & flat).any():
        _, (iy, ix) = ndimage.distance_transform_edt(~(assigned & flat), return_indices=True)
        part_map = np.where(assigned, owner[lab], owner[lab[iy, ix]])
    else:
        part_map = owner[lab]
    part_map = np.where(flat, part_map, -1)
    # ink: the front-most piece within reach
    ink_owner = np.full(a.shape, -1, int)
    for k, p in enumerate(ORDER):
        near = ndimage.binary_dilation(part_map == k, iterations=INK_REACH)
        ink_owner[near & ink] = k
    left = ink & (ink_owner < 0)
    if left.any():
        _, (iy, ix) = ndimage.distance_transform_edt(part_map < 0, return_indices=True)
        ink_owner[left] = part_map[iy[left], ix[left]]
    final = np.where(flat, part_map, np.where(ink, ink_owner, -1))
    # the fret hand: the fret arm's pixels inside HAND_CUT
    fa, fh = ORDER.index("fret_arm"), ORDER.index("fret_hand")
    final[(final == fa) & poly_mask([HAND_CUT], a.shape)] = fh
    # soft edges: the figure's own antialiased rim goes with the nearest piece
    rim = (a > 0) & (final < 0)
    if rim.any():
        _, (iy, ix) = ndimage.distance_transform_edt(final < 0, return_indices=True)
        final[rim] = final[iy[rim], ix[rim]]
    np.save(os.path.join(CUT, "_owner.npy"), final.astype(np.int8))
    dbg = np.zeros((a.shape[0], a.shape[1], 3), np.float32)
    cols = np.array([(230, 120, 40), (80, 200, 80), (40, 160, 230), (60, 60, 230), (230, 60, 60), (230, 200, 40),
                     (200, 60, 200), (60, 230, 230), (250, 250, 250), (140, 90, 255), (255, 140, 200)], np.float32)
    for k, p in enumerate(ORDER):
        m = final == k
        piece = fig.copy()
        piece[..., 3] = np.where(m, a, 0)
        Image.fromarray(piece.astype(np.uint8), "RGBA").save(os.path.join(CUT, p + ".png"))
        dbg[m] = fig[m][:, :3] * .45 + cols[k] * .55
        print(f"{p:10s} {int(m.sum()):7d} px", flush=True)
    Image.fromarray(dbg.astype(np.uint8)).resize((683, 1024), Image.LANCZOS).save(os.path.join(D2, "_cut_debug.jpg"), quality=90)
    print("debug", os.path.join(D2, "_cut_debug.jpg"))


def complete(part):
    os.makedirs(COMP, exist_ok=True)
    try:
        _, c = orimg.generate(os.path.join(COMP, part + ".png"), HEADER + COMPLETE[part] + TAIL, aspect="2:3",
                              refs=[os.path.join(CUT, part + ".png"), FIG], model=MODEL)
        return f"OK {part} {c}"
    except RuntimeError as e:
        return f"FAIL {part} {e}"


def register_to(raw, ref, prior=None):
    """raw (the model's redraw) -> ref (the cut): the scale and offset at which the cut's own visible pixels best match
    the redraw's colours (masked squared difference over the cut's solid pixels, on grey), searched over scales
    .2 - 1.35, coarse at 1/4 size then fine. Colour is far more telling than edges here: the redraw repeats the cut's
    flat colours exactly where the cut has them. Returns M (2x3, raw px -> ref px) and a score (lower = closer)."""
    def on_grey(im):
        a = im[..., 3:4] / 255.
        return (im[..., :3] * a + 128 * (1 - a)).astype(np.float32)
    ys, xs = np.nonzero(ref[..., 3] > 60)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    tpl = on_grey(ref[y0:y1, x0:x1])
    msk = ndimage.binary_erosion(ref[y0:y1, x0:x1, 3] > 200, iterations=2).astype(np.float32)
    img = on_grey(raw)

    def best_at(sc, q):
        im = cv2.resize(img, None, fx=sc * q, fy=sc * q, interpolation=cv2.INTER_AREA)
        t = cv2.resize(tpl, None, fx=q, fy=q, interpolation=cv2.INTER_AREA)
        m = (cv2.resize(msk, (t.shape[1], t.shape[0]), interpolation=cv2.INTER_AREA) > .5).astype(np.float32)
        if t.shape[0] >= im.shape[0] or t.shape[1] >= im.shape[1] or m.sum() < 20:
            return 1e18, (0, 0)
        r = cv2.matchTemplate(im, t, cv2.TM_SQDIFF, mask=np.dstack([m] * 3))
        r[~np.isfinite(r)] = 1e18
        mv, _, ml, _ = cv2.minMaxLoc(r)
        return mv / m.sum(), (ml[0] / q, ml[1] / q)
    q = .25
    best = (1e18, 1, (0, 0))
    for sc in np.arange(.2, 1.36, .02):
        v, ml = best_at(sc, q)
        if v < best[0]:
            best = (v, sc, ml)
    sc0 = best[1]
    best = (1e18, sc0, (0, 0))
    for sc in np.arange(sc0 - .025, sc0 + .026, .005):
        v, ml = best_at(sc, .5)
        if v < best[0]:
            best = (v, sc, ml)
    v, sc, (lx, ly) = best
    M = np.float32([[sc, 0, x0 - lx], [0, sc, y0 - ly]])
    return M, float(v)


BOX_FIT = {"guitar"}


def box_fit(raw, ref):
    """The redraw's largest solid shape laid box on box over the cut's (uniform scale by width, centres matched)."""
    def main_box(im):
        lab, n = ndimage.label(im[..., 3] > 128)
        if n == 0:
            return None
        sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
        k = int(np.argmax(sizes)) + 1
        ys, xs = np.nonzero(lab == k)
        return xs.min(), ys.min(), xs.max(), ys.max()
    a, b = main_box(raw), main_box(ref)
    sc = ((b[2] - b[0]) / max(1, a[2] - a[0]) + (b[3] - b[1]) / max(1, a[3] - a[1])) / 2
    cx_a, cy_a, cx_b, cy_b = (a[0] + a[2]) / 2, (a[1] + a[3]) / 2, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    return np.float32([[sc, 0, cx_b - sc * cx_a], [0, sc, cy_b - sc * cy_a]])


SKIRT_CX = 470                # figure px: the skirt's middle (its hidden left side mirrors its visible right side)


def skirt_fill(cut_im):
    """The whole tight skirt behind the cut: its visible right edge and hem (read row by row off the cut) mirrored about
    SKIRT_CX for the side the guitar hides, filled with its own red and outlined in black."""
    solid = cut_im[..., 3] > 200
    ys = np.nonzero(solid.any(1))[0]
    top, bot = int(ys.min()), int(ys.max())
    right = []
    for y in range(top, bot + 1, 4):
        xs = np.nonzero(solid[y])[0]
        if len(xs) and xs.max() > SKIRT_CX + 40:
            right.append((int(xs.max()), y))
    if len(right) < 5:
        return None
    hem_y = max(y for _, y in right)
    poly = [(SKIRT_CX, top)] + right + [(SKIRT_CX, hem_y + 4)] + [(2 * SKIRT_CX - x, y) for x, y in reversed(right)]
    sh = poly_mask([poly], cut_im.shape[:2])
    sh = ndimage.binary_opening(sh, iterations=2)
    reds = cut_im[..., :3][solid & (cut_im[..., 0] > 150)]
    col = np.median(reds, axis=0) if len(reds) else np.float32([186, 36, 36])
    edge = sh & ~ndimage.binary_erosion(sh, iterations=4)
    edge &= ~(np.arange(cut_im.shape[0])[:, None] < top + 8)      # no line along the waist (the belt sits there)
    fill = np.zeros_like(cut_im)
    fill[sh, :3] = col
    fill[edge, :3] = 17
    fill[sh, 3] = 255
    return fill


# the fret arm's elbow, hidden in the figure by the guitar neck: a band of skin bridging the two cut edges, with the
# elbow's outer and inner contours (figure px, read off a zoomed grid of the cut)
ELBOW_FILL = [(598, 594), (652, 551), (706, 577), (662, 618)]
ELBOW_LINES = [[(611, 593), (636, 607), (662, 616)], [(648, 552), (676, 563), (701, 578)]]


def elbow_fill(cut_im):
    from PIL import Image as _I, ImageDraw as _D
    solid = cut_im[..., 3] > 200
    skin = cut_im[..., :3][solid & (cut_im[..., 0] > 200) & (cut_im[..., 2] > 90)]
    col = tuple(int(v) for v in (np.median(skin, axis=0) if len(skin) else (246, 173, 125)))
    layer = _I.new("RGBA", (cut_im.shape[1], cut_im.shape[0]), (0, 0, 0, 0))
    d = _D.Draw(layer)
    d.polygon(ELBOW_FILL, fill=col + (255,))
    for ln in ELBOW_LINES:
        d.line(ln, fill=(17, 17, 17, 255), width=5, joint="curve")
    return np.asarray(layer).astype(np.float32)


# the guitar's neck, nut -> body (figure px), and how far along it a visible stretch is copied from
NECK = ((905, 432), (560, 652))
NECK_HALF = 27


def guitar_fill(cut_im, covered=None):
    """The guitar's hidden spots rebuilt from the guitar itself: the gap the fret hand leaves in the neck is filled with
    the stretch of the same neck NECK_COPY px nearer the body (frets and dots and all, slid along its axis), and the
    hole under the strumming hand (inside the body's outline) is inpainted from round it."""
    H, W = cut_im.shape[:2]
    (x0, y0), (x1, y1) = NECK
    d = np.float32([x1 - x0, y1 - y0]); L = float(np.hypot(*d)); d /= L
    nrm = np.float32([-d[1], d[0]])
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rx, ry = xx - x0, yy - y0
    along, across = rx * d[0] + ry * d[1], rx * nrm[0] + ry * nrm[1]
    band = (np.abs(across) <= NECK_HALF) & (along > 20) & (along < L - 10)
    out = cut_im.copy()
    gap = band & (cut_im[..., 3] < 200)
    for shift in (110, 150, 75):                          # the first visible stretch nearer the body that has the neck
        sx = (xx + d[0] * shift).astype(np.int32).clip(0, W - 1)
        sy = (yy + d[1] * shift).astype(np.int32).clip(0, H - 1)
        src = cut_im[sy, sx]
        ok = gap & (src[..., 3] > 200)
        out[ok] = src[ok]
        gap &= ~ok
    # holes inside the body's outline - the outline closed where the hands covered it
    solid = out[..., 3] > 128
    holes = ndimage.binary_fill_holes(solid) & ~solid
    if covered is not None:
        closed = ndimage.binary_closing(np.pad(solid, 60), structure=np.ones((3, 3)), iterations=45)[60:-60, 60:-60]
        holes |= closed & ~solid & covered
    holes = ndimage.binary_dilation(holes, iterations=2) & ~ndimage.binary_erosion(solid, iterations=1)
    if holes.any():
        pm = (out[..., :3] * (out[..., 3:4] / 255.)).clip(0, 255).astype(np.uint8)
        filled = cv2.inpaint(pm, holes.astype(np.uint8) * 255, 9, cv2.INPAINT_TELEA).astype(np.float32)
        out[holes, :3] = filled[holes]
        out[holes, 3] = 255
    return out


REACH = {"torso": 130, "skirt": 120, "guitar": 70, "hair_back": 110, "head": 150, "hat": 40, "fret_hand": 30,
         "strum_arm": 40, "fret_arm": 70, "leg_l": 90, "leg_r": 90}


def fit(names):
    os.makedirs(OUT, exist_ok=True)
    fig = load_fig()
    owner = np.load(os.path.join(CUT, "_owner.npy"))
    meta = {"art": list(ART), "scale": PLATE, "size": [int(ART[0] * PLATE), int(ART[1] * PLATE)], "order": ORDER,
            "parts": {}, "faces": {}, "fits": {}}
    mp = os.path.join(OUT, "parts.json")
    if os.path.exists(mp):
        old = json.load(open(mp))
        if old.get("order") == ORDER:
            meta["faces"] = old.get("faces", {})
            meta["parts"].update(old.get("parts", {}))
    for p in names:
        k = ORDER.index(p)
        cut_im = rgba(os.path.join(CUT, p + ".png"))
        mine = owner == k
        # where a piece in front of it covered it - but only near the piece itself (within REACH px of what shows of it)
        near = ndimage.distance_transform_edt(~mine) <= REACH.get(p, 90)
        hidden = (fig[..., 3] > 0) & (owner > k) & near
        hidden = ndimage.binary_dilation(hidden, iterations=3) & ~ndimage.binary_erosion(mine, iterations=1) & near
        out = cut_im.copy()
        how = "cut only"
        cp = os.path.join(COMP, p + ".png")
        warped, how = None, "cut only"
        if os.path.exists(cp):
            raw = RP.tidy(rgba(cp))
            if raw.shape[:2] != fig.shape[:2]:
                raw = cv2.resize(raw, (fig.shape[1], fig.shape[0]), interpolation=cv2.INTER_AREA)
            ys, xs = np.nonzero(cut_im[..., 3] > 60)
            RP.PRIOR["_x"] = (float(xs.mean()), float(ys.mean())); RP.PRIOR_R = 110
            if hasattr(RP, "SCALES"):
                del RP.SCALES
            if p in BOX_FIT:                                  # the cut has the piece's whole outline: box on box
                M, score = box_fit(raw, cut_im), 0.0
            else:
                M, score = RP.register(raw, cut_im, "_x")
            w = cv2.warpAffine(raw, M, (fig.shape[1], fig.shape[0]), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
            solid = cut_im[..., 3] > 200
            cover = (solid & (w[..., 3] > 128)).sum() / max(1, solid.sum())
            if cover >= .8:
                warped = w
                how = f"completed (edges {score:.2f}, cover {cover:.0%}, scale {float(M[0, 0]):.3f})"
            else:
                how = f"cut only (the redraw did not line up: cover {cover:.0%})"
        if p == "skirt":
            warped, how = skirt_fill(cut_im), "cut + its hidden side, mirrored from its visible right side"
            hidden = np.ones_like(hidden)
        if p == "fret_arm":
            warped, how = elbow_fill(cut_im), "cut + the elbow the neck hid, bridged"
            hidden = np.ones_like(hidden)
        if p == "guitar":
            covered = ndimage.binary_dilation(np.isin(owner, [ORDER.index("strum_arm"), ORDER.index("fret_hand")]), iterations=6)
            warped, how = guitar_fill(cut_im, covered), "cut + its neck gap copied along the neck, the hand hole inpainted"
            hidden = np.ones_like(hidden)
        out = cut_im.copy()
        if warped is not None:
            fill = hidden & (warped[..., 3] > 8) & (cut_im[..., 3] < 250)
            soft = cv2.GaussianBlur(fill.astype(np.float32), (0, 0), .8)[..., None]
            ca = cut_im[..., 3:4] / 255.
            out[..., 3] = np.clip(cut_im[..., 3] + warped[..., 3] * soft[..., 0] * (1 - ca[..., 0]), 0, 255)
            rgb_a = np.maximum(out[..., 3:4], 1) / 255.
            out[..., :3] = np.clip((cut_im[..., :3] * ca + warped[..., :3] * soft * (1 - ca)) / np.maximum(rgb_a, 1e-3), 0, 255)
        if p == "head":                                     # the crown the hat hid: her hair colour, flat
            solid = out[..., 3] > 128
            under_hat = ndimage.binary_dilation(owner == ORDER.index("hat"), iterations=4)
            closed = ndimage.binary_closing(np.pad(solid, 80), structure=np.ones((3, 3)), iterations=60)[80:-80, 80:-80]
            crown = closed & ~solid & under_hat
            hair = out[..., :3][solid & (out[..., 0] > 90) & (out[..., 1] < 100) & (out[..., 2] < 70)]
            if crown.any() and len(hair):
                out[crown, :3] = np.median(hair, axis=0)
                out[crown, 3] = 255
                how += f", crown filled ({int(crown.sum())} px)"
        up = RP.esrgan_x4(out)
        Wp, Hp = meta["size"]
        pm = up.copy()
        pm[..., :3] *= pm[..., 3:4] / 255.
        sm = cv2.resize(pm, (Wp, Hp), interpolation=cv2.INTER_AREA)
        al = sm[..., 3:4].clip(0, 255)
        sm[..., :3] = np.where(al > 1, sm[..., :3] * 255. / np.maximum(al, 1), 0)
        ys, xs = np.nonzero(sm[..., 3] > 6)
        x0, y0, x1, y1 = max(0, xs.min() - 6), max(0, ys.min() - 6), min(Wp, xs.max() + 7), min(Hp, ys.max() + 7)
        Image.fromarray(sm[y0:y1, x0:x1].clip(0, 255).astype(np.uint8), "RGBA").save(os.path.join(OUT, p + ".png"))
        meta["parts"][p] = {"box": [int(x0), int(y0), int(x1 - x0), int(y1 - y0)]}
        meta["fits"][p] = [[1, 0, 0], [0, 1, 0]]
        print(f"{p:10s} {how}", flush=True)
    json.dump(meta, open(mp, "w"), indent=1)


FACES = RP.FACES
FACE_CUT_Y = 372            # figure px: below this every face is the neutral head's (neck, collar V)


def face(name):
    p = (f"Redraw the attached cartoon character head EXACTLY - the same face shape, the same hair, the same outlines and "
         f"flat colours, the same position and size on the canvas, transparent background - changing ONLY the facial "
         f"expression (eyes, eyelids, eyebrows, mouth) to: {FACES[name]}. Clean flat TV-animation linework, no other "
         f"changes, no hat, no text.")
    try:
        _, c = orimg.generate(os.path.join(COMP, f"face_{name}.png"), p, aspect="2:3",
                              refs=[os.path.join(D2, "_head_face.png")], model=MODEL)
        return f"OK face {name} {c}"
    except RuntimeError as e:
        return f"FAIL face {name} {e}"


def head_full():
    """The head piece as completed (cut + fill), at figure size: what the reaction faces are drawn from."""
    meta = json.load(open(os.path.join(OUT, "parts.json")))
    W, H = meta["size"]
    can = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    can.paste(Image.open(os.path.join(OUT, "head.png")).convert("RGBA"), tuple(meta["parts"]["head"]["box"][:2]))
    can = can.resize(ART, Image.LANCZOS)
    can.save(os.path.join(D2, "_head_full.png"))
    # what the faces are drawn from: the head above the neck (the collar's V of skin is not shown to the model)
    a = np.asarray(can).copy()
    a[FACE_CUT_Y:, :, 3] = 0
    Image.fromarray(a).save(os.path.join(D2, "_head_face.png"))


def fit_faces(names):
    meta = json.load(open(os.path.join(OUT, "parts.json")))
    head = RP.tidy(rgba(os.path.join(D2, "_head_full.png")))
    for f in names:
        fp = os.path.join(COMP, f"face_{f}.png")
        if not os.path.exists(fp):
            continue
        im = RP.tidy(rgba(fp))
        if im.shape[:2] != head.shape[:2]:
            im = cv2.resize(im, (head.shape[1], head.shape[0]), interpolation=cv2.INTER_AREA)
        hf = head.copy(); hf[FACE_CUT_Y:, :, 3] = 0           # what the face was drawn from (no neck)
        im[FACE_CUT_Y + 40:, :, 3] = 0 if False else im[FACE_CUT_Y + 40:, :, 3]
        M = box_fit(im, hf)                                # the redraw's head box on the head's, then ECC
        im = cv2.warpAffine(im, M, (head.shape[1], head.shape[0]), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
        E = np.eye(2, 3, dtype=np.float32)
        try:
            _, E = cv2.findTransformECC(RP.over(hf).astype(np.float32), RP.over(im).astype(np.float32), E, cv2.MOTION_EUCLIDEAN,
                                        (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), None, 5)
            if abs(E[0, 2]) < 30 and abs(E[1, 2]) < 30:
                im = cv2.warpAffine(im, E, (head.shape[1], head.shape[0]), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                                    borderValue=(0, 0, 0, 0))
        except cv2.error:
            pass
        score = float(np.abs(RP.over(im).astype(np.float32) - RP.over(hf).astype(np.float32))[hf[..., 3] > 200].mean())
        im[..., 3] *= (ndimage.binary_dilation(head[..., 3] > 20, iterations=6)).astype(np.float32)   # nothing outside the head
        ramp = np.clip((np.arange(im.shape[0], dtype=np.float32) - (FACE_CUT_Y - 14)) / 14, 0, 1)[:, None, None]
        im = im * (1 - ramp) + head * ramp                 # the neck and collar are the neutral head's
        up = RP.esrgan_x4(im)
        Wp, Hp = meta["size"]
        pm = up.copy()
        pm[..., :3] *= pm[..., 3:4] / 255.
        sm = cv2.resize(pm, (Wp, Hp), interpolation=cv2.INTER_AREA)
        al = sm[..., 3:4].clip(0, 255)
        sm[..., :3] = np.where(al > 1, sm[..., :3] * 255. / np.maximum(al, 1), 0)
        ys, xs = np.nonzero(sm[..., 3] > 6)
        x0, y0, x1, y1 = max(0, xs.min() - 6), max(0, ys.min() - 6), min(Wp, xs.max() + 7), min(Hp, ys.max() + 7)
        Image.fromarray(sm[y0:y1, x0:x1].clip(0, 255).astype(np.uint8), "RGBA").save(os.path.join(OUT, f"face_{f}.png"))
        meta["faces"][f] = {"box": [int(x0), int(y0), int(x1 - x0), int(y1 - y0)]}
        print(f"face {f:6s} mean diff {score:.1f} (scale {float(M[0, 0]):.3f})", flush=True)
    json.dump(meta, open(os.path.join(OUT, "parts.json"), "w"), indent=1)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "cut"
    names = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    RP.FIG = FIG
    if cmd == "cut":
        cut()
    elif cmd == "complete":
        with ThreadPoolExecutor(5) as ex:
            for r in ex.map(complete, names or ORDER):
                print(r, flush=True)
    elif cmd == "fit":
        fit(names or ORDER)
    elif cmd == "faces":
        head_full()
        with ThreadPoolExecutor(5) as ex:
            for r in ex.map(face, names or list(FACES)):
                print(r, flush=True)
    elif cmd == "fitfaces":
        fit_faces(names or list(FACES))
    elif cmd == "sheet":
        RP.OUT = OUT
        RP.sheet()
