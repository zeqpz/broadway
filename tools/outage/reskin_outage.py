"""Power Outage: every frontend edit on top of Voodoo on Bourbon's frontend, as exact replacements.

Reads the pristine orleans files in tools/outage/base/ (zeqpz/orleans ff43083) and writes frontend/. Each edit must
match its base text the stated number of times, so a changed base fails loudly instead of half-applying.
usage: python tools/outage/reskin_outage.py           (rewrites frontend/index.html and rules.js)
Frame fractions (the frame's opening, measured by tools/outage/frame_fit.py) are read from art/outage-src/frame_fit.json."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = os.path.join(HERE, "base")
FRONT = os.path.join(ROOT, "frontend")


class Doc:
    def __init__(self, name):
        self.name = name
        self.s = open(os.path.join(BASE, name), encoding="utf-8").read()

    def rep(self, old, new, n=1):
        c = self.s.count(old)
        if c != n:
            raise SystemExit(f"{self.name}: expected {n} x {old[:90]!r}, found {c}")
        self.s = self.s.replace(old, new)

    def between(self, start, end, new):
        """Replace everything from `start` up to (not including) `end` - `start` must be unique."""
        assert self.s.count(start) == 1, start[:80]
        i = self.s.index(start)
        j = self.s.index(end, i)
        self.s = self.s[:i] + new + self.s[j:]

    def save(self):
        with open(os.path.join(FRONT, self.name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(self.s)
        print("wrote", self.name, len(self.s))


FIT = json.load(open(os.path.join(ROOT, "art", "outage-src", "frame_fit.json")))

# ------------------------------------------------------------------------------------------------ colours
# Voodoo's palette -> the blackout's. Mardi Gras gold -> candle yellow; voodoo green -> electric cyan; violet -> warm
# orange; the Extreme accent (lime green) -> electric cyan. Applied last, to whatever is left of the old colours.
COLOURS = [
    ("#F2B230", "#FFD54A"), ("#f2b230", "#ffd54a"), ("242, 178, 48", "255, 213, 74"),
    ("#7CFF6B", "#3FE0FF"), ("#7cff6b", "#3fe0ff"), ("124, 255, 107", "63, 224, 255"), ("124,255,107", "63,224,255"),
    ("124 255 107", "63 224 255"),
    ("#9B5CF0", "#FF9A3C"), ("#9b5cf0", "#ff9a3c"), ("155, 92, 240", "255, 154, 60"), ("155 92 240", "255 154 60"),
    ("#5FE04E", "#3FE0FF"), ("#5fe04e", "#3fe0ff"), ("#C9FFC0", "#C2F4FF"), ("#c9ffc0", "#c2f4ff"),
    ("#3C0C6C", "#0E3A5A"), ("#1F7A2E", "#126A8C"), ("#D8FFCF", "#D6F7FF"), ("#E9C2FF", "#D0F4FF"),
    ("#D6FF6E", "#FFF2B0"), ("#F5C518", "#FFC93C"), ("245, 197, 24", "255, 201, 60"),
    ("150, 255, 130", "255, 242, 176"), ("160,255,140", "170,240,255"), ("190,255,160", "200,246,255"),
    ("220, 255, 210", "220, 248, 255"), ("235, 255, 225", "235, 250, 255"), ("245,255,235", "245,252,255"),
    ("214, 160, 255", "255, 200, 140"), ("199, 125, 255", "255, 170, 90"), ("196,140,255", "255,180,110"),
    ("196, 140, 255", "255, 180, 110"), ("#b98cff", "#ffb36b"), ("#C77BF0", "#FFB36B"), ("#C026D8", "#FF9A3C"),
    ("#5B2A86", "#22305A"), ("#d6c7ea", "#d8e2f4"),
]


# fixes from the stake-approval-reviewer pass (2026-11-18), appended to the last stylesheet so they win
REVIEW_CSS = '''  /* ---- Power Outage review fixes (2026-11-18) ---- */
  /* the feature cards are cream: navy lettering without the black outline, the title in the card's yellow band
     (feature_box.webp: the band runs 3.4%-14.5% down the card) */
  .fbox .fin { left: 10%; right: 10%; top: 3.35%; bottom: 7%; }
  .fbox h3 { order: -1; flex: none; height: 14.2cqw; margin: 0 0 3.5cqw; display: flex; align-items: center; justify-content: center;
    color: #141B33; -webkit-text-stroke: 0; text-shadow: none; font-size: 6.2cqw; }
  .fbox p { color: #232a45; -webkit-text-stroke: 0; text-shadow: none; font-weight: 600; }
  .fbox p b { color: #B4410A; }
  .fbox .ficon img { filter: none; }
  @container (max-width: 230px) {   /* a small card (phones) shows only its icon and title: the title stays in the band */
    .fbox .fin { justify-content: flex-start; }
    .fbox h3 { margin-top: 0; font-size: 6.6cqw; }
    .fbox .ficon { margin-top: 10cqw; }
  }
  /* a cell's value is a badge in the cell's lower-right corner, over the symbol: the chunky symbols covered it */
  .multlayer { z-index: 3; }
  .multlayer .gmult:not(.gone) { opacity: 1; }
  .multlayer .gmult { align-items: flex-end !important; justify-content: flex-end !important; padding: 0 3% 4% 0;
    font-size: calc(var(--boxh, 82) * .3px * var(--shrink, 1)) !important; }
  .multlayer .gmult::before { inset: auto 0 0 auto !important; width: 80%; height: 54%;
    background: radial-gradient(closest-side, rgba(8, 10, 26, .85), rgba(8, 10, 26, .55) 62%, rgba(8, 10, 26, 0)) !important; }
  .multlayer .gmult .vg { filter: none; }
'''


def recolour(d):
    for a, b in COLOURS:
        d.s = d.s.replace(a, b)


# ------------------------------------------------------------------------------------------------ index.html
def index():
    d = Doc("index.html")
    d.rep("<title>Voodoo on Bourbon</title>", "<title>Power Outage</title>")
    d.rep('alt="${T("Voodoo on Bourbon")}"', 'alt="${T("Power Outage")}"')
    for k in ("vol", "muted", "rapid", "hist."):
        d.s = d.s.replace(f'"voodoobourbon.{k}', f'"poweroutage.{k}')

    d.between('const SYM = {\n', '};\n', '''const SYM = {
  M:  { label: "SURGE", sub: "MULTI",      cls: "booster", img: "assets/flat/M.webp" },   // the power surge, its value over it
  BS: { label: "FS",    sub: "BONUS",      cls: "scat",  img: "assets/flat/BS.webp" },
  ES: { label: "XFS",   sub: "EXTREME",    cls: "escat", img: "assets/flat/ES.webp" },
  H1: { label: "PREZ",  sub: "PRESIDENT",  cls: "high", img: "assets/flat/H1.webp" },
  H2: { label: "AGENT", sub: "BODYGUARD",  cls: "high", img: "assets/flat/H2.webp" },
  H3: { label: "CEO",   sub: "BANKRUPT",   cls: "high", img: "assets/flat/H3.webp" },
  H4: { label: "CRASH", sub: "STOCKS",     cls: "high", img: "assets/flat/H4.webp" },
  H5: { label: "PHONE", sub: "HOTLINE",    cls: "high", img: "assets/flat/H5.webp" },
  L1: { label: "CANDLE",sub: "",           cls: "low",  img: "assets/flat/L1.webp" },
  L3: { label: "BATT",  sub: "BATTERY",    cls: "low",  img: "assets/flat/L3.webp" },
  L4: { label: "BULB",  sub: "BLOWN",      cls: "low",  img: "assets/flat/L4.webp" },
  H6: { label: "SERVER",sub: "AI",         cls: "high", img: "assets/flat/H6.webp" },
  H7: { label: "PIGGY", sub: "BROKE",      cls: "high", img: "assets/flat/H7.webp" },
''')
    d.rep('''  H1: "#F2B230", H2: "#c9a26a", H3: "#e8b84a", H4: "#b98cff", H5: "#7CFF6B", H6: "#5fd36a", H7: "#fff3dc",   // voodoo: each symbol's own colour
  L1: "#F2B230", L2: "#9B5CF0", L3: "#ff5a3a", L4: "#a86cff", L5: "#ffd27a", L6: "#9aa0b8", L7: "#ffd24a",
  L8: "#9B5CF0", L9: "#efe6cc", L10: "#ffc95a", M: "#7CFF6B", BS: "#b07cff", ES: "#7CFF6B",''',
          '''  H1: "#FFD54A", H2: "#FFF2B0", H3: "#FF9A3C", H4: "#FF5A5A", H5: "#FF5A5A", H6: "#3FE0FF", H7: "#FF9EC0",   // blackout: each symbol's own colour
  L1: "#FFD54A", L3: "#FF6A5A", L4: "#BFD9FF", M: "#3FE0FF", BS: "#FFD54A", ES: "#3FE0FF",''')

    d.rep("tick(`<b>VOODOO STORM</b> \\u2014 every cell is a Potion`);", "tick(`<b>GRID OVERLOAD</b> \\u2014 every cell is a Surge`);")
    d.rep("tick(`<b>HEX LINE</b> \\u2014 ${cells.length} Potions in a row`);", "tick(`<b>SURGE LINE</b> \\u2014 ${cells.length} Multis in a row`);")
    d.rep("`Potions drop in lines of <b>3</b> or <b>4</b>", "`Multis drop in lines of <b>3</b> or <b>4</b>")
    d.s = d.s.replace("tick(`<b>GRID OVERLOAD</b> \\u2014 every cell is a Surge`);", "tick(`<b>GRID OVERLOAD</b> \\u2014 every cell is a Multi`);")

    # no character: the board stands alone with the logo sign at its left (the reference's layout)
    d.rep('''const CHARACTERS = [
  // Doc, the voodoo showman with his skull cane, beside the board (#charfx; CSS stands him on the left)
  {
    el: "charfx", name: "doc",
    flavour: [["cane_twirl"], ["hat_tip"], ["conjure"]],   // idle breaks: twirls the cane, tips his hat, conjures a wisp
  },
];''', '''const CHARACTERS = [];   // Power Outage has no character beside the board: the logo sign hangs there instead''')
    d.rep('''  if (window.MOBILE) { for (const id of ["charfx", "camnear"]) { const el = $(id); if (el) el.remove(); } return; }   // the mobile tier: no Doc''',
          '''  if (window.MOBILE || !CHARACTERS.length) { for (const id of ["charfx", "camnear"]) { const el = $(id); if (el) el.remove(); } return; }   // no character''')
    d.rep('''<script>if (!window.MOBILE) document.write('<script src="charrig.js"><\\/script>');</script>\n''', "")

    # the frame: its opening fractions (tools/outage/frame_fit.py); no skull candle on it
    d.rep('''    width: calc((100% - 36px) / .8273); height: calc((100% - 36px) / .6816);
    left: calc(18px - (100% - 36px) * .10330); top: calc(18px - (100% - 36px) * .22724);''',
          f'''    width: calc((100% - 36px) / {FIT["fw"]:.4f}); height: calc((100% - 36px) / {FIT["fh"]:.4f});
    left: calc(18px - (100% - 36px) * {FIT["kx"]:.5f}); top: calc(18px - (100% - 36px) * {FIT["ky"]:.5f});''')
    d.rep('''  .board { margin: calc(.205 * var(--bh, 781px)) calc(.085 * var(--bw, 963px)); }''',
          f'''  .board {{ margin: calc({FIT["my"]:.3f} * var(--bh, 781px)) calc({FIT["mx"]:.3f} * var(--bw, 963px)); }}
  #candleflame {{ display: none !important; }}''')

    # the Multi is a power surge: it crackles, swells and flashes white-hot before it blows
    d.between("  @keyframes multiboom {", "  @keyframes multihit {", '''  @keyframes multiboom {   /* Power Outage: the surge crackles, swells and flashes white-hot - then it blows */
    0%   { transform: none; filter: none; }
    12%  { transform: rotate(-6deg) scale(1.06); filter: brightness(1.3) drop-shadow(0 0 8px rgb(63 224 255)); }
    24%  { transform: rotate(6deg) scale(1.1); filter: brightness(1.1) drop-shadow(0 0 4px rgb(63 224 255)); }
    36%  { transform: rotate(-5deg) scale(1.14); filter: brightness(1.8) drop-shadow(0 0 16px rgb(255 213 74)); }
    48%  { transform: rotate(4deg) scale(1.18); filter: brightness(1.2) drop-shadow(0 0 6px rgb(63 224 255)); }
    62%  { transform: rotate(-2deg) scale(1.24); filter: brightness(2.4) drop-shadow(0 0 24px rgb(255 255 240)); }
    100% { transform: none; filter: none; }
  }
''')
    # surge tiers by value (tools/outage/potion_tiers.py): cyan, green, violet, orange, red-hot; the win figure's ink
    d.rep("const POTION_INK = { M: [157, 255, 110], M2: [104, 212, 255], M3: [184, 132, 255], M4: [255, 170, 64], M5: [255, 66, 102] };",
          "const POTION_INK = { M: [90, 226, 255], M2: [130, 240, 120], M3: [196, 150, 255], M4: [255, 170, 60], M5: [255, 72, 64] };")

    # winners ZAP (the reference's bursts, electric): the hex pathway is kept (same canvas, clock and sounds) but it
    # draws a swell, a white-hot flash and a burst of yellow and cyan sparks instead of a burn
    d.rep("const HEX_STEPS = window.MOBILE ? 12 : 16, HEX_PX = window.MOBILE ? 132 : 220, HEX_MS = 900;",
          "const HEX_STEPS = 2, HEX_PX = window.MOBILE ? 132 : 220, HEX_MS = 760;   // Power Outage: only frame 0 (the whole icon) is drawn")
    d.rep('''  gx.fillStyle = "rgba(150, 255, 130, .78)"; gx.fillRect(0, 0, w, h);''',
          '''  gx.fillStyle = "rgba(255, 250, 222, .92)"; gx.fillRect(0, 0, w, h);   // Power Outage: the icon's white-hot flash''')
    d.rep('''  const spirit = (/^M\\d?$/.test(m.name || "") && FLAT.ES && hexKit(FLAT.ES)) || kit;
  bursts.push({ hex: true, from: now, born: now, t, x: c.x, y: c.y, W, kit, drawW, ghost: spirit.ghost, glow: glowSprite("#7CFF6B"),
    vglow: glowSprite("#9B5CF0"), turn: rnd(-1, 1),''',
          '''  const spirit = kit, col = BURST_COLOUR[m.name] || "#FFD54A";
  bursts.push({ hex: true, from: now, born: now, t, x: c.x, y: c.y, W, kit, drawW, ghost: spirit.ghost, glow: glowSprite("#FFD54A"),
    vglow: glowSprite("#3FE0FF"), own: glowSprite(col), turn: rnd(-1, 1),''')
    d.between("function drawHex(ctx, b, now) {", "function burstIcon(m) {", r'''function drawHex(ctx, b, now) {
  // Power Outage: the winner swells with a jittery buzz (0-40%), then shorts out in a flash (40-52%)
  const age = (now - b.born) / b.t, p = age / HEX_MS;
  if (p > .52) return;
  const f = b.kit.frames[0];
  let s, a;
  if (p < .4) { const q = p / .4; s = 1 + .22 * (1 - Math.pow(1 - q, 3)) + .03 * Math.sin(q * 22); a = 1; }
  else { const q = (p - .4) / .12; s = 1.22 + .12 * q; a = 1 - q; }
  const dw = b.drawW * s, dh = dw * b.kit.h / b.kit.w, wob = Math.sin(age / 18) * .06 * b.turn * Math.min(1, p / .4);
  ctx.save();
  ctx.translate(b.x + Math.sin(age / 9) * b.W * .01, b.y); ctx.rotate(wob);
  ctx.globalAlpha = a;
  ctx.drawImage(f, -dw / 2, -dh / 2, dw, dh);
  ctx.restore();
}
function drawHexLight(ctx, b, now) {
  const age = (now - b.born) / b.t;
  if (age > HEX_MS) return;
  const p = age / HEX_MS;
  // the icon heats up white-hot as it swells, flickering like a bulb about to blow
  if (b.ghost && p < .52) {
    const flick = .75 + .25 * Math.sin(age / 23) * Math.sin(age / 7);
    const q = (p < .4 ? Math.pow(p / .4, 1.6) : 1 - (p - .4) / .12) * flick, s = 1 + .22 * Math.min(1, p / .4);
    const dw = b.drawW * s, dh = dw * b.kit.h / b.kit.w;
    ctx.globalAlpha = .85 * q;
    ctx.drawImage(b.ghost, b.x - dw / 2, b.y - dh / 2, dw, dh);
  }
  if (p < .5) { const q = p / .5, gs = b.W * (1 + .5 * q); ctx.globalAlpha = .45 * q; ctx.drawImage(b.own, b.x - gs / 2, b.y - gs / 2, gs, gs); }
  // the short: a white-hot yellow orb that flares and spreads, an electric-cyan ring of light behind it
  if (p > .36) {
    const q = Math.min(1, (p - .36) / .64), e = 1 - Math.pow(1 - q, 3);
    const os = b.W * (.7 + 1.5 * e);
    ctx.globalAlpha = Math.max(0, 1 - q);
    ctx.drawImage(b.glow, b.x - os / 2, b.y - os / 2, os, os);
    const rs = b.W * (.9 + 2.0 * e);
    ctx.globalAlpha = .55 * Math.max(0, 1 - q * 1.2);
    ctx.drawImage(b.vglow, b.x - rs / 2, b.y - rs / 2, rs, rs);
  }
  // sparks: yellow and cyan, thrown out from the short and falling a little
  for (const m of b.motes) {
    const t0 = .38 + (m.at / 380) * .08;
    if (p < t0) continue;
    const q = Math.min(1, (p - t0) / (1 - t0)), e = 1 - Math.pow(1 - q, 2), d = b.W * (.08 + .7 * e) * (m.r / b.W * 2.2);
    ctx.globalAlpha = Math.sin(Math.PI * Math.min(1, q * 1.1));
    const s = m.s * (1.4 - q);
    ctx.drawImage(m.violet ? b.vglow : b.glow, b.x + Math.cos(m.a) * d - s, b.y + Math.sin(m.a) * d - s + b.W * .15 * q * q, s * 2, s * 2);
  }
}
''')

    # the blacked-out office's live layers (frontend/bgscene.js, Power Outage's own)
    d.rep('''  #bgscene::after {   /* a touch darker toward the pavement, so the board reads */
    content: ""; position: absolute; inset: 0; z-index: 5; pointer-events: none;
    background: linear-gradient(rgba(12, 6, 24, .04), rgba(12, 6, 24, .26));
  }''', '''  #bgscene::after {   /* a touch darker toward the floor, so the board reads */
    content: ""; position: absolute; inset: 0; z-index: 5; pointer-events: none;
    background: linear-gradient(rgba(8, 10, 24, 0), rgba(8, 10, 24, .22));
  }
  /* Power Outage: flat cartoon layers over the dark office (bgscene.js places them from assets/bg/scene.json) */
  #bgscene i { position: absolute; display: block; pointer-events: none; }
  #bgscene .bgroom { inset: 0; z-index: 4; opacity: 0; mix-blend-mode: screen; }
  #bgscene .bgchand { z-index: 3; opacity: 0; border-radius: 50%; mix-blend-mode: screen;
    background: radial-gradient(circle, rgba(255, 246, 200, .9) 0 14%, rgba(255, 213, 74, .42) 14% 34%, rgba(255, 213, 74, .16) 34% 60%, rgba(255, 213, 74, 0) 60%); }
  #bgscene .bgsky { z-index: 1; overflow: hidden;
    -webkit-mask: url("assets/bg/sky.webp") center / 100% 100% no-repeat; mask: url("assets/bg/sky.webp") center / 100% 100% no-repeat; }
  #bgscene .bgcloud { left: -35%; opacity: .92; animation: bgcloud var(--dur) linear var(--delay) infinite; }
  #bgscene .bgcloud svg { display: block; width: 100%; height: auto; }
  @keyframes bgcloud { from { left: -35%; } to { left: 110%; } }
  #bgscene .bgflash { position: absolute; inset: 0; width: 100%; height: 100%; opacity: 0; }
  #bgscene .bgbolt { top: 0; width: 7%; height: 78%; opacity: 0; }
  #bgscene .bgbolt svg { display: block; width: 100%; height: 100%; }
  #bgscene .bglight { z-index: 1; background: #FFD54A; opacity: 0; transition: opacity .3s steps(2); }
  #bgscene .bglight.on { opacity: .95; }
  #bgscene .bgpool { z-index: 2; border-radius: 50%; mix-blend-mode: screen;
    background: radial-gradient(circle, rgba(255, 213, 74, .2) 0 52%, rgba(255, 213, 74, .09) 52% 100%);
    animation: bgpool var(--dur) steps(3) infinite alternate; }
  @keyframes bgpool { from { opacity: .5; transform: scale(.94); } to { opacity: 1; transform: scale(1.05); } }
  #bgscene .bgflame { z-index: 3; transform-origin: 50% 100%; animation: bgflame var(--dur) steps(6) var(--delay) infinite; }
  #bgscene .bgflame svg { display: block; width: 100%; height: 100%; overflow: visible; }
  @keyframes bgflame {
    0%, 100% { transform: scale(1, 1) skewX(0); } 20% { transform: scale(.9, 1.1) skewX(-5deg); }
    40% { transform: scale(1.05, .93) skewX(3deg); } 60% { transform: scale(.94, 1.12) skewX(6deg); }
    80% { transform: scale(1.03, .96) skewX(-3deg); }
  }
  #bgscene .bgbeam { z-index: 4; right: -3%; top: 50%; width: 72%; height: 34%; transform-origin: 100% 50%; opacity: 0;
    clip-path: polygon(100% 45%, 0 0, 0 100%, 100% 55%); mix-blend-mode: screen;
    background: linear-gradient(to left, rgba(255, 242, 176, .36), rgba(255, 242, 176, .12)); }
  #bgscene .bgbeam.go { animation: bgbeam 7s ease-in-out 1; }
  @keyframes bgbeam { 0% { opacity: 0; transform: rotate(16deg); } 12%, 86% { opacity: 1; } 50% { transform: rotate(-4deg); }
    100% { opacity: 0; transform: rotate(-20deg); } }
  @media (prefers-reduced-motion: reduce) { #bgscene .bgflame, #bgscene .bgpool, #bgscene .bgcloud { animation: none; } }''')

    # the soundtrack: a sneaky dark-comedy cartoon score (tools/music/cues.py; MUSIC printed by tools/music/build.py)
    d.between("const MUSIC = {   // Voodoo on Bourbon", "const MUSIC_RATE = 48000;", '''const MUSIC = {   // Power Outage: a dark-comedy cartoon score (pizzicato, bassoon, tuba, glockenspiel, muted trumpet, mains hum) - tools/music
  base:  { ogg: "assets/music_base.ogg", aac: "assets/music_base.aac", frames: 3592748, aacStart: 5824, aacFrames: 3599360, bpm: 103.003, bars: 32, level: 0.299 },
  menu:  { ogg: "assets/music_menu.ogg", aac: "assets/music_menu.aac", frames: 2003110, aacStart: 5824, aacFrames: 2009088, bpm: 92.006, bars: 16, level: 0.224 },
  intro: { ogg: "assets/music_intro.ogg", aac: "assets/music_intro.aac", frames: 708709, head: 273683, headLen: 302483, aacStart: 5824, aacFrames: 1017856, bpm: 130.002, bars: 8, level: 0.335 },
  bonus: { ogg: "assets/music_bonus.ogg", aac: "assets/music_bonus.aac", frames: 2878536, aacStart: 5824, aacFrames: 2884608, bpm: 128.026, bars: 32, level: 0.398 },
  total: { ogg: "assets/music_total.ogg", aac: "assets/music_total.aac", frames: 768134, head: 204567, headLen: 262167, aacStart: 5824, aacFrames: 1036288, bpm: 119.968, bars: 8, level: 0.376 },
};
''')
    # the phone tier's frame (four bars) and cropped backing, laid on the new frame's box (art/outage-src/mobile_fit.json,
    # written by tools/outage/make_mobile_art.py)
    mf_path = os.path.join(ROOT, "art", "outage-src", "mobile_fit.json")
    if os.path.exists(mf_path):
        M = json.load(open(mf_path))
        W_ = f"(100% - 36px) / {FIT['fw']:.4f}"
        H_ = f"(100% - 36px) / {FIT['fh']:.4f}"
        L_ = f"18px - (100% - 36px) * {FIT['kx']:.5f}"
        T_ = f"18px - (100% - 36px) * {FIT['ky']:.5f}"
        bx, by, bw, bh = M["back"]
        css = (f"  html.mobart #paintback {{\n    width: calc({W_} * {bw:.5f}); height: calc({H_} * {bh:.5f});\n"
               f"    left: calc({L_} + {W_} * {bx:.5f});\n    top: calc({T_} + {H_} * {by:.5f});\n  }}\n"
               "  html.mobart #paintframe { visibility: hidden; }\n"
               "  html.mobart .fbar { position: absolute; z-index: 3; pointer-events: none; user-select: none; display: block; }\n")
        for k in ("top", "bottom", "left", "right"):
            x, y, w, h = M[k]
            css += (f"  html.mobart .fbar.fb-{k} {{ left: calc({L_} + {W_} * {x:.5f}); top: calc({T_} + {H_} * {y:.5f}); "
                    f"width: calc({W_} * {w:.5f}); height: calc({H_} * {h:.5f}); }}\n")
        d.between("  html.mobart #paintback {\n", "</style>\n<script>\n// (phone art)", css + REVIEW_CSS)
    # the symbols fill their cells like the reference's (the voodoo build drew them at 88% of the cell)
    d.rep("  const w = c.clientWidth * .88, h = c.clientHeight * .88;",
          "  const w = c.clientWidth * 1.2, h = c.clientHeight * 1.2;   // Power Outage: chunky symbols that fill the cell")
    # the shop's volatility pips: lightning bolts, not voodoo skulls
    i = d.s.index("    --drip: url(\"data:image/svg+xml,")
    j = d.s.index("\n", i)
    d.s = d.s[:i] + ("    --drip: url(\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 24'>"
                     "<path d='M12.5 1 3 14h6.2L7 23l10-13.2h-6.3L12.5 1z'/></svg>\");") + d.s[j:]
    d.rep("    /* the volatility pips: simple voodoo skulls (cranium, jaw, two eyes and a nose cut out) - was a paint drip */",
          "    /* the volatility pips: lightning bolts (Power Outage) - were voodoo skulls */")
    # the HUD: a solid midnight-navy cartoon bar with a thick black outline (flat, like the art), candle-yellow accents
    d.rep("--hud-on: #F2B230; --hud-fill: rgba(28, 14, 40, .58); --hud-soft: #d6c7ea; --hud-ink: #f6f0ff;",
          "--hud-on: #F2B230; --hud-fill: rgba(16, 22, 48, .88); --hud-soft: #c9d4ee; --hud-ink: #fbf8ee;")
    d.rep("    fill: var(--hud-fill); stroke: var(--hud-line); stroke-width: 3; stroke-linejoin: round;",
          "    fill: var(--hud-fill); stroke: var(--hud-line); stroke-width: 4; stroke-linejoin: round;")
    # what each symbol lands like (tools/sfx/outage_spec.py LAND)
    d.rep('''  H1: "landMask", H2: "landDoll", H3: "landBrass", H4: "landBone", H5: "landPouch", H6: "landGator", H7: "landPastry", L1: "landIron", L2: "landBeads", L3: "landShell", L4: "landPastry", L5: "landWax", L6: "landIron", L7: "landDoubloon", L8: "landTarot", L9: "landBone", L10: "landBrass", M: "landGlass",''',
          '''  H1: "landMask", H2: "landDoll", H3: "landBrass", H4: "landBone", H5: "landPouch", H6: "landGator", H7: "landPastry", L1: "landWax", L3: "landIron", L4: "landShell", M: "landGlass",''')

    # the logo sign hangs at the board's left, like the reference's wooden title board
    d.rep('''  #candleflame {
    position: absolute;''', '''  #logosign {
    position: absolute; z-index: 5; pointer-events: none; user-select: none;
    width: calc(.46 * var(--bw, 963px)); right: calc(100% + .045 * var(--bw, 963px)); top: 4%;
    transform-origin: 50% 0; animation: logosway 5s ease-in-out infinite alternate, logoflicker 7s steps(1) infinite;
    filter: drop-shadow(0 10px 14px rgba(6, 8, 20, .5));
  }
  @keyframes logosway { from { rotate: -1.8deg; } to { rotate: 1.5deg; } }
  @keyframes logoflicker {   /* the sign's bulb is dying: now and then the whole sign dips as the power stutters */
    0%, 61%, 63.5%, 66%, 100% { opacity: 1; } 62% { opacity: .55; } 64.5% { opacity: .7; }
  }
  @media (prefers-reduced-motion: reduce) { #logosign { animation: none; } }
  @media (max-aspect-ratio: 3/2) { #logosign { display: none; } }   /* (review: at 4:3 it ran off-screen / over the rail) */
  html.mob #logosign { display: none; }
  #candleflame {
    position: absolute;''')
    return d


def rules():
    d = Doc("rules.js")
    d.rep('''    H1: "Mardi Gras Mask", H2: "Voodoo Doll", H3: "Jazz Trumpet", H4: "Candle Skull", H5: "Gris-Gris Bag",
    H6: "Bayou Gator", H7: "Beignets",
    L1: "Fleur-de-lis", L2: "Mardi Gras Beads", L3: "Crawfish", L4: "King Cake", L5: "Candle",
    L6: "Skeleton Key", L7: "Doubloon", L8: "Tarot Card", L9: "Bone", L10: "Gas Lamp",''',
          '''    H1: "The President", H2: "The Bodyguard", H3: "Bankrupt CEO", H4: "Market Crash", H5: "Red Hotline",
    H6: "AI Server", H7: "Broke Piggy Bank",
    L1: "Candle", L3: "Dead Battery", L4: "Blown Bulb",''')
    d.rep("Voodoo on Bourbon is a 5-reel", "Power Outage is a 5-reel")
    d.rep('${t("Hex Line and Voodoo Storm")}', '${t("Surge Line and Grid Overload")}')
    d.rep('"Hex Line: a straight line of 3 or 4 Multis', '"Surge Line: a straight line of 3 or 4 Multis')
    d.rep("any spin, and far more often in a bonus. Voodoo Storm: very rarely",
          "any spin, and far more often in a bonus. Grid Overload: very rarely")
    d.s = d.s.replace("Hex Lines", "Surge Lines")
    d.rep("math-sdk/games/voodoo_5x5/game_config.py", "math-sdk/games/outage_5x5/game_config.py")
    return d


def boardgl():
    d = Doc("boardgl.js")
    # the symbols fill their cells like the reference's: the icon's footprint fills 1.2 of the box, not .88
    d.rep("        const sR = Math.min(b.cw * .88 / rw, b.ch * .88 / rh);",
          "        const sR = Math.min(b.cw * 1.2 / rw, b.ch * 1.2 / rh);   // Power Outage: chunky symbols (was .88)")
    return d


def main():
    boardgl().save()
    d = index()
    recolour(d)
    # the logo sign is added next to the frame (it shares the frame's parent, so it moves with the board)
    anchor = 'document.getElementById("paintframe").src = mobArt("assets/frame.webp");'
    d.rep(anchor, anchor + '''
    { const pf = document.getElementById("paintframe"), sign = document.createElement("img");   // Power Outage: the title board
      sign.id = "logosign"; sign.alt = ""; sign.draggable = false; sign.src = "assets/logo_sign.webp";
      if (pf && pf.parentNode && !window.MOBILE) pf.parentNode.appendChild(sign); }''')
    d.save()
    rules().save()


if __name__ == "__main__":
    main()
