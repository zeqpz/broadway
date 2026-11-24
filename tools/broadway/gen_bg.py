"""Broadway on Nashville backgrounds: the street (base + standard bonus) and the Xtreme rooftop, then the phone
redraws (2:3) and the neon-off plates the scene's light layers are cut from (tools/broadway/bg_layers.py).
  gen  bg|bg_xtreme              16:9 from the prompts in art/broadway-src/prompts/<name>.txt (style ref: two symbols)
  mobile bg|bg_xtreme            2:3 phone redraws of art/broadway-src/<name>_v1.png
  unlit bg|bg_mobile             the same picture with every neon sign and bulb switched off (for the flicker layers)
usage: python tools/broadway/gen_bg.py gen|mobile|unlit name[,name] [--suffix _v1]"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg
ROOT = orimg.ROOT
SRC = os.path.join(ROOT, "art", "broadway-src")
P = os.path.join(SRC, "prompts")
MODEL = "openai/gpt-image-2.6-sunburst"
STYLE = open(os.path.join(P, "style.txt"), encoding="utf-8").read().strip()
REFNOTE = ("The attached pictures are two symbols from this same game, only for the drawing style (outline weight, flat "
           "colour, hard shade shapes): draw none of them in the scene.")


def job(cmd, name, suf):
    if cmd == "gen":
        p = open(os.path.join(P, name + ".txt"), encoding="utf-8").read().strip() + "\n" + REFNOTE + "\n\n" + STYLE
        refs = [os.path.join(SRC, "H4_v1.png"), os.path.join(SRC, "H6_v1.png")]
        out, aspect = os.path.join(SRC, name + suf + ".png"), "16:9"
    elif cmd == "mobile":
        p = ("Redraw the attached slot game background as a TALL PORTRAIT picture (2:3) for phones: the same place at "
             "night in exactly the same flat adult-animation cartoon style, the same colours, outlines, buildings, signs "
             "and props - but recomposed for a tall screen: the night sky and distant skyline at the top, the buildings "
             "and their neon signs in the upper middle, the street and pavement in the lower part. Keep the middle "
             "calm (a slot reel board sits over it). No people, no characters, no logos. Flat hard-edged light shapes, "
             "no glow haze.")
        refs = [os.path.join(SRC, name + "_v1.png")]
        out, aspect = os.path.join(SRC, name + "_mobile" + suf + ".png"), "2:3"
    else:   # unlit
        p = ("Redraw the attached picture EXACTLY - the same buildings, the same composition, the same shapes, outlines, "
             "colours and every detail in the same place - but with EVERY neon sign, neon word, marquee bulb and string "
             "light SWITCHED OFF: the neon tubes become dull unlit glass tubes (greyish pastel versions of their colours "
             "with a thin dark outline), the bulbs become pale grey unlit glass, and the flat coloured light patches "
             "they threw on the walls and pavement are gone. The windows, street lamps, moon, stars and skyline stay "
             "exactly as they are. No other changes.")
        refs = [os.path.join(SRC, name + "_v1.png")]
        out, aspect = os.path.join(SRC, name + "_unlit" + suf + ".png"), "16:9" if "mobile" not in name else "2:3"
    try:
        _, c = orimg.generate(out, p, aspect=aspect, transparent=False, refs=refs, model=MODEL)
        return f"OK {out} {c}"
    except RuntimeError as e:
        return f"FAIL {out} {e}"


if __name__ == "__main__":
    cmd, names = sys.argv[1], sys.argv[2].split(",")
    suf = sys.argv[sys.argv.index("--suffix") + 1] if "--suffix" in sys.argv else "_v1"
    with ThreadPoolExecutor(4) as ex:
        for r in ex.map(lambda n: job(cmd, n, suf), names):
            print(r, flush=True)
