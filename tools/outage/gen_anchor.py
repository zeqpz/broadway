"""Power Outage: generate a symbol two ways (text only / with the owner's reference board for shape simplicity) to
pick the style anchor. usage: python tools/outage/gen_anchor.py <ID> [tag-suffix]"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg
ROOT = orimg.ROOT
SRC = os.path.join(ROOT, "art", "outage-src")
P = os.path.join(SRC, "prompts")
SYMS = json.load(open(os.path.join(SRC, "symbols.json"), encoding="utf-8"))
base = open(os.path.join(P, "icon_base.txt"), encoding="utf-8").read().strip()
style = open(os.path.join(P, "style.txt"), encoding="utf-8").read().strip()
sid = sys.argv[1] if len(sys.argv) > 1 else "H1"
suf = sys.argv[2] if len(sys.argv) > 2 else ""
pa = f"{base}\nThe symbol: {SYMS[sid]}.\n\n{style}\n"
pb = (f"{base}\nThe symbol: {SYMS[sid]}.\nThe attached picture is ONLY a reference from another game for how SIMPLE and "
      "CHUNKY the symbols should be (big readable shapes, thick outlines, few details); keep our flat cartoon colouring "
      "with no glossy candy shine, and draw a completely new subject - do not copy any object, character, colour scheme "
      "or layout from it. Draw ONE symbol only.\n\n" + style + "\n")
jobs = [("a", pa, []), ("b", pb, [os.path.join(P, "style_ref_board.png")])]


def run(j):
    tag, p, refs = j
    try:
        _, c = orimg.generate(os.path.join(SRC, "anchor", f"{sid}_{tag}{suf}.png"), p, refs=refs)
        return f"OK {sid}_{tag}{suf} {c}"
    except RuntimeError as e:
        return f"FAIL {sid}_{tag}{suf} {e}"


with ThreadPoolExecutor(2) as ex:
    for r in ex.map(run, jobs):
        print(r, flush=True)
