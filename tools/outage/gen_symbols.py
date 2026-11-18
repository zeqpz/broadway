"""Power Outage: generate the symbols (art/outage-src/symbols.json) with H1 (the President) as the style reference
and the owner's reference board for shape simplicity, 6 at a time.
usage: python tools/outage/gen_symbols.py [ID,ID..] [--suffix _v1]"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg

ROOT = orimg.ROOT
SRC = os.path.join(ROOT, "art", "outage-src")
P = os.path.join(SRC, "prompts")
SYMS = json.load(open(os.path.join(SRC, "symbols.json"), encoding="utf-8"))


def prompt(desc):
    base = open(os.path.join(P, "icon_base.txt"), encoding="utf-8").read().strip()
    style = open(os.path.join(P, "style.txt"), encoding="utf-8").read().strip()
    return (f"{base}\nThe symbol: {desc}.\nThe FIRST attached picture is another symbol from this same set: match it exactly "
            "in drawing style, outline weight, flat colouring, hard shadow shapes and scale on the canvas. The SECOND attached "
            "picture is only a reference from a different game for how simple and chunky symbols should be - do not copy any "
            "object, character, colour or layout from it, and keep our flat cartoon colouring (no glossy shine). "
            f"Draw ONE symbol only.\n\n{style}\n")


def one(sid, suffix):
    out = os.path.join(SRC, f"{sid}{suffix}.png")
    refs = [os.path.join(SRC, "H1_v1.png"), os.path.join(P, "style_ref_board.png")]
    try:
        _, cost = orimg.generate(out, prompt(SYMS[sid]), refs=refs)
        return f"OK {sid} {cost}"
    except RuntimeError as e:
        return f"FAIL {sid} {e}"


if __name__ == "__main__":
    ids = sys.argv[1].split(",") if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else [k for k in SYMS if k != "H1"]
    suffix = sys.argv[sys.argv.index("--suffix") + 1] if "--suffix" in sys.argv else "_v1"
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(lambda s: one(s, suffix), ids):
            print(r, flush=True)
