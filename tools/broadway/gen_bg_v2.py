"""Backgrounds v2 (owner, 2026-11-22: "redo the background, it's way too chaotic and looks like AI").

v1 asked for a street full of signs and got a busy, generic picture. Here the composition is designed first: a flat
layout guide drawn in code (art/broadway-src/bg2/layout_<name>.png) fixes where every block goes - a straight-on row of
five storefronts (no vanishing-point street), big calm wall areas, a flat night sky with a simple skyline, a plain
pavement - and ONLY FOUR neon pieces (a guitar blade sign, a marquee canopy, one word sign, a neon boot). The image
model paints over that layout in the game's clean TV-animation style (uniform line weight, matte flat colour).
  layout            write the layout guides
  gen [name,..] [n] paint each over its guide (n takes)
  unlit / mobile    as gen_bg.py, from the pick (<name>_pick.png)
usage: python tools/broadway/gen_bg_v2.py layout|gen|unlit|mobile [street,roof] [n]"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg

ROOT = orimg.ROOT
SRC = os.path.join(ROOT, "art", "broadway-src")
D = os.path.join(SRC, "bg2")
MODEL = "openai/gpt-image-2.6-sunburst"
W, H = 1536, 864
STYLE = ("STYLE: a background painting from a professional American adult-animation TV show - clean, confident, UNIFORM "
         "black line weight, flat matte colours with one simple hard-edged shade, very few highlights, no glossy shine, no "
         "texture noise, no gradients except the sky, no tiny clutter, no random props. Calm, designed, readable at a "
         "glance, with large simple shapes and plenty of quiet areas. Consistent straight-on perspective. NOT busy, NOT "
         "chaotic, NOT photo-realistic, NOT a generic AI illustration.")


def layout_street():
    im = Image.new("RGB", (W, H), (22, 24, 64))
    d = ImageDraw.Draw(im)
    for y in range(0, 330):                                    # sky: navy to violet
        t = y / 330
        d.line([(0, y), (W, y)], fill=(int(20 + 40 * t), int(22 + 10 * t), int(62 + 40 * t)))
    d.ellipse([1290, 50, 1350, 110], fill=(250, 240, 200))     # moon
    for x0, x1, top in ((140, 230, 205), (230, 300, 240), (560, 640, 220), (640, 700, 150), (700, 770, 230),
                        (1010, 1090, 215), (1090, 1180, 245)):  # the distant skyline
        d.rectangle([x0, top, x1, 330], fill=(40, 44, 96))
    d.polygon([(655, 150), (662, 95), (669, 150)], fill=(40, 44, 96)); d.polygon([(675, 150), (682, 95), (689, 150)], fill=(40, 44, 96))
    fronts = [(0, 380, 262, (150, 52, 40)), (380, 640, 318, (214, 190, 150)), (640, 900, 298, (110, 46, 44)),
              (900, 1150, 330, (70, 120, 84)), (1150, W, 272, (156, 58, 44))]
    for x0, x1, top, col in fronts:                            # the storefronts, straight on
        d.rectangle([x0, top, x1, 690], fill=col, outline=(15, 15, 15), width=4)
        d.rectangle([x0, top, x1, top + 18], fill=tuple(int(c * .7) for c in col), outline=(15, 15, 15), width=3)
        for k in range(2):                                     # two rows of upper windows, lit amber
            y0 = top + 60 + k * 110
            if y0 + 70 > 540:
                continue
            n = max(2, (x1 - x0) // 95)
            for i in range(n):
                cx = x0 + (i + .5) * (x1 - x0) / n
                d.rectangle([cx - 22, y0, cx + 22, y0 + 70], fill=(255, 196, 92), outline=(15, 15, 15), width=3)
        d.rectangle([x0 + 20, 560, x1 - 20, 690], fill=(70, 40, 30), outline=(15, 15, 15), width=3)   # shopfront
        d.rectangle([x0 + 40, 580, x1 - 40, 670], fill=(255, 190, 90))
    # the four neon pieces
    d.rectangle([250, 330, 310, 540], fill=(30, 30, 60), outline=(255, 63, 164), width=6)           # guitar blade sign
    d.rectangle([410, 520, 610, 560], fill=(200, 160, 60), outline=(15, 15, 15), width=3)            # marquee canopy
    for i in range(10):
        d.ellipse([418 + i * 19, 530, 430 + i * 19, 542], fill=(255, 230, 120))
    d.rectangle([930, 380, 1120, 450], fill=(30, 30, 60), outline=(47, 168, 255), width=6)          # word sign
    d.rectangle([1250, 350, 1400, 520], fill=(30, 30, 60), outline=(255, 59, 59), width=6)          # neon boot
    for i in range(16):                                        # one string of party lights
        x = 40 + i * 92
        y = 300 + 22 * (1 - ((i % 8) / 3.5 - 1) ** 2)
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(255, 220, 120))
    d.rectangle([0, 690, W, 775], fill=(120, 110, 130), outline=(15, 15, 15), width=4)               # pavement
    d.rectangle([0, 775, W, H], fill=(48, 46, 70))                                                    # the road, flat
    for x in (120, 1420):                                      # two street lamps
        d.rectangle([x - 5, 560, x + 5, 760], fill=(20, 20, 30)); d.ellipse([x - 16, 540, x + 16, 572], fill=(255, 230, 170))
    return im


def layout_roof():
    im = Image.new("RGB", (W, H), (22, 24, 64))
    d = ImageDraw.Draw(im)
    for y in range(0, 560):
        t = y / 560
        d.line([(0, y), (W, y)], fill=(int(24 + 60 * t), int(20 + 18 * t), int(70 + 40 * t)))
    for x0, x1, top in ((80, 190, 380), (190, 260, 330), (300, 380, 400), (560, 650, 360), (650, 720, 250), (720, 800, 380),
                        (980, 1070, 340), (1070, 1160, 390), (1250, 1340, 350), (1340, 1440, 410)):
        d.rectangle([x0, top, x1, 560], fill=(46, 50, 104))
    d.polygon([(670, 250), (678, 180), (686, 250)], fill=(46, 50, 104)); d.polygon([(690, 250), (698, 180), (706, 250)], fill=(46, 50, 104))
    for cx, cy, r, col in ((300, 140, 70, (255, 63, 164)), (1180, 120, 80, (47, 168, 255)), (760, 80, 50, (255, 194, 58))):
        for k in range(12):                                    # three fireworks
            import math
            a = k / 12 * 6.283
            d.line([(cx + math.cos(a) * r * .3, cy + math.sin(a) * r * .3), (cx + math.cos(a) * r, cy + math.sin(a) * r)], fill=col, width=5)
    d.rectangle([0, 560, W, 600], fill=(150, 60, 50), outline=(15, 15, 15), width=4)                 # parapet
    d.rectangle([0, 600, W, H], fill=(150, 100, 60), outline=(15, 15, 15), width=4)                  # deck
    d.rectangle([40, 470, 330, 600], fill=(120, 80, 50), outline=(15, 15, 15), width=4)              # bandstand left
    d.rectangle([1200, 500, 1500, 610], fill=(120, 80, 50), outline=(15, 15, 15), width=4)           # bar right
    for i in range(16):
        x = 40 + i * 92
        y = 430 + 30 * (1 - ((i % 8) / 3.5 - 1) ** 2)
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(255, 220, 120))
    return im


PROMPTS = {
    "street": ("A wide landscape background for a slot game, painted over the attached LAYOUT GUIDE: keep every block "
               "exactly where the guide puts it and keep its calm, simple composition. Scene: LOWER BROADWAY in Nashville "
               "at night, seen straight on from across the street: a continuous row of five old two- to four-storey "
               "honky-tonk storefronts (red brick, cream brick, dark brick, green clapboard, red brick) with tall warm-lit "
               "windows and glowing shopfronts on the ground floor, a flat night sky (navy to violet) with a few small stars "
               "and a crescent moon, a simple distant skyline silhouette with one twin-spired tower, one string of round "
               "party bulbs across the top, a plain pavement with two iron street lamps, and the road in front. "
               "ONLY FOUR neon pieces, exactly where the guide's coloured outlines are: a tall vertical blade sign with a "
               "hot-pink neon guitar on the left building; a marquee canopy ringed with round amber bulbs over the cream "
               "building's door; one word sign reading HONKY TONK in electric-blue neon tubes on the green building; a big "
               "red neon cowboy boot on the right building. Each neon tube is a clean flat coloured stroke with a white "
               "core and a black outline, with a soft flat patch of its colour on the wall around it. No other signs, no "
               "other words, no people, no cars, no clutter. The middle third is the calmest part (a slot board covers it)."),
    "roof": ("A wide landscape background for a slot game, painted over the attached LAYOUT GUIDE: keep every block exactly "
             "where the guide puts it and keep its calm, simple composition. Scene: a rooftop honky-tonk stage high above "
             "Nashville at night during a celebration: a deep violet sky with three big flat cartoon fireworks (hot pink, "
             "electric blue, gold), the downtown skyline silhouette with lit windows and one twin-spired tower, a low red "
             "brick parapet, a warm wooden deck, a small wooden bandstand with amplifiers and a drum kit on the left (no "
             "people), a small barn-wood bar on the right, one string of round party bulbs. No words, no people, no "
             "clutter. The middle third is the calmest part (a slot board covers it)."),
}


def gen(job):
    name, k = job
    p = PROMPTS[name] + "\n\n" + STYLE
    refs = [os.path.join(D, f"layout_{name}.png"), os.path.join(SRC, "rosie2", "rosie_v2.png")]
    p += ("\nThe second attached picture is the game's main character, only as the reference for the drawing style and "
          "line weight - do NOT draw her in the scene.")
    out = os.path.join(D, f"{name}_{k}.png")
    try:
        _, c = orimg.generate(out, p, aspect="16:9", transparent=False, refs=refs, model=MODEL)
        return f"OK {out} {c}"
    except RuntimeError as e:
        return f"FAIL {out} {e}"


def edit(job):
    name, kind = job
    src = os.path.join(D, f"{name}_pick.png")
    if kind == "unlit":
        p = ("Redraw the attached picture EXACTLY - the same buildings, composition, shapes, outlines, colours and every "
             "detail in the same place - but with EVERY neon sign, neon tube, marquee bulb and party bulb SWITCHED OFF: "
             "the neon tubes become dull unlit glass (greyish pastel versions of their colours, no white core), the "
             "bulbs pale grey unlit glass, and the flat coloured light patches they threw on the walls are gone. The "
             "windows, shopfronts, street lamps, moon, stars and skyline stay exactly as they are. No other changes.")
        out, aspect = os.path.join(D, f"{name}_unlit.png"), "16:9"
    else:
        p = ("Redraw the attached slot game background as a TALL PORTRAIT picture (2:3) for phones: the same place, the "
             "same clean TV-animation style, colours, buildings and neon pieces, recomposed for a tall screen: the sky and "
             "skyline at the top, the storefronts and their neon in the middle, the pavement and road at the bottom. Keep "
             "it calm and simple, no extra signs, no words other than those already there, no people.")
        out, aspect = os.path.join(D, f"{name}_mobile.png"), "2:3"
    try:
        _, c = orimg.generate(out, p, aspect=aspect, transparent=False, refs=[src], model=MODEL)
        return f"OK {out} {c}"
    except RuntimeError as e:
        return f"FAIL {out} {e}"


if __name__ == "__main__":
    os.makedirs(D, exist_ok=True)
    cmd = sys.argv[1]
    names = sys.argv[2].split(",") if len(sys.argv) > 2 else ["street", "roof"]
    if cmd == "layout":
        layout_street().save(os.path.join(D, "layout_street.png"))
        layout_roof().save(os.path.join(D, "layout_roof.png"))
        print("layouts written")
    elif cmd == "gen":
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        with ThreadPoolExecutor(4) as ex:
            for r in ex.map(gen, [(nm, k) for nm in names for k in range(1, n + 1)]):
                print(r, flush=True)
    else:
        with ThreadPoolExecutor(4) as ex:
            for r in ex.map(edit, [(nm, cmd) for nm in names]):
                print(r, flush=True)
