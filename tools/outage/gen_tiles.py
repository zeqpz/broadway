"""Power Outage: the engine.io lobby tiles (Media Editor), built from SEPARATE layers as Engine requires.

Engine review, 2026-11-19: "both the 3:4 and 16:9 game tiles should contain separate background and foreground
elements" and "the backgrounds of both tiles are too dark". The Media Editor composes a tile from
  background  - "an environmental background that shows the world of the game ... bright images and vibrant colours"
                (no characters, no wording, no multipliers)
  foreground  - "a feature character or key item ... focus on one key element and enlarge it to fill the key focus
                area" (transparent)
  + Engine's own gradient and title text, so neither layer carries any text (owner rule too: no text on lobby art).

usage: python tools/outage/gen_tiles.py gen [bg16 bg34 fg ...] | build | check
  gen    -> art/outage-src/tiles/<job>_<n>_raw.png (the image model, refs = the game's own art)
  build  -> media/tiles/bg_16x9.png (3840x2160), bg_3x4.png (2400x3200), fg_president.png (transparent, 2048 tall)
            from the picks in PICKS, plus frontend/tiles/*.webp copies the editor's "Game files" picker can load
  check  -> the perceived brightness of each background (Engine's editor warns below ~40 %)"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageStat
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg

ROOT = orimg.ROOT
SRC = os.path.join(ROOT, "art", "outage-src")
OUT = os.path.join(SRC, "tiles")
MEDIA = os.path.join(ROOT, "media", "tiles")
FRONT = os.path.join(ROOT, "frontend", "tiles")

STYLE = ("Drawn in exactly the attached pictures' flat adult-animation sitcom cartoon style: thick clean black outlines, "
         "flat solid colours with one hard shadow shape, crisp and simple, no realistic lighting, no blur, no photo "
         "texture. NO text, NO letters, NO numbers, NO logo, NO words, NO seal anywhere.")
ROOM = ("A lobby-tile BACKGROUND (environment only - NO people, NO characters, NO faces) for a funny slot game called a "
        "power blackout in the president's oval office. The attached room, redrawn BRIGHT, VIBRANT and EYE-CATCHING like a "
        "candy-coloured cartoon poster, at the exact moment the power blows: a huge electric-cyan and hot-pink "
        "lightning storm fills the tall windows with a brilliant violet-to-turquoise sky, crackling neon-blue electric "
        "arcs and a shower of bright yellow sparks burst from the swinging golden chandelier, warm golden candle "
        "flames glow on the desk and mantel, glowing amber curtains, royal-blue and lavender striped walls in bright "
        "light tints (not dark navy), a bright cobalt and gold oval rug, a red rotary phone on the desk, a few cash "
        "bills and gold coins fluttering in the air, chunky yellow cartoon lightning bolts. High-key and saturated: "
        "every area of the picture is clearly lit and colourful, light mid-tones, NO large black or dark areas, NO "
        "heavy vignette - a joyful, dopamine-bright colour explosion that still clearly reads as 'the power just went "
        "out'. " + STYLE)
PRESIDENT = ("A lobby-tile FOREGROUND character cut-out on a fully TRANSPARENT background: the attached blond president "
             "caricature (same face, same blond swoop, navy suit, white shirt, long red tie - an original cartoon "
             "character, no real-world insignia), seen from the waist up, big and centred, comically outraged and "
             "glaring sideways, one arm raising a lit candle high with a bright golden flame, the other fist gripping a "
             "frayed unplugged power cord whose plug spits bright electric-blue sparks and a small yellow cartoon "
             "lightning bolt. Bright, vivid, saturated colours, strong rim of warm candle light on his face and hair. "
             "Nothing else in the picture: no room, no floor, no shadow on the ground, no frame. " + STYLE)
JOBS = {   # job -> (prompt, aspect, refs, transparent)
    "bg16": (ROOM + " Wide landscape composition, the windows and the lightning storm in the centre.", "16:9",
             ["bg_v1.png"], False),
    "bg34": (ROOM + " Tall portrait composition: the tall centre window with the lightning storm and the sparking "
             "chandelier fill the upper half, the desk and the rug in the lower half.", "3:4", ["bg_v1.png"], False),
    "fg": (PRESIDENT, "3:4", ["H1_v1.png"], True),
}
PICKS = {"bg16": 1, "bg34": 1, "fg": 1}          # which take of each job build() uses


def raw(job, n):
    return os.path.join(OUT, f"{job}_{n}_raw.png")


def gen_one(job, n):
    prompt, aspect, refs, transparent = JOBS[job]
    try:
        _, cost = orimg.generate(raw(job, n), prompt, aspect=aspect, refs=[os.path.join(SRC, r) for r in refs],
                                 transparent=transparent)
        return f"OK {job} take {n} cost {cost}"
    except RuntimeError as e:
        return f"FAIL {job} take {n}: {e}"


def brightness(im):
    """Perceived brightness 0..1: mean of sqrt(.299 R^2 + .587 G^2 + .114 B^2) over the picture."""
    small = im.convert("RGB").resize((256, round(256 * im.height / im.width)))
    px = list(small.getdata())
    return sum(((.299 * r * r + .587 * g * g + .114 * b * b) ** .5) for r, g, b in px) / len(px) / 255


def build():
    import upscale4k
    os.makedirs(MEDIA, exist_ok=True)
    os.makedirs(FRONT, exist_ok=True)
    for job, name, size in (("bg16", "bg_16x9", (3840, 2160)), ("bg34", "bg_3x4", (2400, 3200))):
        im = Image.open(raw(job, PICKS[job])).convert("RGB")
        big = upscale4k.up4(im.convert("RGBA"), size=size).convert("RGB")
        big.save(os.path.join(MEDIA, name + ".png"), optimize=True)
        web = big.resize((size[0] // 2, size[1] // 2), Image.LANCZOS)
        web.save(os.path.join(FRONT, name + ".webp"), quality=90, method=6)
        print(name, big.size, f"brightness {brightness(big):.0%}")
    fg = Image.open(raw("fg", PICKS["fg"])).convert("RGBA")
    fg = fg.crop(fg.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
    big = upscale4k.up4(fg, long_edge=2048)
    big.save(os.path.join(MEDIA, "fg_president.png"), optimize=True)
    big.save(os.path.join(FRONT, "fg_president.webp"), quality=92, method=6)
    print("fg_president", big.size)


if __name__ == "__main__":
    cmd, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("", [])
    if cmd == "gen":
        os.makedirs(OUT, exist_ok=True)
        todo = []
        for spec in (args or ["bg16", "bg34", "fg"]):
            job, _, n = spec.partition(":")
            todo += [(job, int(k)) for k in (n.split(",") if n else ["1", "2"])]
        with ThreadPoolExecutor(6) as ex:
            for line in ex.map(lambda jn: gen_one(*jn), todo):
                print(line, flush=True)
    elif cmd == "build":
        build()
    elif cmd == "check":
        for f in sorted(os.listdir(OUT)):
            if f.startswith("bg"):
                print(f, f"{brightness(Image.open(os.path.join(OUT, f))):.0%}")
    else:
        print(__doc__)
