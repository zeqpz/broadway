"""Owner pass 4 (2026-11-18): the title sign in steel to match the frame (not wood), no hanging rods, no text change."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg
from gen_ui import STYLE
ROOT = orimg.ROOT
RAW = os.path.join(ROOT, "art", "broadway-src", "ui")
P = ("Redraw the attached title sign with EXACTLY the same POWER / OUTAGE lettering (same letter shapes, colours, sizes and "
     "positions, the last letters of OUTAGE grey and unlit) and the same cracked light bulb with sparks on its top-right "
     "corner, but the sign board itself is now made of chunky cartoon grey STEEL like the second attached picture (the "
     "game's breaker-panel frame): a riveted steel plate with a thick black outline, flat steel grey with one hard darker "
     "shade, round steel rivets at the corners, a thin strip of yellow-and-black hazard stripes along its bottom edge. No "
     "wood anywhere, no hanging rods, no chains. Transparent background.")
_, c = orimg.generate(os.path.join(RAW, "logo_sign3.png"), P + "\n\n" + STYLE, aspect="4:3",
                      refs=[os.path.join(RAW, "logo_sign2.png"), os.path.join(RAW, "frame.png")])
print("OK logo_sign3", c)
