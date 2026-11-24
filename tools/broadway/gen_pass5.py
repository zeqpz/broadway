"""Owner pass 5b (2026-11-19): the title sign LIT, as an OLED / LED sign ("when the GE flickers we want it to look like
it has an OLED light on it ... the power outage still needs a glow so it looks like an OLED sign").

One redraw of the steel sign (ui/logo_sign3.png) with all eleven letters switched on as luminous light panels - and no
glow painted on the plate: the light the letters throw is added live by the page (tools/broadway/sign_layers.py), so it
can hum and the last two letters can flicker. Two takes; sign_layers.py reads the one copied to ui/logo_sign_led.png.
usage: python tools/broadway/gen_pass5.py [a b ...]"""
import os, sys, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg
RAW = os.path.join(orimg.ROOT, "art", "broadway-src", "ui")
P = ("Redraw the attached title sign EXACTLY: the same riveted grey steel plate, the same yellow-and-black hazard stripe "
     "along its bottom edge, the same cracked light bulb with cyan sparks on its top-right corner, and the same chunky "
     "POWER / OUTAGE lettering - the same letter shapes, sizes, tilts and positions, the same thick black outline round "
     "every letter. The ONLY change is the light: all eleven letters, INCLUDING the last G and E, are now SWITCHED ON as "
     "the glowing letters of an illuminated OLED / LED sign at night. Each letter's face is a luminous light panel: "
     "white-hot pale yellow across its middle, deepening smoothly to rich saturated amber and orange toward its edges, "
     "with a thin bright hot rim just inside the black outline, so the letter looks lit from inside, like a light you "
     "could not look straight at. No grey letters: G and E are lit exactly like the other nine. Keep the small white "
     "glint on each letter. Do NOT paint any glow, halo, rays, haze or light spill outside the letters or on the steel "
     "plate - the plate stays plain flat steel grey exactly as in the attached picture, and the black outlines stay "
     "solid black. Only the two words POWER and OUTAGE, no other text. Clean chunky cartoon with thick black outlines, "
     "crisp edges. Transparent background.")


def one(tag):
    out, cost = orimg.generate(os.path.join(RAW, f"logo_sign_led_{tag}.png"), P, aspect="4:3",
                               refs=[os.path.join(RAW, "logo_sign3.png")])
    print("OK", tag, cost, flush=True)


ts = [threading.Thread(target=one, args=(t,)) for t in (sys.argv[1:] or ["a", "b"])]
[t.start() for t in ts]
[t.join() for t in ts]
