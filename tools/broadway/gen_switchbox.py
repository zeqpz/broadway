"""The breaker switch's empty box (no lever), drawn to cover the frame's old switch so the handle can move on its own."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg
from gen_ui import STYLE
ROOT = orimg.ROOT
P = ("A single chunky cartoon electrical breaker switch box, seen straight on, for bolting onto a steel frame: a tall "
     "rounded-rectangle steel plate (about 2 wide by 3 tall) with a very thick black outline, flat steel grey with one hard "
     "darker shade, a round steel rivet at the top-left and bottom-left corners, a raised inner panel with its own black "
     "outline, and near the TOP of the inner panel a dark horizontal slot (a black rounded opening) where a lever comes "
     "out. NO lever, NO handle, NOTHING sticking out of the slot. Match the attached switch exactly in colours, outline "
     "weight and style (it is the same switch with its red lever removed). Transparent background.")
_, c = orimg.generate(os.path.join(ROOT, "art", "broadway-src", "ui", "switchbox.png"), P + "\n\n" + STYLE,
                      aspect="2:3", refs=[os.path.join(ROOT, "art", "broadway-src", "prompts", "ref_lever.png")])
print("OK switchbox", c)
