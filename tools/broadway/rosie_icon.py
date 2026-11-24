"""Rosie's head for the features screen's Encore card (assets/flat/rosie_icon.webp, 480 px): her back hair, the smiling
face and her hat from art/broadway-src/rosie_parts, laid together and cropped round the head.
usage: python tools/broadway/rosie_icon.py"""
import json, os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "art", "broadway-src", "rosie_parts")
meta = json.load(open(os.path.join(P, "parts.json")))
W, H = meta["size"]
can = Image.new("RGBA", (W, H), (0, 0, 0, 0))
for nm, key in (("hair_back", "parts"), ("face_smile", "faces"), ("hat", "parts")):
    box = meta[key][nm if key == "parts" else nm[5:]]["box"]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(Image.open(os.path.join(P, nm + ".png")).convert("RGBA"), tuple(box[:2]))
    can = Image.alpha_composite(can, layer)
k = meta["scale"]
crop = can.crop((int(140 * k), 0, int(700 * k), int(560 * k)))
bb = crop.getchannel("A").getbbox()
crop = crop.crop(bb)
side = max(crop.size)
sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
sq.alpha_composite(crop, ((side - crop.width) // 2, (side - crop.height) // 2))
sq.convert("RGBa").resize((480, 480), Image.LANCZOS).convert("RGBA").save(
    os.path.join(ROOT, "frontend", "assets", "flat", "rosie_icon.webp"), "WEBP", quality=92, alpha_quality=100, method=6)
print("rosie_icon 480")
