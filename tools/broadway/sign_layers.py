"""The title sign as a lit OLED / LED sign, in layers (owner pass 5, 2026-11-19: "make the GE glitch and sometimes turn
on, make the text glowing"; then: "when the GE flickers we want it to look like it has an OLED light on it ... the
power outage still needs a glow so it looks like an OLED sign").

The art is ONE picture: art/broadway-src/ui/logo_sign_led.png (tools/broadway/gen_pass5.py, the image model's redraw of
the steel sign with all eleven letters switched on - luminous faces, white-hot in the middle, amber at the edge, and no
glow painted on the plate). Everything the page stacks is cut from it, so the layers line up to the pixel:
  logo_sign.webp           the sign as it rests: POWER OUTA lit, G and E dead - their faces repainted as unlit grey
                           panels (a lighter upper tone, a darker lower one, like the first sign's dead letters)
  logo_sign_ge.webp        G and E's lit faces, exactly as drawn: the page fades / stutters this layer in (--ge)
  logo_sign_glow.webp      the light the nine lit letters throw: a hot bloom hugging the letters, a wide warm spill
                           over the steel and a haze past its edge; screen-blended, it hums
  logo_sign_ge_glow.webp   the same for G and E, shown with them
A letter is a region closed off by the black outline: the eleven big warm ones inside the plate; G and E are the two
at the right of the second row.
usage: python tools/broadway/sign_layers.py"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
A = os.path.join(ROOT, "frontend", "assets")
SRC = os.path.join(ROOT, "art", "broadway-src", "ui", "logo_sign_led.png")
SIZE = (1200, 900)
LUM = np.array([.299, .587, .114], np.float32)


def contain(im, size):
    """The art fitted into the sign's canvas (as fit_pass2.py fitted the first sign)."""
    bb = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    im = im.crop(bb)
    W, H = size
    k = min(W / im.width, H / im.height) * .98
    sm = im.convert("RGBa").resize((round(im.width * k), round(im.height * k)), Image.LANCZOS).convert("RGBA")
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.alpha_composite(sm, ((W - sm.width) // 2, (H - sm.height) // 2))
    return out


def halo(mask, plate, ink, tight=7, wide=46):
    """The light a set of lit letters throws: RGBA float (0..1), for a screen blend. A hot bloom close in (it creeps
    over the outline a little, as a bright light does), a wide warm spill over the steel, a fainter haze in the air
    past the plate's edge. The faces themselves are already white-hot in the art: only a slight lift there."""
    t = ndi.gaussian_filter(mask, tight)
    m = ndi.gaussian_filter(mask, 18)
    w = ndi.gaussian_filter(mask, wide)
    w = w / max(w.max(), 1e-6)
    core, mid, outer = (np.array(c, np.float32) for c in ([255, 240, 190], [255, 196, 96], [255, 140, 36]))
    k1, k2 = np.clip(t * 1.2, 0, 1)[..., None], np.clip(m * 1.3, 0, 1)[..., None]
    rgb = outer + (mid - outer) * k2
    rgb = rgb + (core - rgb) * k1
    a = np.clip(.62 * t + .42 * m + .5 * w ** 1.2, 0, .92)
    a *= 1 - .74 * ndi.gaussian_filter(mask, 1.2)
    a *= 1 - .68 * ink
    a *= .55 + .45 * plate
    return np.dstack([rgb / 255, a])


def save(arr, name):
    im = Image.fromarray((np.clip(arr, 0, 1) * 255 + .5).astype(np.uint8), "RGBA")
    p = os.path.join(A, name)
    im.save(p, "WEBP", quality=90, alpha_quality=96, method=6)
    return os.path.getsize(p)


def main():
    im = np.asarray(contain(Image.open(SRC).convert("RGBA"), SIZE)).astype(np.float32)
    H, W = im.shape[:2]
    rgb, al = im[..., :3], im[..., 3]
    lum = rgb @ LUM
    ink = (lum < 62) & (al > 128)
    lab, n = ndi.label((~ink) & (al > 128))
    letters = []
    for i, s in enumerate(ndi.find_objects(lab), 1):
        m = lab[s] == i
        if m.sum() < 9000:
            continue
        y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
        c = rgb[s][m].mean(0)
        if c[0] - c[2] > 90 and c[0] > 200 and y0 > .25 * H and y1 < .9 * H and x1 < .93 * W:   # warm, inside the plate, not the bulb
            letters.append((i, s, m, (x0 + x1) / 2, (y0 + y1) / 2))
    assert len(letters) == 11, [(round(l[3]), round(l[4])) for l in letters]
    ys = [q[4] for q in letters]
    row2 = sorted([l for l in letters if l[4] > (min(ys) + max(ys)) / 2], key=lambda l: l[3])   # the lower word
    assert len(row2) == 6, len(row2)                       # O U T A G E
    lit, dead = np.zeros((H, W), bool), np.zeros((H, W), bool)
    for l in letters:
        (dead if l in row2[-2:] else lit)[l[1]] |= l[2]
    # the resting sign: G and E unlit - grey panels, a lighter upper tone and a darker lower one (the cut tilts a touch
    # like the art's own shading), their white glints kept as soft grey ones
    base = rgb.copy()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for l in row2[-2:]:
        s, m = l[1], l[2]
        y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
        cut = y0 + (y1 - y0) * .6 - (xx[s] - x0) * .16
        up = np.clip((cut - yy[s]) / 2.5 + .5, 0, 1)[..., None]          # 1 above the cut, a soft 2.5 px edge
        tone = np.array([86, 96, 119], np.float32) + (np.array([134, 142, 162], np.float32) - np.array([86, 96, 119], np.float32)) * up
        glint = np.clip((rgb[s].min(-1) - 232) / 18, 0, 1)[..., None]     # the art's pure-white glints
        tone = tone + (np.array([226, 230, 240], np.float32) - tone) * glint
        edge = np.clip(lum[s] / 150, 0, 1)[..., None]                    # the soft pixels toward the outline keep their shade
        base[s] = np.where(m[..., None], tone * (.35 + .65 * edge), base[s])
    grow = ndi.binary_dilation(dead, iterations=2) & ~dead               # the anti-aliased rim: toward the unlit tone too
    base[grow] = base[grow] * .45 + np.array([40, 44, 56], np.float32) * .55 * np.clip(lum[grow] / 120, 0, 1)[..., None]
    print("logo_sign.webp", save(np.dstack([base / 255, al / 255]), "logo_sign.webp"))
    # G and E switched on: their faces as drawn
    a = ndi.gaussian_filter(ndi.binary_dilation(dead, iterations=2).astype(np.float32), .8)
    a = np.where(dead, 1, a) * (al / 255)
    print("logo_sign_ge.webp", save(np.dstack([rgb / 255, a]), "logo_sign_ge.webp"))
    plate = ndi.gaussian_filter((al > 128).astype(np.float32), 2)
    inks = ndi.gaussian_filter(ink.astype(np.float32), 1.2)
    print("logo_sign_glow.webp", save(halo(lit.astype(np.float32), plate, inks), "logo_sign_glow.webp"))
    print("logo_sign_ge_glow.webp", save(halo(dead.astype(np.float32), plate, inks), "logo_sign_ge_glow.webp"))


if __name__ == "__main__":
    main()
