"""Power Outage: the pictures gen_ui.py doesn't cover - the Multi value glyph sheet and border (tools/outage/vnum.py
cuts them) and the bonus shop's three banners (assets/bonus/banner_*.webp, 1440x810).
usage: python tools/outage/gen_extra.py gen [name,..] | fit"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg
from gen_ui import STYLE, REFNOTE, REF_SYM

ROOT = orimg.ROOT
RAW = os.path.join(ROOT, "art", "outage-src", "ui")
ASSETS = os.path.join(ROOT, "frontend", "assets")
SYMI = lambda s: os.path.join(ROOT, "art", "outage-src", s + "_v1.png")
NUMS = ("chunky bouncy cartoon numerals, FLAT electric-cyan fill (#3FE0FF) with a hard deep-blue shadow shape on the lower "
        "half, a very thick black outline, one small white highlight, all the same size and style")
JOBS = {
    "vnum": ('A 4 by 3 grid of separate game glyphs on a transparent background, one glyph centred in each cell with plenty of '
             'space between: top row "x 0 1 2", middle row "3 4 5 6", bottom row "7 8 9 ." (a small lowercase multiplication '
             'x, the ten digits and a full stop) - ' + NUMS + '.', "1:1", [REF_SYM]),
    "vborder": ("A round cartoon badge ring for showing a multiplier value: a thick ring of yellow-and-black hazard stripes "
                "with a thick black outline inside and out, four small steel rivets on it, the middle COMPLETELY EMPTY and "
                "TRANSPARENT (cut out), seen straight on, perfectly round.", "1:1", [REF_SYM]),
    "banner_fs": ("A wide game bonus banner illustration (no text, no letters): the attached FS light-bulb symbol big in the "
                  "middle, glowing as the lights come back on, on a flat dark-navy background with flat yellow light rays "
                  "bursting out behind it and a few flat sparks; framed by a chunky rounded black outline.", "16:9",
                  [SYMI("BS")]),
    "banner_xfs": ("A wide game bonus banner illustration (no text, no letters): the attached XFS high-voltage symbol big in "
                   "the middle, on a flat dark-navy background with big flat yellow and cyan lightning bolts striking "
                   "behind it and flat sparks flying; framed by a chunky rounded black outline.", "16:9", [SYMI("ES")]),
    "banner_boost": ("A wide game bonus banner illustration (no text, no letters): a big chunky cartoon battery being charged "
                     "up - its meter full and glowing green - with a plug and cable plugged into it, flat yellow lightning "
                     "zig-zags round it, on a flat dark-navy background; framed by a chunky rounded black outline.", "16:9",
                     [REF_SYM]),
}


def gen(name):
    p, aspect, refs = JOBS[name]
    note = ("The attached picture is from this same game: match its outline weight and flat colouring exactly"
            + (" and draw that same symbol." if name.startswith("banner_") and name != "banner_boost" else "."))
    try:
        _, c = orimg.generate(os.path.join(RAW, name + ".png"), p + "\n\n" + note + "\n\n" + STYLE, aspect=aspect, refs=refs,
                              transparent=not name.startswith("banner_"))
        return f"OK {name} {c}"
    except RuntimeError as e:
        return f"FAIL {name} {e}"


def fit():
    for n in ("banner_fs", "banner_xfs", "banner_boost"):
        im = Image.open(os.path.join(RAW, n + ".png")).convert("RGB").resize((1440, 810), Image.LANCZOS)
        im.save(os.path.join(ASSETS, "bonus", n + ".webp"), "WEBP", quality=88, method=6)
        print("fit", n)


if __name__ == "__main__":
    if sys.argv[1] == "gen":
        names = sys.argv[2].split(",") if len(sys.argv) > 2 else list(JOBS)
        with ThreadPoolExecutor(5) as ex:
            for r in ex.map(gen, names):
                print(r, flush=True)
    else:
        fit()
