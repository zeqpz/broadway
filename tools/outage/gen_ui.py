"""Power Outage: generate the UI art (art/outage-src/ui/<name>.png) and fit each onto the size the game draws it at
(frontend/assets/<path>, the same file names as Voodoo on Bourbon so the code needs no change).
Every job gets the President symbol (H1) as its style reference; the frame, signs and cards also get a crop of the
owner's reference screenshots, for chunkiness only.
usage: python tools/outage/gen_ui.py gen [name,..]     (OpenRouter, ~$0.06 each)
       python tools/outage/gen_ui.py fit [name,..]     (no API; reads the 4K masters from tools/outage/upscale4k.py ui)"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg

ROOT = orimg.ROOT
RAW = os.path.join(ROOT, "art", "outage-src", "ui")
SRC = os.path.join(ROOT, "art", "outage-src", "4k", "ui")
ASSETS = os.path.join(ROOT, "frontend", "assets")
PR = os.path.join(ROOT, "art", "outage-src", "prompts")
REF_SYM = os.path.join(ROOT, "art", "outage-src", "H1_v1.png")
REF_FRAME = os.path.join(PR, "style_ref_frame.png")
REF_CARD = os.path.join(PR, "style_ref_card.png")
STYLE = ("Art style: classic adult-animation sitcom cartoon crossed with a chunky casual slot game UI - clean uniform thick "
         "BLACK outlines, FLAT solid colours with one hard-edged darker shadow shape per colour, one small simple white "
         "highlight on shiny parts, simple rounded chunky shapes, no gradients, no glow haze, no realistic lighting, crisp "
         "clean vector cartoon. Blackout palette: midnight navy #141B33, deep blue #22305A, slate blue #3A4A7A, candle yellow "
         "#FFD54A, warm orange #FF9A3C, presidential red #D7263D, steel grey #8A93A6, off-white #F4F1E8, gold #E8B23A, "
         "electric cyan #3FE0FF, black #111111. Original design: no logos, no brands, no seals, no characters from any "
         "existing show or game. Transparent background.")
REFNOTE = ("The FIRST attached picture is a symbol from this same game: match its outline weight and flat colouring exactly. "
           "Any OTHER attached picture is only a reference from a different game for chunkiness: do not copy its objects, "
           "colours, wood, chains or layout.")
LETTER = ("big fat chunky cartoon letters, bouncy with a slight tilt, FLAT candle-yellow fill with a hard orange shadow shape "
          "on the lower half of every letter, a thick black outline, one small white highlight on each letter")
METAL = ("chunky cartoon grey steel bars with round rivets, like the casing of an electrical breaker panel, a thick black "
         "outline, flat steel grey with one hard darker shade")
CARD = ("an off-white (#F4F1E8) card with big rounded corners, a thick black outline and a flat darker shade along its lower edge; "
        "its face is ONE flat plain colour, perfectly empty - no smudges, no shading blobs, no placeholder marks")
S, F, C = [REF_SYM], [REF_SYM, REF_FRAME], [REF_SYM, REF_CARD]
JOBS = {
    "frame": (f"A chunky cartoon picture frame for a 5x5 slot machine reel board, seen straight on, made of {METAL}: yellow-and-"
              "black hazard stripes along the bottom bar, a big red breaker lever switch bolted to the right side bar (flipped "
              "down to OFF), a tangle of black and red electric cables spilling over the top-left corner, an unplugged power "
              "cord with a two-prong plug dangling from the bottom-right corner, a frayed wire spitting a flat yellow spark at "
              "the top-right corner. The inside of the frame is a big rectangular opening that is COMPLETELY EMPTY and "
              "TRANSPARENT (cut out), the frame border fairly thin compared to the opening, symmetrical rectangular shape.",
              "1:1", "frame.webp", (2200, 1982), "stretch", F),
    "logo_sign": ('A chunky cartoon sign board hanging by two short wires: a dark wooden plank sign with a thick black outline, a '
                  'big cartoon light bulb on its top-right corner that is cracked and sputtering, with the game title "POWER" '
                  '(top line) and "OUTAGE" (bottom line) on it in ' + LETTER + ', the last two letters of OUTAGE dimmer and '
                  'greyer as if they are going out. Only those two words.', "4:3", "logo_sign.webp", (1200, 900), "contain", F),
    "wordmark": ('The game title logo "POWER OUTAGE": "POWER" on top in ' + LETTER + ' with a chunky lightning bolt cracking '
                 'through the O, "OUTAGE" below, bigger, in the same letters but going dark one letter at a time from left to '
                 'right (the last letters flat grey and unlit), a cut power cord with a plug curling under the words, a few flat '
                 'yellow sparks. Only those two words, nothing else written.', "21:9", "intro_wordmark.webp", (2736, 1160), "contain", S),
    "title_logo": ('The game title logo "POWER OUTAGE": "POWER" on top in ' + LETTER + ' with a chunky lightning bolt cracking '
                   'through the O, "OUTAGE" below, bigger, in the same letters but going dark one letter at a time from left to '
                   'right (the last letters flat grey and unlit), a cut power cord with a plug curling under the words, a few flat '
                   'yellow sparks. Only those two words, nothing else written.', "16:9", "title_logo.webp", (2400, 1279), "contain", S),
    "big_win": (f'The words "BIG WIN" as a game headline: {LETTER}, a few flat yellow spark zig-zags round it. Nothing else.',
                "21:9", "big_win.webp", (1800, 370), "contain", S),
    "mega_win": (f'The words "MEGA WIN" as a game headline: {LETTER}, extra excited, flat cartoon cash bills and coins flying '
                 'round it.', "21:9", "mega_win.webp", (1800, 374), "contain", S),
    "xtreme_win": ('The words "XTREME WIN" as a game headline: big fat chunky bouncy cartoon letters, FLAT electric-cyan fill with a '
                   'hard deep-blue shadow shape on the lower half, a thick black outline, white highlights, big flat yellow '
                   'lightning bolts striking behind the letters, the most intense version. Nothing else written.',
                   "21:9", "xtreme_win.webp", (1800, 402), "contain", S),
    "total_win": (f'The words "TOTAL WIN" as a game headline: {LETTER}, set on a curved flat red ribbon banner with a black outline.',
                  "21:9", "total_win.webp", (1800, 508), "contain", S),
    "tier_bg": (f"A wide horizontal sign board for a game headline made of {METAL}, yellow-and-black hazard stripes along its top "
                "and bottom edges, EMPTY dark navy face in the middle (no text).", "21:9", "tier_bg.webp", (1980, 559), "stretch", F),
    "total_bg": (f"A wide horizontal plate for showing a win amount: {CARD}, a slightly darker inset panel in the middle (empty, "
                 "no text), a candle-yellow border band all round it.", "21:9", "total_bg.webp", (1800, 560), "stretch", C),
    "digits": ('A 4 by 3 grid of separate game number glyphs on a transparent background, one glyph centred in each cell with '
               'plenty of space between: top row "0 1 2 3", middle row "4 5 6 7", bottom row "8 9 , ." - chunky bouncy cartoon '
               'numerals, FLAT candle-yellow fill with a hard orange shadow shape on the lower half, a thick black outline, one '
               'small white highlight, the same size and style for all.', "1:1", None, None, "digits", S),
    "bonus_btn_bg": ("A game button: a rounded rectangular big red emergency-button panel, flat red with a hard darker red shade "
                     "along the bottom, a thick black outline, a flat white highlight stripe along the top, EMPTY face (no text).",
                     "3:2", "bonus_btn_bg.webp", (950, 610), "stretch", S),
    "bonus_btn_text": ('The word "BONUS" as a game logo: big fat chunky bouncy cartoon letters, FLAT candle-yellow fill with a hard '
                       'orange shadow shape, a thick black outline, white highlights, stacked big and bold. Only that word.',
                       "3:2", "bonus_btn_text.webp", (1140, 759), "contain", S),
    "xbonus_text": ('The words "XTREME" (smaller, on top, flat electric cyan with a deep-blue shade) and "BONUS" (big, below, flat '
                    'candle yellow with an orange shade) as a game logo: chunky bouncy cartoon letters, thick black outlines, '
                    'white highlights, a flat yellow lightning bolt striking the X. Only those two words.',
                    "1:1", "xbonus_text.webp", (1065, 897), "contain", S),
    "bonus_panel": (f"A big landscape game menu panel: {CARD} (EMPTY, no text), a wide flat candle-yellow header strip across the "
                    "top (empty), a dark navy outer border band, a couple of black electric cables curling over the top corners.",
                    "3:2", "bonus_panel.webp", (2250, 1510), "stretch", C),
    "feature_box": (f"A tall portrait game info card: {CARD} (EMPTY, no text), a flat candle-yellow header strip across the top "
                    "(empty), a dark navy border band.", "3:4", "feature_box.webp", (840, 1074), "stretch", C),
    "info_panel": ("A tall portrait game rules panel: a very dark navy panel (#141B33) with big rounded corners (EMPTY, no text), a "
                   "thick black outline, a thin candle-yellow border band and round steel rivets at the corners; its face ONE flat plain colour, perfectly empty, no smudges.",
                   "3:4", "info_panel.webp", (1600, 2034), "stretch", S),
    "banner_box": (f"A wide horizontal small sign plate for a game message banner (EMPTY dark navy face, no text), made of {METAL}, "
                   "hanging from two short wires.", "21:9", "banner_box.webp", (1440, 582), "stretch", F),
    "board_bg": ("A square, completely OPAQUE background panel for the inside of a 5x5 slot machine reel board - no frame, no border, "
                 "no outline, no text, no symbols, no objects - an edge-to-edge texture filling the whole canvas: flat dark "
                 "midnight-navy wallpaper (#161D38) with very subtle, low-contrast, slightly darker vertical stripes, the outer edges "
                 "gently darker. Calm, dark and even so bright cartoon symbols on top stay perfectly readable. No transparency.",
                 "1:1", None, None, "raw", []),
}


def gen(name):
    p, aspect = JOBS[name][0], JOBS[name][1]
    refs = JOBS[name][5]
    body = p + ("\n\n" + REFNOTE if refs else "") + "\n\n" + (STYLE if name != "board_bg" else
                                                                STYLE.replace(" Transparent background.", ""))
    try:
        _, c = orimg.generate(os.path.join(RAW, name + ".png"), body, aspect=aspect, refs=refs,
                              transparent=name != "board_bg")
        return f"OK {name} {c}"
    except RuntimeError as e:
        return f"FAIL {name} {e}"


def trim(im):
    a = np.asarray(im.getchannel("A"))
    a = np.where(a > 12, a, 0).astype(np.uint8)
    im.putalpha(Image.fromarray(a))
    bb = im.getchannel("A").getbbox()
    return im.crop(bb) if bb else im


def fit(name):
    _, _, path, size, mode, _ = JOBS[name]
    if mode == "raw":
        return f"skip {name} (raw)"
    im = Image.open(os.path.join(SRC, name + ".png")).convert("RGBA")
    if mode == "digits":
        return fit_digits(im)
    im = trim(im)
    W, H = size
    if mode == "stretch":
        out = im.convert("RGBa").resize(size, Image.LANCZOS).convert("RGBA")
    else:
        k = min(W / im.width, H / im.height) * .98
        sm = im.convert("RGBa").resize((round(im.width * k), round(im.height * k)), Image.LANCZOS).convert("RGBA")
        out = Image.new("RGBA", size, (0, 0, 0, 0))
        out.alpha_composite(sm, ((W - sm.width) // 2, (H - sm.height) // 2))
    out.save(os.path.join(ASSETS, path), "WEBP", quality=90, alpha_quality=100, method=6)
    return f"fit {name} -> {path} {size}"


def fit_digits(im):
    """Cut the 4x3 glyph sheet into num/0..9, comma, dot at 343 px tall (the old glyph height)."""
    names = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "comma", "dot"]
    W, H = im.size
    cw, ch = W / 4, H / 3
    glyphs = []
    for i, n in enumerate(names):
        glyphs.append((n, im.crop((round((i % 4) * cw), round((i // 4) * ch), round((i % 4 + 1) * cw), round((i // 4 + 1) * ch)))))
    hs = [trim(c.copy()).height for n, c in glyphs[:10]]
    k = 330 / max(hs)
    out_dir = os.path.join(ASSETS, "num")
    existing = {os.path.splitext(f)[0]: f for f in os.listdir(out_dir)}
    for n, c in glyphs:
        a = np.asarray(c.getchannel("A"))
        ys = np.nonzero(a.max(1) > 12)[0]
        xs = np.nonzero(a.max(0) > 12)[0]
        if not len(xs):
            continue
        g = c.crop((xs.min(), 0, xs.max() + 1, c.height))
        g = g.crop((0, ys.min() if n not in ("comma", "dot") else 0, g.width, c.height if n in ("comma", "dot") else ys.max() + 1))
        g = trim(g) if n not in ("comma", "dot") else g
        gs = g.convert("RGBa").resize((max(2, round(g.width * k)), max(2, round(g.height * k))), Image.LANCZOS).convert("RGBA")
        if n in ("comma", "dot"):
            gs = trim(gs)
            canvas = Image.new("RGBA", (gs.width + 14, 343), (0, 0, 0, 0))
            canvas.alpha_composite(gs, (7, 343 - gs.height - 6))
        else:
            canvas = Image.new("RGBA", (gs.width + 14, 343), (0, 0, 0, 0))
            canvas.alpha_composite(gs, (7, (343 - gs.height) // 2))
        canvas.save(os.path.join(out_dir, existing.get(n, n + ".webp")), "WEBP", quality=92, alpha_quality=100, method=6)
    return "fit digits -> num/ " + ", ".join(sorted(existing))


if __name__ == "__main__":
    step = sys.argv[1]
    names = sys.argv[2].split(",") if len(sys.argv) > 2 else list(JOBS)
    os.makedirs(RAW, exist_ok=True)
    if step == "gen":
        with ThreadPoolExecutor(6) as ex:
            for r in ex.map(gen, names):
                print(r, flush=True)
    else:
        for n in names:
            print(fit(n))
