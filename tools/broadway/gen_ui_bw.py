"""Broadway on Nashville: generate the UI art (art/broadway-src/ui/<name>.png) and fit each onto the size the game draws
it at (frontend/assets/<path>: the same file names as Power Outage, so the code needs no change).
Kept from Power Outage on purpose (owner): the HUD, the bonus buy menu (its panel, buttons and layout - only the
banner pictures inside it are re-themed) and the black-and-white SMUKIEZ introduction; the cream feature cards too.
usage: python tools/broadway/gen_ui_bw.py gen [name,..]    (OpenRouter, ~$0.06 each)
       python tools/broadway/gen_ui_bw.py fit [name,..]    (reads the 4K masters from tools/broadway/upscale4k.py ui)"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg
import gen_ui as G                                   # trim / fit_digits / the fit modes

ROOT = orimg.ROOT
SRC = os.path.join(ROOT, "art", "broadway-src")
RAW = os.path.join(SRC, "ui")
MODEL = "openai/gpt-image-2.6-sunburst"
SYM = lambda s: os.path.join(SRC, s + "_v1.png")
STYLE = ("Art style: an American adult-animation TV cartoon crossed with a premium casual slot game UI - clean uniform thick "
         "BLACK outlines, FLAT solid colours with one hard-edged darker shade per colour, small simple white highlights on "
         "shiny parts, chunky readable shapes with rich cartoon detail, no gradients, no glow haze, no realistic lighting, "
         "crisp clean vector cartoon. Palette (Lower Broadway, Nashville, at night): night navy #12163A, deep indigo #241E5C, "
         "neon hot pink #FF3FA4, neon electric blue #2FA8FF, neon red #FF3B3B, marquee amber #FFC23A, gold #E8B23A, "
         "rhinestone white #F7F4FF, honky-tonk wood #8A5A33, dark walnut #4A2C18, brass #C9A040, boot red #C8282E, "
         "black #111111. Original design: no logos, no brands, no real business names, no characters from any existing "
         "show or game. Transparent background.")
REFNOTE = ("The attached picture is a symbol from this same game: match its outline weight, flat colouring and level of "
           "detail exactly - but do not draw it unless asked.")
LETTER = ("big fat chunky rodeo-poster slab-serif letters with a slight bounce, FLAT marquee-gold fill (#FFC23A) with a hard "
          "red-orange shade on the lower half of every letter, a thick black outline, a thin hot-pink neon stroke running "
          "round the outside of the black outline, one small white highlight on each letter")
WOOD = ("chunky cartoon polished dark-walnut wood planks with brass corner plates and round brass studs, a thick black "
        "outline, flat wood colour with one hard darker shade and a few simple grain lines")
BULBS = "a row of round glowing amber marquee light bulbs set evenly along it, each bulb a flat bright circle with a white highlight"
NUMS = ("glowing NEON-TUBE numerals: each glyph drawn as one thick flat neon tube in hot pink (#FF3FA4) with a bright white "
        "core line running down the middle of the tube and a thick black outline round the tube, all the same size and "
        "style, chunky and very readable")
JOBS = {   # name: (prompt, aspect, asset path, size, fit mode, refs)
    "frame": (f"A chunky cartoon HONKY-TONK STAGE frame for a 5x5 slot machine reel board, seen straight on: a rectangular "
              f"frame of {WOOD}, with {BULBS} running all the way round the frame on all four sides, a thin hot-pink neon "
              "tube running round the inner edge of the frame, a small gold star on each corner plate. The inside of the "
              "frame is a big rectangular opening that is COMPLETELY EMPTY and TRANSPARENT (cut out), the frame border "
              "fairly thin compared to the opening, a perfectly symmetrical rectangle, nothing hanging off it.",
              "1:1", "frame.webp", (2200, 1982), "stretch", [SYM("H1")]),
    "logo_sign": ('A big cartoon NEON SIGN for the game title, mounted on a dark navy metal backing board with a black outline '
                  'and rivets: the words "BROADWAY" (big, top line) and "ON NASHVILLE" (smaller, bottom line) spelled in '
                  'glowing NEON TUBES drawn as flat cartoon shapes - hot-pink tubes for BROADWAY, electric-blue tubes for ON '
                  'NASHVILLE, each tube a flat colour with a bright white core line and a black outline - a neon gold star '
                  'and a small neon guitar beside the words, a row of amber marquee bulbs round the board\'s edge. The light '
                  'is ONLY in the tubes (flat colours), no glow painted on the board. Only those words.',
                  "4:3", None, None, "raw", [SYM("BS")]),   # sign_layers_bw.py cuts the sign
    "title_logo": ('The game title logo "BROADWAY ON NASHVILLE": "BROADWAY" big on top in ' + LETTER + ', with "ON NASHVILLE" '
                   'below it smaller in glowing electric-blue neon-tube letters (flat tubes with white cores and black '
                   'outlines); a gold cowboy hat tipped on the B, a red electric guitar crossing behind the words, a few gold '
                   'stars. Only those words, nothing else written.', "16:9", "title_logo.webp", (2400, 1279), "contain", [SYM("H1")]),
    "big_win": (f'The words "BIG WIN" as a game headline: {LETTER}, a few flat gold stars round it. Nothing else.',
                "21:9", "big_win.webp", (1800, 370), "contain", [SYM("H1")]),
    "mega_win": (f'The words "MEGA WIN" as a game headline: {LETTER}, extra excited, flat cartoon music notes, gold stars and '
                 'cash bills flying round it.', "21:9", "mega_win.webp", (1800, 374), "contain", [SYM("H1")]),
    "xtreme_win": ('The words "XTREME WIN" as a game headline: big fat chunky rodeo-poster slab-serif letters, FLAT neon '
                   'electric-blue fill with a hard deep-indigo shade on the lower half, a thick black outline, white highlights, '
                   'big flat gold fireworks bursting behind the letters, the most intense version. Nothing else written.',
                   "21:9", "xtreme_win.webp", (1800, 402), "contain", [SYM("ES")]),
    "total_win": (f'The words "TOTAL WIN" as a game headline: {LETTER}, set on a curved flat red ribbon banner with a black '
                  'outline and gold stars on its ends.', "21:9", "total_win.webp", (1800, 508), "contain", [SYM("H1")]),
    "tier_bg": (f"A wide horizontal sign board for a game headline made of {WOOD}, {BULBS} along its top and bottom edges, an "
                "EMPTY dark navy face in the middle (no text).", "21:9", "tier_bg.webp", (1980, 559), "stretch", [SYM("H1")]),
    "total_bg": ("A wide horizontal plate for showing a win amount: a cream (#F4EBD8) tooled-leather panel with big rounded "
                 "corners, a thick black outline, a twisted gold rope border running all round it, a slightly darker inset "
                 "panel in the middle that is EMPTY (no text), flat colours, perfectly clean face.",
                 "21:9", "total_bg.webp", (1800, 560), "stretch", [SYM("H6")]),
    "digits": ('A 4 by 3 grid of separate game number glyphs on a transparent background, one glyph centred in each cell with '
               'plenty of space between: top row "0 1 2 3", middle row "4 5 6 7", bottom row "8 9 , ." - chunky rodeo-poster '
               'slab-serif numerals, FLAT marquee-gold fill with a hard red-orange shade on the lower half, a thick black '
               'outline, one small white highlight, the same size and style for all.', "1:1", None, None, "digits", [SYM("H1")]),
    "bonus_btn_bg": ("A game button: a rounded rectangular panel of polished dark-walnut wood with a brass rim and four brass "
                     "studs, flat colours with a hard darker shade along the bottom, a thick black outline, a flat white "
                     "highlight along the top, EMPTY face (no text).", "3:2", "bonus_btn_bg.webp", (950, 610), "stretch", [SYM("H7")]),
    "bonus_btn_text": ('The word "BONUS" as a game logo: ' + LETTER + ', stacked big and bold. Only that word.',
                       "3:2", "bonus_btn_text.webp", (1140, 759), "contain", [SYM("H1")]),
    "xbonus_text": ('The words "XTREME" (smaller, on top, in glowing electric-blue neon-tube letters with white cores and black '
                    'outlines) and "BONUS" (big, below, in ' + LETTER + ') as a game logo, a flat gold firework burst behind '
                    'the X. Only those two words.', "1:1", "xbonus_text.webp", (1065, 897), "contain", [SYM("ES")]),
    "banner_box": (f"A wide horizontal small sign plate for a game message banner: an EMPTY dark navy face (no text) framed by "
                   f"{WOOD}, {BULBS} along its top edge.", "21:9", "banner_box.webp", (1440, 582), "stretch", [SYM("H1")]),
    "board_bg": ("A square, completely OPAQUE background panel for the inside of a 5x5 slot machine reel board - no frame, no "
                 "border, no outline, no text, no symbols, no objects - an edge-to-edge texture filling the whole canvas: a "
                 "deep night-navy (#151A3E) velvet stage curtain with soft, very low-contrast vertical folds drawn as flat "
                 "slightly darker bands, the outer edges gently darker. Calm, dark and even so bright cartoon symbols on top "
                 "stay perfectly readable. No transparency.", "1:1", None, None, "raw", []),
    "bonus_icon": ('A chunky cartoon game button emblem for opening the bonus shop, seen straight on: a small glowing retro '
                   'jukebox top with chrome trim and coloured bubble tubes, a red electric guitar leaning across it, gold '
                   'stars, and the word "BONUS" across the bottom in ' + LETTER + '. A compact roughly square emblem.',
                   "1:1", "bonus_icon.webp", (640, 640), "contain", [SYM("ES")]),
    "vnum": ('A 4 by 3 grid of separate game glyphs on a transparent background, one glyph centred in each cell with plenty of '
             'space between: top row "x 0 1 2", middle row "3 4 5 6", bottom row "7 8 9 ." (a small lowercase multiplication '
             'x, the ten digits and a full stop) - ' + NUMS + '.', "1:1", None, None, "raw", [SYM("BS")]),
    "banner_fs": ("A wide game bonus banner illustration (no text, no letters): the attached FS marquee-star symbol big in the "
                  "middle, on a flat night-navy background with flat pink and gold spotlight rays bursting out behind it, "
                  "flat music notes and stars; framed by a chunky rounded black outline. Fill the whole picture.",
                  "16:9", None, None, "banner", [SYM("BS")]),
    "banner_xfs": ("A wide game bonus banner illustration (no text, no letters): the attached XFS jukebox symbol big in the "
                   "middle, on a flat night-navy rooftop background with big flat gold, pink and blue fireworks bursting behind "
                   "it; framed by a chunky rounded black outline. Fill the whole picture.", "16:9", None, None, "banner", [SYM("ES")]),
    "banner_boost": ("A wide game bonus banner illustration (no text, no letters): a big chunky cartoon guitar amplifier with "
                     "its volume knob cranked all the way up, sound waves and music notes blasting out of it, a red electric "
                     "guitar plugged in, gold stars, on a flat night-navy background; framed by a chunky rounded black "
                     "outline. Fill the whole picture.", "16:9", None, None, "banner", [SYM("H7")]),
}


def gen(name):
    p, aspect, _, _, mode, refs = JOBS[name]
    note = REFNOTE.replace("but do not draw it unless asked", "and draw that same symbol") if name in ("banner_fs", "banner_xfs") else REFNOTE
    style = STYLE if mode not in ("raw", "banner") or name == "vnum" else STYLE.replace(" Transparent background.", "")
    body = p + ("\n\n" + note if refs else "") + "\n\n" + style
    try:
        _, c = orimg.generate(os.path.join(RAW, name + ".png"), body, aspect=aspect, refs=refs, model=MODEL,
                              transparent=mode not in ("raw", "banner") or name == "vnum")
        return f"OK {name} {c}"
    except RuntimeError as e:
        return f"FAIL {name} {e}"


def fit(name):
    p, aspect, path, size, mode, refs = JOBS[name]
    if mode == "banner":
        im = Image.open(os.path.join(RAW, name + ".png")).convert("RGB").resize((1440, 810), Image.LANCZOS)
        im.save(os.path.join(G.ASSETS, "bonus", name + ".webp"), "WEBP", quality=88, method=6)
        return f"fit {name}"
    if mode == "raw":
        return f"skip {name} (raw: board_back.py / vnum.py)"
    G.JOBS[name] = (p, aspect, path, size, mode, refs)
    return G.fit(name)


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
