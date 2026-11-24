"""Power Outage: the lobby covers for engine.io's Media page - 16:9 (3840x2160) and 3:4 (3072x4096).

The image model paints the key art WITHOUT any text (no title either: the owner wants NO text on the covers; the President, his bodyguard and the bankrupt CEO in the
blacked-out office, symbols flying, a lightning flash), from the game's own art as references; the real POWER OUTAGE
logo (frontend/assets/title_logo.webp) is laid over it here, so the title is crisp and spelled right.
usage: python tools/broadway/gen_covers.py gen | build
-> art/broadway-src/covers/<aspect>_raw.png, media/cover_16x9.png, media/cover_3x4.png (+ .jpg copies)"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg, upscale4k

ROOT = orimg.ROOT
SRC = os.path.join(ROOT, "art", "broadway-src")
OUT = os.path.join(SRC, "covers")
MEDIA = os.path.join(ROOT, "media")
REFS = [os.path.join(SRC, n) for n in ("H1_v1.png", "H2_v1.png", "H3_v1.png", "bg_v1.png")]
SCENE = ("Key art for a slot game's lobby cover, NO text, NO letters, NO logo, NO words anywhere. Original characters only "
         "(the ones in the attached pictures) - no characters from any existing show, film or game, no real logos, no seals. "
         "Scene: inside the dark oval presidential office during a total power blackout (the attached background), drawn "
         "in exactly the attached pictures' flat adult-animation sitcom cartoon style - thick clean black outlines, flat "
         "solid colours with one hard shadow shape, no realistic lighting, no glow haze. In the middle the attached "
         "blond president caricature in his navy suit and long red tie, holding up a candle and glaring, comically outraged; "
         "beside him the attached bodyguard with sunglasses shining a flashlight; the attached bankrupt CEO in his barrel "
         "peeking in, sweating. Around them flying cartoon objects from the game: a red rotary phone, a cracked light bulb, "
         "a dead red battery, a broke pink piggy bank, a computer monitor with a red arrow crashing down, cash bills and gold "
         "coins, chunky yellow lightning bolts. A big flat lightning flash in the window behind. Funny dark-comedy energy, "
         "bold readable shapes, punchy colours (navy, candle yellow, red, electric cyan).")
JOBS = {
    "16x9": (SCENE + " Wide landscape composition: the characters in the middle and right two thirds, LEAVE THE UPPER-LEFT "
             "THIRD calmer and darker (a title logo will be placed there).", "16:9", (3840, 2160)),
    "3x4": (SCENE + " Tall portrait composition: the characters in the lower two thirds, LEAVE THE TOP THIRD calmer and darker "
            "(a title logo will be placed there).", "3:4", (3072, 4096)),
}


def gen(name):
    p, aspect, _ = JOBS[name]
    try:
        _, c = orimg.generate(os.path.join(OUT, name + "_raw.png"), p, aspect=aspect, refs=REFS, transparent=False)
        return f"OK {name} {c}"
    except RuntimeError as e:
        return f"FAIL {name} {e}"


def build(name):
    _, _, size = JOBS[name]
    raw = Image.open(os.path.join(OUT, name + "_raw.png")).convert("RGBA")
    big = upscale4k.up4(raw, size=size).convert("RGBA")
    W, H = size
    # owner, 2026-11-18: the covers carry NO text at all (the lobby shows the title itself) - the logo is opt-in only
    if os.environ.get("COVER_LOGO") != "1":
        return save(big.convert("RGB"), name, W, H)
    logo = Image.open(os.path.join(ROOT, "frontend", "assets", "title_logo.webp")).convert("RGBA")
    lw = round(W * (.36 if name == "16x9" else .86))
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    bb = logo.getbbox()
    logo = logo.crop(bb)
    x = round(W * .035) if name == "16x9" else (W - logo.width) // 2
    y = round(H * .05) if name == "16x9" else round(H * .035)
    # a soft dark pool under the logo so it reads over any part of the painting
    sh = Image.new("RGBA", big.size, (0, 0, 0, 0))
    a = logo.getchannel("A").filter(ImageFilter.MaxFilter(9))
    pool = Image.new("RGBA", logo.size, (6, 8, 22, 200))
    pool.putalpha(a)
    sh.alpha_composite(pool, (x, y + round(H * .008)))
    sh = sh.filter(ImageFilter.GaussianBlur(W * .012))
    big.alpha_composite(sh)
    big.alpha_composite(logo, (x, y))
    return save(big.convert("RGB"), name, W, H)


def save(rgb, name, W, H):
    os.makedirs(MEDIA, exist_ok=True)
    rgb.save(os.path.join(MEDIA, f"cover_{name}.png"), optimize=True)
    rgb.save(os.path.join(MEDIA, f"cover_{name}.jpg"), quality=92)
    rgb.resize((W // 4, H // 4), Image.LANCZOS).save(os.path.join(OUT, f"_{name}_preview.jpg"), quality=85)
    return f"built {name} {(W, H)}"


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1] == "gen":
        with ThreadPoolExecutor(2) as ex:
            for r in ex.map(gen, JOBS):
                print(r, flush=True)
    else:
        for n in JOBS:
            print(build(n), flush=True)
