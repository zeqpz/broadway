"""Rosie v2 (owner, 2026-11-22: "the clothes should be tighter and she should be thinner ... looks too much like AI"):
a slim figure in a fitted outfit, drawn as a clean TV model-sheet pose (uniform line weight, flat colour, few
highlights), posed so every rig piece can be cut straight out of it (gaps round the arms and between the legs).
usage: python tools/broadway/gen_rosie_v2.py [n=4] [suffix]"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg
ROOT = orimg.ROOT
SRC = os.path.join(ROOT, "art", "broadway-src")
n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
suf = sys.argv[2] if len(sys.argv) > 2 else ""
body = open(os.path.join(SRC, "prompts", "rosie2.txt"), encoding="utf-8").read().strip()
REF = ("\nThe attached picture is an earlier drawing of the same character, only for who she is (her face, hair colour, "
       "hat, colours): redraw her much SLIMMER, in TIGHT fitted clothes, in the cleaner model-sheet style described above.")


def run(k):
    out = os.path.join(SRC, "rosie2", f"full_{k}{suf}.png")
    refs = [os.path.join(SRC, "rosie", "full_2_b.png")] if k % 2 == 0 else []
    try:
        _, c = orimg.generate(out, body + (REF if refs else ""), aspect="2:3", refs=refs, model="openai/gpt-image-2.6-sunburst")
        return f"OK {out} {c}"
    except RuntimeError as e:
        return f"FAIL {out} {e}"


with ThreadPoolExecutor(n) as ex:
    for r in ex.map(run, range(1, n + 1)):
        print(r, flush=True)
