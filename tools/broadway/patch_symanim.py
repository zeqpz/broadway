"""One-off: turn the (Miami-patched) symanim.py personality tables into Power Outage's (asserted exact edits)."""
import os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blender", "symanim.py")
s = open(p, encoding="utf-8").read()


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)


rep('"""Miami Getaway symbols, animated in Blender', '"""Power Outage symbols, animated in Blender')
rep('''GLOW = {                                                      # halo colour per tier (sunset gold, hot pink, aqua)
    1: (1.0, 0.8, 0.3), 2: (1.0, 0.42, 0.72), "M": (1.0, 0.36, 0.7), "BS": (0.36, 0.95, 0.9),
    "ES": (1.0, 0.72, 0.25), 0: (1.0, 0.95, 0.85)}''',
    '''GLOW = {                                                      # halo colour per tier (candle yellow, warm orange, electric cyan)
    1: (1.0, 0.84, 0.3), 2: (1.0, 0.62, 0.26), "M": (0.25, 0.88, 1.0), "BS": (1.0, 0.86, 0.32),
    "ES": (0.25, 0.88, 1.0), 0: (1.0, 0.95, 0.8)}''')
start = s.index("P = {          # idle")
end = s.index("}\n", s.index('"ES": dict(idle', start)) + 2
s = s[:start] + '''P = {          # idle (bob, sway Hz, breathe Hz, lean, harmonics), softness, effects, hit style
    "H1": dict(idle=(.025, .9, 1.3, .03, 2), soft=1.0, fx=["coin", "sparkle"], hit="jiggle"),        # the President: blusters, coins fly
    "H2": dict(idle=(.015, .7, 1.0, .02, 1), soft=.6, fx=["glint", "sparkle"], hit="hiccup"),         # bodyguard: flashlight jitters
    "H3": dict(idle=(.03, 1.4, 1.8, .03, 2), soft=1.1, fx=["drop", "feather"], hit="hop"),            # bankrupt CEO: sweats, moth flies
    "H4": dict(idle=(.015, 1.8, 1.2, .02, 2), soft=.6, fx=["leaf", "crumb"], hit="hiccup"),           # crashing chart: arrows + glass
    "H5": dict(idle=(.02, 3.0, 2.4, .02, 1), soft=.8, fx=["sparkle", "straw"], hit="hiccup"),         # hotline phone: rattles
    "H6": dict(idle=(.015, 1.2, 1.0, .02, 1), soft=.7, fx=["steam", "straw"], hit="wobbletop"),       # AI server: smokes and sparks
    "H7": dict(idle=(.03, 1.0, 1.6, .03, 2), soft=1.2, fx=["coin", "sparkle"], hit="bounce"),         # broke piggy: last coins out
    "L1": dict(idle=(.015, 0.0, .9, .02, 1), soft=.6, fx=["sparkle"], hit="jiggle"),                  # candle
    "L3": dict(idle=(.02, 1.6, .8, .03, 1), soft=.7, fx=["straw"], hit="hop"),                        # dying battery
    "L4": dict(idle=(.02, 1.4, .7, .04, 1), soft=.7, fx=["crumb", "sparkle"], hit="wobbletop"),       # blown bulb
    "M": dict(idle=(.02, 2.0, 1.4, .02, 2), soft=.8, fx=["straw", "sparkle"], hit="pop"),             # power surge: crackles
    "BS": dict(idle=(.025, 1.8, 1.4, .04, 2), soft=.9, fx=["sparkle", "straw"], hit="jiggle"),        # FS: the bulb comes on
    "ES": dict(idle=(.03, 1.2, 2.6, .02, 3), soft=1.1, fx=["straw", "glint"], hit="wobbletop"),       # XFS: high voltage
}
''' + s[end:]
# idle: sparks crackle off the surge badge's rim (replaces the Miami bomb's fuse fizz)
rep('''    if sid == "M" and "sparkle" in pools:                     # the fuse fizzes all the time: sparks spit off its tip
        tip = (2.55, 3.85)
        for j, fs in enumerate(range(f0 + 1, f0 + n - 8, 5)):
            a = math.radians(rng.uniform(20, 160))
            sp = rng.uniform(1.4, 2.4)
            pools["sparkle"].particle(fs, fs + 7, lambda t, a=a, sp=sp: (tip[0] + math.cos(a) * sp * t,
                                      tip[1] + math.sin(a) * sp * t - 1.2 * t * t), rng, spin=200,
                                      grow=(.55, .1), fade=(1, 1))''',
    '''    if sid == "M" and "straw" in pools:                       # the surge crackles all the time: sparks jump off its rim
        for j, fs in enumerate(range(f0 + 1, f0 + n - 8, 6)):
            a = rng.uniform(0, 2 * math.pi)
            x0, z0 = 4.3 * math.cos(a), 4.3 * math.sin(a)
            pools["straw"].particle(fs, fs + 6, lambda t, x0=x0, z0=z0, a=a: (x0 + math.cos(a) * .9 * t, z0 + math.sin(a) * .9 * t),
                                    rng, spin=rng.choice([-1, 1]) * 60, grow=(.7, .35), fade=(1, 1))''')
rep('''            elif kind in ("sparkle", "glint") and k < 2 and sid == "M":
                pass                                          # the bomb's fuse fizz is keyed below''',
    '''            elif kind in ("sparkle", "glint") and k < 2 and sid == "M":
                pass                                          # the surge's crackle is keyed below''')
rep('''    if sid == "M" and "puff" in pools:                          # the bomb goes off: a smoke puff each side''',
    '''    if sid == "M" and "puff" in pools:                          # (unused: the surge has no smoke)''')
open(p, "w", encoding="utf-8").write(s)
print("patched", p)
