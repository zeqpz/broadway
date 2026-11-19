"""The title sign's live layers (owner pass 5, 2026-11-19: "make the GE on power outage glitch and sometimes turn on,
make the power outage text glowing realistically").

The sign (frontend/assets/logo_sign.webp, from fit_pass2.py) is drawn with POWER OUTA lit yellow and the last two
letters, G and E, dead grey. From that one picture this makes three overlays, all on the sign's own 4:3 canvas:
  logo_sign_ge.webp        G and E switched ON: their grey faces recoloured to the lit letters' own yellow, orange
                           and white, the black outline untouched (the page fades / stutters this layer in)
  logo_sign_glow.webp      the light the nine lit letters throw: a tight warm bloom on the letters and a wide spill
                           over the steel plate (and a little past it, into the air); screen-blended
  logo_sign_ge_glow.webp   the same for G and E, shown with them
A letter is a region of the picture closed off by the black outline: the lit ones are the big saturated regions
inside the plate, G and E the two big grey ones at the right of the second row.
usage: python tools/outage/sign_layers.py"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(os.path.dirname(os.path.dirname(HERE)), "frontend", "assets")
LUM = np.array([.299, .587, .114], np.float32)


def halo(mask, plate, ink, tight=9, wide=44):
    """The light a set of lit letters throws: RGBA float (0..1), for a screen blend. It falls on the steel round the
    letters; the letters' own faces and the black outline stay as drawn (washed out, the sign reads milky)."""
    t = ndi.gaussian_filter(mask, tight)
    w = ndi.gaussian_filter(mask, wide)
    w = w / max(w.max(), 1e-6)
    core, outer = np.array([255, 226, 150], np.float32), np.array([255, 138, 32], np.float32)
    rgb = outer + (core - outer) * np.clip(t * 1.15, 0, 1)[..., None]
    a = np.clip(.4 * t + .6 * w ** 1.25, 0, .8)
    a *= 1 - .86 * ndi.gaussian_filter(mask, 1.2)   # the faces are already bright: only a slight lift
    a *= 1 - .72 * ink                               # the outline stays black
    a *= .42 + .58 * plate                   # full on the steel, a fainter haze past its edge
    return np.dstack([rgb / 255, a])


def save(arr, name, size=None):
    im = Image.fromarray((np.clip(arr, 0, 1) * 255 + .5).astype(np.uint8), "RGBA")
    if size:
        im = im.resize(size, Image.LANCZOS)
    p = os.path.join(A, name)
    im.save(p, "WEBP", quality=88, alpha_quality=92, method=6)
    return os.path.getsize(p)


def main():
    im = np.asarray(Image.open(os.path.join(A, "logo_sign.webp")).convert("RGBA")).astype(np.float32)
    H, W = im.shape[:2]
    assert (W, H) == (1200, 900), (W, H)
    rgb, al = im[..., :3], im[..., 3]
    lum = rgb @ LUM
    sat = (rgb.max(-1) - rgb.min(-1)) / np.maximum(rgb.max(-1), 1)
    ink = (lum < 62) & (al > 128)
    lab, n = ndi.label((~ink) & (al > 128))
    lit, dead = np.zeros((H, W), bool), np.zeros((H, W), bool)
    nl = nd = 0
    for i, s in enumerate(ndi.find_objects(lab), 1):
        m = lab[s] == i
        if m.sum() < 10000:
            continue
        y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
        msat, mlum = sat[s][m].mean(), lum[s][m].mean()
        if msat > .6 and y0 > 270 and y1 < 790 and x1 < 990:        # a lit letter (not the bulb, not the stripe)
            lit[s] |= m; nl += 1
        elif msat < .3 and mlum > 112 and x0 > 700 and x1 < 1085 and y0 > 530 and y1 < 790:   # G, E
            dead[s] |= m; nd += 1
    assert (nl, nd) == (9, 2), (nl, nd)
    # the two palettes: each letter is a lighter upper tone, a darker lower one and white glints
    def tones(mask):
        L = lum[mask]
        body = L < 225
        cut = np.median(L[body])
        hi, lo = mask & (lum >= cut) & (lum < 225), mask & (lum < cut)
        return np.median(rgb[hi], 0), np.median(rgb[lo], 0)
    yel, org = tones(lit)
    gl, gd = tones(dead)
    Lgl, Lgd = float(gl @ LUM), float(gd @ LUM)
    print("lit", yel.round().tolist(), org.round().tolist(), " dead", gl.round().tolist(), gd.round().tolist())
    # G and E switched on: grey -> the lit tones by brightness; the soft pixels toward the outline keep their shade
    t_mid = np.clip((lum - Lgd) / max(Lgl - Lgd, 1), 0, 1)[..., None]
    t_hi = np.clip((lum - Lgl) / max(248 - Lgl, 1), 0, 1)[..., None]
    col = org + (yel - org) * t_mid
    col = col + (np.array([255, 255, 255], np.float32) - col) * t_hi ** 1.3
    col = col * np.clip(lum / Lgd, 0, 1)[..., None]
    grow = ndi.binary_dilation(dead, iterations=2)
    a = ndi.gaussian_filter(grow.astype(np.float32), .8)
    a = np.where(dead, 1, a) * (al / 255)
    ge = np.dstack([col / 255, a])
    print("logo_sign_ge.webp", save(ge, "logo_sign_ge.webp"))
    plate = ndi.gaussian_filter((al > 128).astype(np.float32), 2)
    inks = ndi.gaussian_filter(ink.astype(np.float32), 1.2)
    print("logo_sign_glow.webp", save(halo(lit.astype(np.float32), plate, inks), "logo_sign_glow.webp"))
    print("logo_sign_ge_glow.webp", save(halo(dead.astype(np.float32), plate, inks), "logo_sign_ge_glow.webp"))


if __name__ == "__main__":
    main()
