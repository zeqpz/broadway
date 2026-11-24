"""Power Outage owner pass 2 (2026-11-18): art redone on the owner's notes.
  logo_sign2     the title board WITHOUT the two hanging rods and rings (redrawn from the current sign)
  banner_*2      the bonus shop's three banners, each with a full painted background (no flat backdrop)
  bonus_icon     the HUD's bonus button as an illustrated emblem, not just the word
usage: python tools/broadway/gen_pass2.py gen [names] | fit"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg
from gen_ui import STYLE

ROOT = orimg.ROOT
RAW = os.path.join(ROOT, "art", "broadway-src", "ui")
SRC = os.path.join(ROOT, "art", "broadway-src")
A = os.path.join(ROOT, "frontend", "assets")
S = lambda n: os.path.join(SRC, n + "_v1.png")
OPAQUE = STYLE.replace(" Transparent background.", "")
BANNER = ("A wide game bonus-shop banner illustration that fills the WHOLE picture edge to edge with a fully painted cartoon "
          "background scene - no plain backdrop, no transparency, no checkerboard, no border, no frame, no text, no letters "
          "except the ones on the attached symbol. ")
JOBS = {
    "logo_sign2": ("Redraw the attached sign board EXACTLY - the same dark wooden planks, the same POWER / OUTAGE lettering with "
                   "the same colours and shapes, the same cracked light bulb with its sparks on the top-right corner - but "
                   "WITHOUT the two hanging metal rods and rings at the top: the sign stands on its own, the top edge of the "
                   "wooden planks continues clean and unbroken where the rings were. Nothing else changes. Transparent "
                   "background.", "4:3", [os.path.join(RAW, "logo_sign.png")], True),
    "banner_fs2": (BANNER + "The attached FS light-bulb symbol big in the middle, glowing as the power comes back on, in front of "
                   "the attached blacked-out oval office: the chandelier flickering to life, warm yellow light rays bursting "
                   "out from the bulb across the dark room, sparks and a few gold coins in the air.", "16:9",
                   [S("BS"), os.path.join(SRC, "bg_v1.png")], False),
    "banner_xfs2": (BANNER + "The attached XFS high-voltage symbol big in the middle, in front of a dark stormy night city skyline "
                    "with every window black, huge chunky yellow and cyan lightning bolts striking a big power station and "
                    "its pylons behind it, sparks flying, dramatic purple-navy storm clouds.", "16:9", [S("ES")], False),
    "banner_boost2": (BANNER + "A big chunky cartoon battery being charged in the middle, its meter full and glowing green, a fat "
                      "plug and cable plugged into it, inside a buzzing cartoon power-plant control room: big round dials with "
                      "needles in the red, levers, blinking lights, cables everywhere, flat yellow zig-zag sparks.", "16:9",
                      [S("L3")], False),
    "bonus_icon": ("A chunky cartoon game button emblem for opening the bonus shop, seen straight on: a big round glossy red "
                   "emergency power button inside a thick yellow-and-black hazard-stripe ring with steel rivets, a glowing "
                   "yellow cartoon light bulb with a lightning bolt inside it bursting up out of the button, a few green cash "
                   "bills and gold coins flying round it, and a small curved yellow ribbon banner across the bottom of the "
                   "badge with the word \"BONUS\" on it in chunky navy letters (the only text). Transparent background.",
                   "1:1", [S("H1"), S("BS")], True),
}


def gen(name):
    p, aspect, refs, transparent = JOBS[name]
    note = "The attached pictures are from this same game: match their outline weight and flat cartoon colouring exactly."
    style = STYLE if transparent else OPAQUE
    try:
        _, c = orimg.generate(os.path.join(RAW, name + ".png"), p + "\n\n" + note + "\n\n" + style, aspect=aspect, refs=refs,
                              transparent=transparent)
        return f"OK {name} {c}"
    except RuntimeError as e:
        return f"FAIL {name} {e}"


if __name__ == "__main__":
    names = sys.argv[2].split(",") if len(sys.argv) > 2 else list(JOBS)
    with ThreadPoolExecutor(5) as ex:
        for r in ex.map(gen, names):
            print(r, flush=True)
