"""Quick look at where every Rosie piece lands (no enlargement): figure | pieces | pieces over a ghost of the figure."""
import os, sys
import cv2, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rosie_parts as R
fig = R.rgba(R.FIG)
can = np.zeros_like(fig)
skip = sys.argv[1].split(",") if len(sys.argv) > 1 else []
for nm in R.ORDER:
    if nm in skip:
        continue
    raw = R.tidy(R.rgba(os.path.join(R.RAW, nm + ".png")))
    M = R.manual_M(nm) if nm in R.MANUAL else R.register(raw, fig, nm)[0]
    w = cv2.warpAffine(raw, M, (fig.shape[1], fig.shape[0]), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    al = w[..., 3:4] / 255.
    can[..., :3] = can[..., :3] * (1 - al) + w[..., :3] * al
    can[..., 3] = np.maximum(can[..., 3], w[..., 3])
out = Image.new("RGBA", (3072, 1536), (235, 235, 240, 255))
out.alpha_composite(Image.fromarray(fig.astype(np.uint8)), (0, 0))
out.alpha_composite(Image.fromarray(can.astype(np.uint8)), (1024, 0))
ghost = fig.copy(); ghost[..., 3] *= .35
out.alpha_composite(Image.fromarray(ghost.astype(np.uint8)), (2048, 0))
c2 = can.copy(); c2[..., 3] *= .75
out.alpha_composite(Image.fromarray(c2.astype(np.uint8)), (2048, 0))
out.convert("RGB").resize((1536, 768)).save(os.path.join(R.SRC, "rosie", "_reg_test.jpg"), quality=88)
print("ok")
