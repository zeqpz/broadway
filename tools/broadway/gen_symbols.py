"""Broadway on Nashville: generate the symbols (art/broadway-src/symbols.json) with the chosen style anchor as the
style reference, 6 at a time (gpt-image-2.6).
usage: python tools/broadway/gen_symbols.py [ID,ID..] [--suffix _v1] [--ref path]"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg

ROOT = orimg.ROOT
SRC = os.path.join(ROOT, "art", "broadway-src")
P = os.path.join(SRC, "prompts")
SYMS = json.load(open(os.path.join(SRC, "symbols.json"), encoding="utf-8"))
MODEL = "openai/gpt-image-2.6-sunburst"


def prompt(desc):
    base = open(os.path.join(P, "icon_base.txt"), encoding="utf-8").read().strip()
    style = open(os.path.join(P, "style.txt"), encoding="utf-8").read().strip()
    return (f"{base}\nThe symbol: {desc}.\nThe attached picture is another symbol from this same set: match it exactly in "
            "drawing style, outline weight, flat colouring, hard shade shapes, level of detail and scale on the canvas, but "
            "draw a completely different subject - do not copy the character, his suit or his microphone unless asked. "
            f"Draw ONE symbol only.\n\n{style}\n")


def one(sid, suffix, ref):
    out = os.path.join(SRC, f"{sid}{suffix}.png")
    try:
        _, cost = orimg.generate(out, prompt(SYMS[sid]), refs=[ref], model=MODEL)
        return f"OK {sid} {cost}"
    except RuntimeError as e:
        return f"FAIL {sid} {e}"


if __name__ == "__main__":
    ids = sys.argv[1].split(",") if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else list(SYMS)
    suffix = sys.argv[sys.argv.index("--suffix") + 1] if "--suffix" in sys.argv else "_v1"
    ref = sys.argv[sys.argv.index("--ref") + 1] if "--ref" in sys.argv else os.path.join(SRC, "anchor", "H1_b.png")
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(lambda s: one(s, suffix, ref), ids):
            print(r, flush=True)
