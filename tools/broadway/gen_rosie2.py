"""Rosie round 2: the chosen figure (full_1) redrawn with a prettier face, same pose/outfit/guitar.
usage: python tools/broadway/gen_rosie2.py [n=3] [base=full_1] [suffix=_b]"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg
ROOT = orimg.ROOT
SRC = os.path.join(ROOT, "art", "broadway-src")
P = os.path.join(SRC, "prompts")
n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
base = sys.argv[2] if len(sys.argv) > 2 else "full_1"
suf = sys.argv[3] if len(sys.argv) > 3 else "_b"
style = open(os.path.join(P, "style.txt"), encoding="utf-8").read().strip()
prompt = ("Redraw the attached character (image 1) as the SAME full-body figure: the same pose, the same three-quarter "
          "stance, the same outfit, hat, boots, belt and the same red electric guitar with its rose decals and strap, the "
          "same size and position on the canvas, isolated on a fully transparent background. Change ONLY her face and "
          "make it genuinely attractive and glamorous, like a pretty leading lady in an adult animated TV sitcom: "
          "almond-shaped eyes with long dark lashes and blue irises, a confident, flirty half-lidded look towards the "
          "viewer, softly arched eyebrows, a small cute upturned nose, full red lips in a warm closed-mouth smile with one "
          "corner raised (a sweet smirk), a defined jaw and chin, rosy cheeks. Her auburn curls are big, glossy and "
          "voluminous. She is a grown woman, charming and confident, not goofy, not exaggerated, not explicit. Keep her "
          "arms, the guitar, her legs, hair and hat clearly separated with clean gaps (she will be cut into puppet parts). "
          "Image 2 is another symbol from this game, only for the drawing style.\n\n" + style + "\n")
refs = [os.path.join(SRC, "rosie", base + ".png"), os.path.join(SRC, "H2_v1.png")]


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
