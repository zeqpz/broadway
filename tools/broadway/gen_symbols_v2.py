"""Symbols v2 (owner, 2026-11-22: "the artwork looks too much like AI and low quality"): the same thirteen subjects
(art/broadway-src/symbols.json) redrawn in the finish of Rosie v2 - a professional TV-animation model sheet: uniform
black line weight, flat matte colour with one hard shade, only a few small highlights, no glossy plastic shine, no
texture noise - with Rosie v2 as the style reference. -> art/broadway-src/<ID>_v2.png
usage: python tools/broadway/gen_symbols_v2.py [ID,ID..]"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg
ROOT = orimg.ROOT
SRC = os.path.join(ROOT, "art", "broadway-src")
SYMS = json.load(open(os.path.join(SRC, "symbols.json"), encoding="utf-8"))
BASE = ("A single slot machine game symbol icon, centred, isolated on a fully transparent background, filling about 88% of "
        "a square canvas, a slight three-quarter view, a bold readable silhouette. No border, no sticker outline, no drop "
        "shadow, no glow, no background, no frame, no text unless asked.")
STYLE = ("STYLE: drawn like an official model sheet from a professional American adult-animation TV show - clean, "
         "confident, UNIFORM black line weight, flat matte colours with ONE simple hard-edged shade, only one or two tiny "
         "highlights, NO glossy plastic shine, no airbrush, no gradients, no texture noise, no fussy over-detailing; "
         "simple, well-designed shapes with a few deliberate details. Match the attached character's line weight and "
         "flat colouring exactly, but draw ONLY the symbol described (not her). Original design: no logos, no brands, "
         "no real people.")


def one(sid):
    out = os.path.join(SRC, f"{sid}_v2.png")
    p = f"{BASE}\nThe symbol: {SYMS[sid]}.\n\n{STYLE}"
    try:
        _, c = orimg.generate(out, p, refs=[os.path.join(SRC, "rosie2", "rosie_v2.png")], model="openai/gpt-image-2.6-sunburst")
        return f"OK {sid} {c}"
    except RuntimeError as e:
        return f"FAIL {sid} {e}"


if __name__ == "__main__":
    ids = sys.argv[1].split(",") if len(sys.argv) > 1 else list(SYMS)
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(one, ids):
            print(r, flush=True)
