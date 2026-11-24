"""Rosie, the cowgirl beside the board: generate full-figure variants to pick from (style ref = H2's symbol).
usage: python tools/broadway/gen_rosie.py [n=3] [suffix]"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg
ROOT = orimg.ROOT
SRC = os.path.join(ROOT, "art", "broadway-src")
P = os.path.join(SRC, "prompts")
n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
suf = sys.argv[2] if len(sys.argv) > 2 else ""
style = open(os.path.join(P, "style.txt"), encoding="utf-8").read().strip()
body = open(os.path.join(P, "rosie.txt"), encoding="utf-8").read().strip()
prompt = (body + "\nThe attached pictures are two symbols from this same game: match them exactly in drawing style, outline "
          "weight, flat colouring and hard shade shapes, but draw a completely different person - do not copy their faces, "
          "hair or clothes.\n\n" + style + "\n")
refs = [os.path.join(SRC, "H2_v1.png"), os.path.join(SRC, "H1_v1.png")]


def run(k):
    out = os.path.join(SRC, "rosie", f"full_{k}{suf}.png")
    try:
        _, c = orimg.generate(out, prompt, aspect="2:3", refs=refs, model="openai/gpt-image-2.6-sunburst")
        return f"OK {out} {c}"
    except RuntimeError as e:
        return f"FAIL {out} {e}"


with ThreadPoolExecutor(n) as ex:
    for r in ex.map(run, range(1, n + 1)):
        print(r, flush=True)
