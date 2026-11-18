"""Power Outage: flat cartoon effect sprites for the Blender symbol clips -> art/outage-src/fx/<name>.png (RGBA, 256 px).
Flat colour, a thick black ink outline, one hard shade on the lower right - the same look as the symbols.
The file names are the kinds symanim.py's FX_SPEC asks for; the pictures are blackout ones:
  sparkle / sparkle_w / star  yellow, white and gold stars        steam  grey smoke wisp (no ink, see-through)
  puff   inked grey smoke cloud                                    bubble a cyan electric orb
  drop   a light-blue sweat drop                                   popcorn a green cash bill
  coin   a gold coin                                               straw  a yellow electric zig-zag spark
  feather a grey moth                                              crumb  a pale-blue glass shard
  leaf_red / leaf_orange  red down-arrows (the market)             leaf_gold a white sheet of paper
  ring   a yellow shock ring                                       rays   a yellow and cyan burst     flare a soft light"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "art", "outage-src", "fx")
INK = (17, 17, 17, 255)
S = 256
SS = 4


def canvas():
    return Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))


def done(im, name):
    im.resize((S, S), Image.LANCZOS).save(os.path.join(OUT, name + ".png"))


def poly_star(cx, cy, r0, r1, n, rot=0):
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r0
        a = rot + math.pi * i / n
        pts.append((cx + r * math.sin(a), cy - r * math.cos(a)))
    return pts


def inked_poly(pts, fill, shade=None, w=9):
    """An ink-outlined polygon with one hard shade offset to the lower right."""
    im = canvas()
    d = ImageDraw.Draw(im)
    d.polygon(pts, fill=INK)
    d.line(pts + [pts[0]], fill=INK, width=w * SS, joint="curve")
    inner = Image.new("L", im.size, 0)
    ImageDraw.Draw(inner).polygon(pts, fill=255)
    inner = inner.filter(ImageFilter.MinFilter(2 * w * SS // 2 * 2 + 1)) if w else inner
    im.paste(Image.new("RGBA", im.size, fill), (0, 0), inner)
    if shade:
        off = Image.new("L", im.size, 0)
        off.paste(inner, (-int(S * SS * .06), -int(S * SS * .06)))
        sh = Image.fromarray(np.minimum(np.asarray(inner), 255 - np.asarray(off)).astype(np.uint8))
        im.paste(Image.new("RGBA", im.size, shade), (0, 0), sh)
    return im


def circle_pts(cx, cy, r, n=64, wob=0.0, seed=0):
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 6.3, 3)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (1 + wob * (math.sin(3 * a + ph[0]) * .5 + math.sin(5 * a + ph[1]) * .3 + math.sin(2 * a + ph[2]) * .2))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def main():
    os.makedirs(OUT, exist_ok=True)
    C = S * SS / 2
    done(inked_poly(poly_star(C, C, C * .22, C * .92, 4), (255, 213, 74, 255), (255, 154, 60, 255), 7), "sparkle")
    done(inked_poly(poly_star(C, C, C * .3, C * .92, 4), (255, 255, 248, 255), (170, 236, 255, 255), 6), "sparkle_w")
    done(inked_poly(poly_star(C, C, C * .42, C * .92, 5), (255, 213, 74, 255), (232, 160, 40, 255), 8), "star")
    # steam: a grey smoke wisp, see-through, no ink
    im = canvas()
    d = ImageDraw.Draw(im)
    for (x, y, r) in [(.5, .55, .32), (.33, .5, .22), (.67, .48, .24), (.5, .35, .25)]:
        d.ellipse([C * 2 * x - C * 2 * r, C * 2 * y - C * 2 * r, C * 2 * x + C * 2 * r, C * 2 * y + C * 2 * r],
                  fill=(120, 126, 140, 205))
    done(im.filter(ImageFilter.GaussianBlur(10)), "steam")
    done(inked_poly(circle_pts(C, C, C * .7, 80, .14, 3), (170, 176, 190, 255), (122, 128, 145, 255), 8), "puff")
    # bubble: a cyan electric orb with a white core
    im = inked_poly(circle_pts(C, C, C * .62, 96), (63, 224, 255, 255), (20, 150, 210, 255), 8)
    ImageDraw.Draw(im).ellipse([C * .7, C * .62, C * 1.05, C * .95], fill=(255, 255, 255, 240))
    done(im, "bubble")
    # drop: a light-blue sweat drop
    pts = [(C + C * .5 * math.sin(a) * (1 - .7 * max(0, -math.cos(a))), C + C * .62 * -math.cos(a) * .9 + C * .1)
           for a in np.linspace(0, 2 * math.pi, 80, endpoint=False)]
    im = inked_poly(pts, (150, 214, 255, 255), (90, 160, 230, 255), 8)
    ImageDraw.Draw(im).ellipse([C * .78, C * .9, C * .98, C * 1.2], fill=(255, 255, 255, 230))
    done(im, "drop")
    # popcorn -> a green cash bill
    im = canvas()
    d = ImageDraw.Draw(im)
    box = [C * .25, C * .55, C * 1.75, C * 1.45]
    d.rounded_rectangle(box, radius=C * .1, fill=INK)
    d.rounded_rectangle([box[0] + 9 * SS, box[1] + 9 * SS, box[2] - 9 * SS, box[3] - 9 * SS], radius=C * .06, fill=(122, 200, 112, 255))
    d.rounded_rectangle([box[0] + 9 * SS, box[1] + C * .55, box[2] - 9 * SS, box[3] - 9 * SS], radius=C * .06, fill=(86, 160, 84, 255))
    d.ellipse([C * .72, C * .7, C * 1.28, C * 1.3], fill=INK)
    d.ellipse([C * .78, C * .76, C * 1.22, C * 1.24], fill=(196, 236, 170, 255))
    d.line([(C, C * .8), (C, C * 1.2)], fill=(40, 110, 52, 255), width=7 * SS)
    done(im, "popcorn")
    im = inked_poly(circle_pts(C, C, C * .72, 96), (232, 178, 58, 255), (190, 130, 30, 255), 8)
    d = ImageDraw.Draw(im)
    d.ellipse([C * .55, C * .55, C * 1.45, C * 1.45], outline=(190, 130, 30, 255), width=8 * SS)
    d.ellipse([C * .62, C * .52, C * .92, C * .76], fill=(255, 250, 220, 235))
    done(im, "coin")
    # straw -> a yellow electric zig-zag spark
    zig = [(.58, .04), (.2, .56), (.46, .56), (.3, .96), (.82, .4), (.56, .4), (.74, .04)]
    pts = [(C * 2 * x, C * 2 * y) for x, y in zig]
    done(inked_poly(pts, (255, 228, 80, 255), (255, 170, 40, 255), 7), "straw")
    # feather -> a little grey moth
    im = canvas()
    d = ImageDraw.Draw(im)
    for sx in (-1, 1):
        wing = [(C, C), (C + sx * C * .85, C * .5), (C + sx * C * .9, C * 1.1), (C + sx * C * .3, C * 1.3)]
        d.polygon(wing, fill=INK)
        d.line(wing + [wing[0]], fill=INK, width=14 * SS, joint="curve")
        inner = [(C + sx * C * .06, C * 1.0), (C + sx * C * .78, C * .6), (C + sx * C * .8, C * 1.05), (C + sx * C * .32, C * 1.2)]
        d.polygon(inner, fill=(178, 170, 160, 255))
    d.ellipse([C * .86, C * .6, C * 1.14, C * 1.5], fill=INK)
    d.ellipse([C * .92, C * .68, C * 1.08, C * 1.42], fill=(120, 112, 104, 255))
    done(im, "feather")
    # crumb -> a pale-blue glass shard
    done(inked_poly([(C * .5, C * .3), (C * 1.5, C * .55), (C * 1.1, C * 1.7)], (196, 226, 255, 255), (140, 180, 230, 255), 8), "crumb")
    # leaf -> red down-arrows and a white sheet of paper
    arrow = [(.38, .1), (.62, .1), (.62, .55), (.82, .55), (.5, .92), (.18, .55), (.38, .55)]
    pts = [(C * 2 * x, C * 2 * y) for x, y in arrow]
    done(inked_poly(pts, (215, 38, 61, 255), (160, 20, 40, 255), 8), "leaf_red")
    done(inked_poly(pts, (240, 80, 70, 255), (185, 40, 40, 255), 8), "leaf_orange")
    im = inked_poly([(C * .45, C * .25), (C * 1.55, C * .35), (C * 1.5, C * 1.75), (C * .4, C * 1.65)],
                    (244, 241, 232, 255), (200, 196, 186, 255), 8)
    d = ImageDraw.Draw(im)
    for k in range(5):
        y = C * (.6 + .22 * k)
        d.line([(C * .62, y), (C * 1.36, y + C * .02)], fill=(150, 150, 160, 255), width=5 * SS)
    done(im, "leaf_gold")
    im = canvas()
    d = ImageDraw.Draw(im)
    d.ellipse([C * .08, C * .08, C * 1.92, C * 1.92], outline=INK, width=26 * SS)
    d.ellipse([C * .12, C * .12, C * 1.88, C * 1.88], outline=(255, 213, 74, 255), width=14 * SS)
    done(im, "ring")
    # rays: 12 flat wedges, yellow and cyan, faded before the sprite's edge
    im = canvas()
    d = ImageDraw.Draw(im)
    for i in range(12):
        a0, a1 = 2 * math.pi * i / 12, 2 * math.pi * (i + .45) / 12
        d.polygon([(C, C), (C + C * math.cos(a0) * 1.4, C + C * math.sin(a0) * 1.4),
                   (C + C * math.cos(a1) * 1.4, C + C * math.sin(a1) * 1.4)],
                  fill=(63, 224, 255, 150) if i % 2 else (255, 213, 74, 160))
    yy, xx = np.mgrid[0:S * SS, 0:S * SS]
    rr = np.hypot(xx - C, yy - C) / C
    fall = np.clip((0.97 - rr) / 0.45, 0, 1) ** 1.2
    im.putalpha(Image.fromarray((np.asarray(im.getchannel("A")) * fall).astype(np.uint8)))
    done(im, "rays")
    a = (np.clip(1 - rr, 0, 1) ** 2.2 * 255).astype(np.uint8)
    done(Image.merge("RGBA", (Image.new("L", (S * SS, S * SS), 255),) * 3 + (Image.fromarray(a),)), "flare")
    print("fx sprites ->", OUT)


if __name__ == "__main__":
    main()
