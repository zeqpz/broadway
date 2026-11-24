"""One-off: turn Power Outage's symanim.py personality tables into Broadway on Nashville's (asserted exact edits).
The Gold Record (M) spins like a record on a turntable in every clip; music notes float up off the paying symbols."""
import os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blender", "symanim.py")
s = open(p, encoding="utf-8").read()


def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:90])
    s = s.replace(old, new)


rep('"""Power Outage symbols, animated in Blender', '"""Broadway on Nashville symbols, animated in Blender')
rep('''GLOW = {                                                      # halo colour per tier (candle yellow, warm orange, electric cyan)
    1: (1.0, 0.84, 0.3), 2: (1.0, 0.62, 0.26), "M": (0.25, 0.88, 1.0), "BS": (1.0, 0.86, 0.32),
    "ES": (0.25, 0.88, 1.0), 0: (1.0, 0.95, 0.8)}''',
    '''GLOW = {                                                      # halo colour per tier (marquee amber, neon pink, record gold, neon blue)
    1: (1.0, 0.76, 0.23), 2: (1.0, 0.3, 0.66), "M": (1.0, 0.8, 0.32), "BS": (1.0, 0.3, 0.66),
    "ES": (0.22, 0.66, 1.0), 0: (1.0, 0.95, 0.85)}''')
start = s.index("P = {          # idle")
end = s.index("}\n", s.index('"ES": dict(idle', start)) + 2
s = s[:start] + '''P = {          # idle (breath, sway deg, bend deg, bob, cycles), softness, effects, hit style
    "H1": dict(idle=(.025, .9, 1.3, .03, 2), soft=1.0, fx=["straw", "sparkle"], hit="jiggle"),        # the Crooner: croons, notes float up
    "H2": dict(idle=(.03, 1.6, 1.8, .03, 2), soft=1.1, fx=["sparkle", "feather"], hit="hop"),          # the Bachelorette: woo! jumps
    "H3": dict(idle=(.02, 2.2, 1.6, .03, 2), soft=.9, fx=["feather", "straw"], hit="jiggle"),          # the Fiddler: saws away
    "H4": dict(idle=(.02, 1.4, 1.2, .04, 2), soft=.7, fx=["steam", "puff"], hit="bounce"),             # Mechanical Bull: snorts, bucks
    "H5": dict(idle=(.02, 1.0, 1.4, .02, 2), soft=.8, fx=["steam", "leaf"], hit="jiggle"),             # Hot Chicken: steams, flames fly
    "H6": dict(idle=(.015, 1.2, 1.0, .03, 1), soft=.6, fx=["sparkle", "crumb"], hit="hop"),            # Rhinestone Boot: stomps
    "H7": dict(idle=(.02, 1.6, 1.2, .03, 2), soft=.7, fx=["straw", "feather"], hit="wobbletop"),       # Banjo: twangs
    "L1": dict(idle=(.015, 0.0, .9, .02, 1), soft=.6, fx=["sparkle"], hit="jiggle"),                   # Horseshoe
    "L3": dict(idle=(.02, 1.6, .8, .03, 1), soft=.7, fx=["straw"], hit="hop"),                         # Guitar Pick
    "L4": dict(idle=(.02, 1.4, .7, .03, 1), soft=.7, fx=["feather", "sparkle"], hit="wobbletop"),      # Harmonica
    "M": dict(idle=(.008, 0.0, 0.0, .015, 1), soft=.5, fx=["sparkle", "straw"], hit="pop"),            # Gold Record: spins
    "BS": dict(idle=(.025, 1.8, 1.4, .04, 2), soft=.9, fx=["sparkle", "crumb"], hit="jiggle"),         # FS: the marquee star
    "ES": dict(idle=(.03, 1.2, 2.6, .02, 3), soft=1.1, fx=["straw", "glint"], hit="wobbletop"),        # XFS: the jukebox
}
SPIN = -360.0                                                 # the record turns once a loop (72 f = 2.4 s, ~25 rpm)
''' + s[end:]
# idle: the record spins; the notes RISE (they used to be falling straws / sparks)
rep('''        if sid == "L5":                                       # the sunflower turns slowly like a wheel
            pose["root"]["r"] = 6 * math.sin(2 * math.pi * t)''',
    '''        if sid == "L5":                                       # the sunflower turns slowly like a wheel
            pose["root"]["r"] = 6 * math.sin(2 * math.pi * t)
        if sid == "M":                                        # the Gold Record turns on its spindle
            pose["spin"] = dict(r=SPIN * t)''')
