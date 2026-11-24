"""The Encore card's picture on the features screen (owner, 2026-11-24: the cowgirl is gone, so her head no longer
stands for the Encore): a red electric guitar in a stage spotlight, drawn in the finish of the v2 symbols.
-> art/broadway-src/encore/encore_<n>.png;  `pick <n>` -> frontend/assets/flat/encore_icon.webp (480 px)
usage: python tools/broadway/gen_encore_icon.py gen [n] | pick <n>"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg
from PIL import Image
ROOT = orimg.ROOT
SRC = os.path.join(ROOT, "art", "broadway-src")
OUT = os.path.join(SRC, "encore")
PROMPT = (
    "A single slot machine game feature icon, centred, isolated on a fully transparent background, filling about 88% of "
    "a square canvas, a bold readable silhouette. No border, no sticker outline, no drop shadow, no background, no "
    "frame, NO text, NO letters, NO people, NO hands.\n"
    "The icon: a red electric guitar with a white pickguard, leaning at a jaunty angle, standing in a stage spotlight - "
    "a small black stage lamp at the top-left corner throws a flat, solid warm-yellow cone of light down onto the "
    "guitar (the cone is an opaque flat cartoon shape with a black outline, not a soft glow), and the light makes a "
    "flat pale-yellow oval pool under the guitar. Three chunky gold five-point stars and two pink music notes pop around "
    "the guitar.\n\n"
    "STYLE: drawn like an official model sheet from a professional American adult-animation TV show - clean, confident, "
    "UNIFORM black line weight, flat matte colours with ONE simple hard-edged shade, only one or two tiny highlights, "
    "NO glossy plastic shine, no airbrush, no gradients, no texture noise, no fussy over-detailing; simple, "
    "well-designed shapes with a few deliberate details. Match the attached symbols' line weight and flat colouring "
    "exactly (they are other icons from the same game), but draw ONLY the icon described. Original design: no logos, "
    "no brands.")
REFS = [os.path.join(SRC, "H7_v2.png"), os.path.join(SRC, "L3_v2.png"), os.path.join(SRC, "H6_v2.png")]


def one(k):
    out = os.path.join(OUT, f"encore_{k}.png")
    try:
        _, c = orimg.generate(out, PROMPT, refs=REFS, model="openai/gpt-image-2.6-sunburst")
        return f"OK {k} {c}"
    except RuntimeError as e:
        return f"FAIL {k} {e}"


def pick(k):
    im = Image.open(os.path.join(OUT, f"encore_{k}.png")).convert("RGBA")
    im = im.crop(im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox())
    side = max(im.size)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.alpha_composite(im, ((side - im.width) // 2, (side - im.height) // 2))
    dst = os.path.join(ROOT, "frontend", "assets", "flat", "encore_icon.webp")
    sq.convert("RGBa").resize((480, 480), Image.LANCZOS).convert("RGBA").save(dst, "WEBP", quality=92, alpha_quality=100, method=6)
    print("encore_icon 480 from take", k)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "gen"
    if cmd == "pick":
        pick(sys.argv[2])
    else:
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        os.makedirs(OUT, exist_ok=True)
        with ThreadPoolExecutor(n) as ex:
            for r in ex.map(one, range(1, n + 1)):
                print(r, flush=True)