rep('''            elif kind == "straw" and k < 2:
                x0 = rng.uniform(-3, 3)
                pools[kind].particle(fs, fs + 18, lambda t, x0=x0: (x0 + t, 2.5 - 4 * t * t), rng, spin=300,
                                     grow=(.5, .5), fade=(1, 0))''',
    '''            elif kind == "straw" and k < 2:                   # a music note floats up and drifts away
                x0 = rng.uniform(-3, 3)
                pools[kind].particle(fs, fs + 20, lambda t, x0=x0: (x0 + .6 * math.sin(t * 6), 2.0 + 3.0 * t), rng,
                                     spin=rng.choice([-1, 1]) * 30, grow=(.45, .55), fade=(1, 0))''')
rep('''            elif kind == "feather" and k == 1:
                x0 = rng.uniform(-2, 2)
                pools[kind].particle(fs, fs + 20, lambda t, x0=x0: (x0 + .9 * math.sin(t * 7), 1.0 - 4 * t), rng,
                                     spin=160, grow=(.6, .55), fade=(1, 0))''',
    '''            elif kind == "feather" and k == 1:                # a pair of notes floats up
                x0 = rng.uniform(-2, 2)
                pools[kind].particle(fs, fs + 20, lambda t, x0=x0: (x0 + .8 * math.sin(t * 5), 1.8 + 3.2 * t), rng,
                                     spin=rng.choice([-1, 1]) * 25, grow=(.5, .6), fade=(1, 0))''')
rep('''    if sid == "M" and "straw" in pools:                       # the surge crackles all the time: sparks jump off its rim
        for j, fs in enumerate(range(f0 + 1, f0 + n - 8, 6)):
            a = rng.uniform(0, 2 * math.pi)
            x0, z0 = 4.3 * math.cos(a), 4.3 * math.sin(a)
            pools["straw"].particle(fs, fs + 6, lambda t, x0=x0, z0=z0, a=a: (x0 + math.cos(a) * .9 * t, z0 + math.sin(a) * .9 * t),
                                    rng, spin=rng.choice([-1, 1]) * 60, grow=(.7, .35), fade=(1, 1))''',
    '''    if sid == "M" and "straw" in pools:                       # the record plays: a note lifts off its rim now and then
        for j, fs in enumerate(range(f0 + 4, f0 + n - 20, 16)):
            a = rng.uniform(.35, 2.8)
            x0, z0 = 4.0 * math.cos(a), 3.4 * math.sin(a)
            pools["straw"].particle(fs, fs + 18, lambda t, x0=x0, z0=z0: (x0 + .5 * math.sin(t * 5), z0 + 2.4 * t),
                                    rng, spin=rng.choice([-1, 1]) * 25, grow=(.5, .45), fade=(1, 0))''')
# the burst: notes float instead of falling like crumbs
rep('''                g = 9 if kind not in ("leaf", "feather") else 4''',
    '''                g = 9 if kind not in ("leaf", "feather", "straw") else 3''')
rep('''                                     fade=(1, 0) if kind in ("leaf", "feather") else (1, 1))''',
    '''                                     fade=(1, 0) if kind in ("leaf", "feather", "straw") else (1, 1))''')
# land: the record lands spinning (a quarter turn that ends on rest)
rep('''        if i == n:
            pose = dict(root={}, b1={}, b2={})
        pose.setdefault("b0", {})''',
    '''        if i == n:
            pose = dict(root={}, b1={}, b2={})
        if sid == "M" and 0 < i < n:                          # drops onto the platter still turning
            pose["root"]["r"] = SPIN * .5 * (1 - ease_out(i / n))
        pose.setdefault("b0", {})''')
# multi: the record winds up to a fast spin while it charges, then lets go
rep('''        else:                                                   # release: punch out then settle
            t = (i - 18) / FPS
            k = damp(t, 3.4, .3)
            pose = dict(root=dict(sx=1 + .16 * soft * k, sy=1 + .1 * k, y=.15 * k),
                        b2=dict(r=-5 * soft * damp(t, 2.6, .3)))''',
    '''        else:                                                   # release: punch out then settle
            t = (i - 18) / FPS
            k = damp(t, 3.4, .3)
            pose = dict(root=dict(sx=1 + .16 * soft * k, sy=1 + .1 * k, y=.15 * k),
                        b2=dict(r=-5 * soft * damp(t, 2.6, .3)))
        if sid == "M" and i < n:                                # it winds up to a fast spin: two turns, ends on rest
            pose["root"]["r"] = pose["root"].get("r", 0) + 2 * SPIN * ease_in_out(i / n)
            if i < 18:
                pose["b2"] = {}''')
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched", p)
