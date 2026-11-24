"""Power Outage: every frontend edit on top of Voodoo on Bourbon's frontend, as exact replacements.

Reads the pristine orleans files in tools/broadway/base/ (zeqpz/orleans ff43083) and writes frontend/. Each edit must
match its base text the stated number of times, so a changed base fails loudly instead of half-applying.
usage: python tools/broadway/reskin_outage.py           (rewrites frontend/index.html and rules.js)
Frame fractions (the frame's opening, measured by tools/broadway/frame_fit.py) are read from art/broadway-src/frame_fit.json."""
import json, os, re
import pass5
import pass6
import pass7

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


FIT = json.load(open(os.path.join(ROOT, "art", "broadway-src", "frame_fit.json")))

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
  @container (max-width: 230px) {   /* a small card (phones): the title stays in the band */
    .fbox .fin { justify-content: flex-start; }
    .fbox h3 { margin-top: 0; font-size: 6.6cqw; }
    .fbox .ficon { margin-top: 3cqw; }
  }
  /* (owner, 2026-11-18) every intro card has its description at every size: the full one on a big card, a short one
     at a size that reads (min 10px) where the card is small - a laptop's or a phone's - instead of none or 9px type */
  .fbox p.fshort { display: none; margin: 2.5cqw 0 0; font-size: max(5.4cqw, 10px); line-height: 1.3; font-weight: 600;
    color: #232a45; -webkit-text-stroke: 0; text-shadow: none; }
  .fbox p.fshort b { color: #B4410A; }
  @container (max-width: 300px) {
    .fbox p.flong { display: none; }
    .fbox p.fshort { display: block; }
    .fbox .ficon { width: 44%; }
  }
  /* (owner, 2026-11-18) the multiplier values stay in the background: behind the symbols, filling the cell, still
     (the corner badges over the symbols are gone) */
'''


def pass2_css(W_, H_, L_, T_):
    """Owner pass 2 (2026-11-18): the throwable breaker, the illustrated bonus button, glowing living Multi values,
    the Xtreme Bonus's own room. W_/H_/L_/T_ are the frame box's calc() terms (the same as #paintframe's)."""
    LV = json.load(open(os.path.join(ROOT, "art", "broadway-src", "lever.json")))
    lx, ly, lw, lh = LV["box"]
    px, py = LV["pivot"]
    return f'''  /* ---- owner pass 2 (2026-11-18) ---- */
  /* the breaker on the frame: click it to spin; it is thrown up (ON) while a round plays and drops back after */
  #leverbox {{ position: absolute; z-index: 4; cursor: pointer; pointer-events: auto; user-select: none;
    left: calc({L_} + {W_} * {lx:.5f}); top: calc({T_} + {H_} * {ly:.5f});
    width: calc({W_} * {lw:.5f}); height: calc({H_} * {lh:.5f}); }}
  #leverbox img {{ position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none;
    transform-origin: {px * 100:.2f}% {py * 100:.2f}%; transform: perspective(260px) rotateX(0deg);
    transition: transform .32s cubic-bezier(.45, 1.45, .5, 1), filter .15s; }}
  /* a real toggle: it rocks over its pivot in the slot (toward you, through edge-on, to pointing up) */
  body.poweron #leverbox img {{ transform: perspective(260px) rotateX(180deg); }}
  /* the power cord: its own box the size of the frame, under the frame (it comes out from under the clamp) */
  #cablebox {{ position: absolute; z-index: 2; pointer-events: none;
    left: calc({L_}); top: calc({T_}); width: calc({W_}); height: calc({H_}); }}
  #cablebox .cablecv {{ position: absolute; pointer-events: none; }}
  #cablebox .cablegrab {{ position: absolute; width: 8%; height: 9%; margin: -4.5% 0 0 -4%; border-radius: 50%;
    pointer-events: auto; cursor: grab; touch-action: none; }}
  #cablebox .cablegrab.held {{ cursor: grabbing; }}
  body.replay #cablebox .cablegrab {{ pointer-events: none; }}
  #leverbox:hover img {{ filter: brightness(1.15) drop-shadow(0 0 6px rgba(255, 213, 74, .6)); }}
  body.replay #leverbox {{ pointer-events: none; cursor: default; }}
  /* the HUD's bonus button is an emblem now (a red power button, a bulb, cash and a BONUS ribbon), not just the word */
  .bonusbtn {{ width: calc(176px * var(--hs, 1)); height: calc(176px * var(--hs, 1)); }}
  .bonusbtn::before {{ display: none; }}
  .bonusbtn::after {{ inset: 0; background-image: url("assets/bonus_icon.webp"); filter: none;
    animation: bonusIconBob 2.6s ease-in-out infinite; }}
  .bonusbtn:hover:not(:disabled)::after {{ filter: brightness(1.12) drop-shadow(0 0 10px rgba(255, 213, 74, .7)); }}
  @keyframes bonusIconBob {{ 0%, 100% {{ translate: 0 0; scale: 1; }} 50% {{ translate: 0 -3%; scale: 1.04; }} }}
  .bonusbtn .bglow {{ display: none; }}
  /* owner pass 3: the multiplier values ARE their colour - the numerals filled with the value's heat colour (green ->
     red -> purple for the max wins: heatHue), their black outline, shade and shine kept (vnum_ink.py) - and they glow
     only slightly, from the lettering itself: nothing underneath them */
  .vg {{ --vg-fill: linear-gradient(color-mix(in srgb, var(--heat, #3FE0FF) 55%, #fff), var(--heat, #3FE0FF) 48%,
      color-mix(in srgb, var(--heat, #3FE0FF) 72%, #000));
    background-size: contain, 100% 100% !important; background-position: center !important; background-repeat: no-repeat !important;
    -webkit-mask: var(--vgm) center / contain no-repeat; mask: var(--vgm) center / contain no-repeat; }}
  .multlayer .gmult::before {{ display: none !important; }}
  .multlayer .gmult {{ filter: drop-shadow(0 0 1.5px color-mix(in srgb, var(--heat, #3FE0FF) 85%, #fff))
      drop-shadow(0 0 4px color-mix(in srgb, var(--heat, #3FE0FF) 55%, transparent)); }}
  .cell.booster .multface .mv .vg {{ animation: vgWave 1.8s ease-in-out infinite; }}
  .cell.booster .multface .mv .vg:nth-child(2) {{ animation-delay: -.15s; }}
  .cell.booster .multface .mv .vg:nth-child(3) {{ animation-delay: -.3s; }}
  .cell.booster .multface .mv .vg:nth-child(4) {{ animation-delay: -.45s; }}
  .cell.booster .multface .mv .vg:nth-child(5) {{ animation-delay: -.6s; }}
  .cell.booster .multface .mv .vg:nth-child(6) {{ animation-delay: -.75s; }}
  .cell.booster .multface .mv .vg:nth-child(7) {{ animation-delay: -.9s; }}
  @keyframes vgWave {{ 0%, 100% {{ translate: 0 0; }} 50% {{ translate: 0 -10%; }} }}
  /* the Surge's own value: just its coloured numerals with the same slight glow (no ring, no plate, no shadow) */
  .cell.booster .multface .mv {{ background: none !important;
    filter: drop-shadow(0 0 1.5px color-mix(in srgb, var(--heat, #3FE0FF) 85%, #fff))
      drop-shadow(0 0 4px color-mix(in srgb, var(--heat, #3FE0FF) 55%, transparent)) !important;
    animation: mvPulse 1.1s ease-in-out infinite alternate; }}
  @keyframes mvPulse {{ from {{ scale: .96; }} to {{ scale: 1.06; }} }}
  .fbox .fmult {{ filter: drop-shadow(0 0 1.5px color-mix(in srgb, var(--heat, #3FE0FF) 85%, #fff)); }}
  @media (prefers-reduced-motion: reduce) {{ .multlayer .gmult::before, .multlayer .gmult .vg, .cell.booster .multface .mv,
    .cell.booster .multface .mv .vg, .bonusbtn::after {{ animation: none; }} }}
  /* the Xtreme Bonus's red emergency room: on its intro screen and on phones too */
  .bonusintro.x .wall {{ background-image: url("assets/bonus_wall_xtreme.webp") !important; }}
  html.mob body.xtreme #bgwall {{ background-image: url("assets/mobile/bg_portrait_xtreme.webp") !important; }}
  html.mob body.xtreme .bonusintro.x .wall {{ background-image: url("assets/mobile/bg_portrait_xtreme.webp") !important; }}
  @media (orientation: landscape) {{
    html.mob body.xtreme #bgwall, html.mob body.xtreme .bonusintro.x .wall {{ background-image: url("assets/mobile/bg_landscape_xtreme.webp") !important; }}
  }}
'''


def pass4_css(W_, H_, L_, T_):
    """Owner pass 4 (2026-11-18): live sparks, the bonus emblem clean at every size, the bar's fixed columns, a
    bigger board."""
    return f'''  /* ---- owner pass 4 (2026-11-18) ---- */
  /* the frayed wire's sparks: the frame's own box, over the frame (frontend/spark.js draws in it) */
  #sparkbox {{ position: absolute; z-index: 6; pointer-events: none;
    left: calc({L_}); top: calc({T_}); width: calc({W_}); height: calc({H_}); }}
  #sparkbox .sparkcv {{ position: absolute; pointer-events: none; }}
  /* a bigger board: the page gives the frame only the room it needs (the margins above), not the 64 px of air over
     it, the 44 under it and the 22 under that */
  .main {{ padding-top: 4px; padding-bottom: 6px; gap: 10px; }}
  .stage {{ padding-bottom: 30px; }}   /* the plug dangles here, just over the bar */
  /* the cord's and the sparks' canvases hang past the frame: they are not page height (fitToScreen measures with
     html.rimmeasure set) - counted, the cord's alone kept the board a fifth smaller than the screen allows */
  html.rimmeasure #cablebox, html.rimmeasure #sparkbox {{ display: none; }}
  /* the bonus emblem is only its picture: nothing behind it, nothing round it, in any state or browser */
  .bonusbtn, .bonusbtn:hover, .bonusbtn:active, .bonusbtn:focus, .bonusbtn:focus-visible, .bonusbtn:disabled {{
    background: none !important; background-color: transparent !important; border: 0 !important; outline: 0 !important;
    box-shadow: none !important; -webkit-tap-highlight-color: transparent; appearance: none; -webkit-appearance: none; }}
  .bonusbtn::before {{ content: none !important; }}
  .bonusbtn::after {{ box-shadow: none; background-color: transparent; }}
  .bonusbtn:hover:not(:disabled)::after {{ filter: brightness(1.14); }}
  /* THE "black box" (owner pass 4): on a window narrow enough for the bar to reach the corner, the bar's dark buttons
     lay over the emblem. hudfit.js moves it wherever that would happen: up onto the bar's left shoulder (.up), and a
     size smaller if the frame is in the way there (.sm) - the bar never covers it */
  .hud .bonusbtn.up {{ bottom: calc(100% + 2px); }}
  .hud .bonusbtn.sm {{ width: calc(118px * var(--hs, 1)); height: calc(118px * var(--hs, 1)); }}
  /* on an upright phone or tablet it sat on the bar's own buttons (their dark shapes boxed it in): it rides in the
     band under the bar, lowered by half its new height (it was half the old 74 px button's), never off the screen */
  @media (max-width: 1100px) and (orientation: portrait) {{
    .hud .bonusbtn {{ width: calc(150px * var(--hs, 1)); height: calc(150px * var(--hs, 1));
      bottom: max(calc(4px / max(var(--fit, 1), .2)), calc((6vh + env(safe-area-inset-bottom, 0px) * .4) / max(var(--fit, 1), .2) - 75px * var(--hs, 1))); }}
  }}
  /* the bar's figures: three fixed columns - BALANCE | WIN | BET - so nothing grows or shifts with the numbers; each
     figure is shrunk to its slot by hudfit.js when it is long */
  .hudbar {{ grid-template-columns: minmax(0, 1fr) calc(218px * var(--hs, 1)) minmax(0, 1fr); column-gap: calc(10px * var(--hs, 1)); }}
  .hudbar > .hudstat:first-child {{ justify-self: stretch; overflow: hidden; }}
  .hudstat.win {{ justify-self: stretch; min-width: 0; box-sizing: border-box; padding: 0 calc(12px * var(--hs, 1)); overflow: hidden; }}
  .hudbar > .hudbet {{ justify-self: stretch; justify-content: flex-end; min-width: 0; }}
  .hudbet .hudstat.bet {{ flex: 1 1 0; min-width: 0; overflow: hidden; }}
  .hudstat .val {{ max-width: 100%; }}
  #balance.long, #balance.vlong, #betVal.long, #betVal.vlong {{ font-size: calc(34px * var(--hs, 1)); }}
  @keyframes winSlotPop {{ 0% {{ scale: 1; }} 30% {{ scale: 1.1; filter: brightness(1.5); }} 100% {{ scale: 1; filter: none; }} }}
  @media (max-width: 1100px) and (orientation: portrait) {{
    .hudbar {{ grid-template-columns: minmax(0, 1fr) calc(150px * var(--hs, 1)) minmax(0, 1fr); column-gap: calc(6px * var(--hs, 1)); }}
    .hudstat.win {{ padding: 0 calc(8px * var(--hs, 1)); min-width: 0; }}
  }}
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

    # the frame: its opening fractions (tools/broadway/frame_fit.py); no skull candle on it
    d.rep('''    width: calc((100% - 36px) / .8273); height: calc((100% - 36px) / .6816);
    left: calc(18px - (100% - 36px) * .10330); top: calc(18px - (100% - 36px) * .22724);''',
          f'''    width: calc((100% - 36px) / {FIT["fw"]:.4f}); height: calc((100% - 36px) / {FIT["fh"]:.4f});
    left: calc(18px - (100% - 36px) * {FIT["kx"]:.5f}); top: calc(18px - (100% - 36px) * {FIT["ky"]:.5f});''')
    d.rep('''  .board { margin: calc(.205 * var(--bh, 781px)) calc(.085 * var(--bw, 963px)); }''',
          f'''  .board {{ margin: calc({FIT["mt"]:.3f} * var(--bh, 781px)) calc({FIT["mr"]:.3f} * var(--bw, 963px)) calc({FIT["mb"]:.3f} * var(--bh, 781px)) calc({FIT["ml"]:.3f} * var(--bw, 963px)); }}
  @media (max-width: 1100px) and (orientation: portrait) {{ .board {{ margin-left: calc({FIT["ml_phone"]:.3f} * var(--bw, 963px)); }} }}
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
    # surge tiers by value (tools/broadway/potion_tiers.py): cyan, green, violet, orange, red-hot; the win figure's ink
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
  /* owner pass 2: soft, realistic candle light - every layer of a candle is driven by its flicker (bgscene.js) */
  #bgscene .bgdark { inset: 0; z-index: 2; opacity: .22; background: radial-gradient(130% 110% at 50% 45%, rgba(4, 6, 18, 0) 30%, rgba(4, 6, 18, .7)); }
  #bgscene .bgglow { z-index: 2; border-radius: 50%; mix-blend-mode: screen; will-change: opacity;
    background: radial-gradient(closest-side, rgba(255, 170, 70, .22), rgba(255, 150, 60, .1) 45%, rgba(255, 140, 50, 0)); }
  #bgscene .bgpool { z-index: 2; border-radius: 50%; mix-blend-mode: screen; will-change: opacity, transform;
    background: radial-gradient(closest-side, rgba(255, 226, 150, .42), rgba(255, 196, 96, .2) 40%, rgba(255, 170, 70, .06) 72%, rgba(255, 170, 70, 0)); }
  #bgscene .bghalo { z-index: 3; border-radius: 50%; mix-blend-mode: screen; will-change: opacity, transform;
    background: radial-gradient(closest-side, rgba(255, 250, 220, .75), rgba(255, 214, 110, .38) 30%, rgba(255, 170, 60, .1) 62%, rgba(255, 170, 60, 0)); }
  #bgscene .bgflame { z-index: 3; transform-origin: 50% 100%; will-change: transform; }
  #bgscene .bgflame svg { display: block; width: 100%; height: 100%; overflow: visible; }
  /* the flashlights: a soft cone with a bright hotspot where it lands, swung from off-screen right (or left) */
  #bgscene .bgbeam { z-index: 4; right: -4%; top: 44%; width: 78%; height: 40%; transform-origin: 100% 50%; opacity: 0;
    mix-blend-mode: screen; will-change: opacity, transform; }
  #bgscene .bgbeam.left { right: auto; left: -4%; transform-origin: 0 50%; }
  #bgscene .bgbeam .cone { position: absolute; inset: 0;
    background: linear-gradient(to left, rgba(255, 246, 210, .5), rgba(255, 240, 190, .2) 45%, rgba(255, 236, 180, .07) 85%, rgba(255, 236, 180, 0));
    clip-path: polygon(100% 46%, 0 4%, 0 96%, 100% 54%);
    -webkit-mask: linear-gradient(transparent, #000 22%, #000 78%, transparent); mask: linear-gradient(transparent, #000 22%, #000 78%, transparent); }
  #bgscene .bgbeam.left .cone { transform: scaleX(-1); }
  #bgscene .bgbeam .spot { position: absolute; left: -6%; top: 6%; width: 30%; height: 88%; border-radius: 50%;
    background: radial-gradient(closest-side, rgba(255, 252, 230, .55), rgba(255, 240, 190, .22) 50%, rgba(255, 236, 180, 0)); }
  #bgscene .bgbeam.left .spot { left: auto; right: -6%; }
  /* the Xtreme Bonus: the red emergency room (its own painting), its alarm beacon turning on the ceiling */
  body.xtreme #bgscene { background-image: url("assets/bonus_wall_xtreme.webp"); }
  #bgscene.xtreme .bgsky, #bgscene.xtreme .bglight, #bgscene.xtreme .bgchand { display: none; }
  #bgscene .bgbeacon { z-index: 4; width: 0; height: 0; display: none; }
  #bgscene.xtreme .bgbeacon { display: block; }
  /* owner pass 5: the light sits on the lamp's glass (scene.json "beacon" = the glass's centre) and turns like a real
     beacon - bgscene.js swings one beam round the lamp's upright axis (scaleX), flares the glass as it passes us and
     lights the wall behind as it passes the wall */
  #bgscene .bgbeacon .lamp { left: -3.4cqh; top: -3.8cqh; width: 6.8cqh; height: 7.6cqh; border-radius: 50%; mix-blend-mode: screen;
    will-change: opacity, transform;
    background: radial-gradient(closest-side, rgba(255, 236, 200, .95), rgba(255, 110, 90, .8) 30%, rgba(255, 40, 40, .4) 60%, rgba(255, 0, 0, 0)); }
  #bgscene .bgbeacon .wash { left: -34cqh; top: -30cqh; width: 68cqh; height: 60cqh; border-radius: 50%; mix-blend-mode: screen;
    will-change: opacity; opacity: .3;
    background: radial-gradient(closest-side, rgba(255, 70, 60, .5), rgba(255, 40, 40, .2) 45%, rgba(255, 30, 30, 0)); }
  #bgscene .bgbeacon .ray { left: 0; top: -17cqh; width: 135cqh; height: 34cqh; transform-origin: 0 50%; mix-blend-mode: screen;
    will-change: opacity, transform; transform: rotate(7deg);
    clip-path: polygon(0 43%, 100% 0, 100% 100%, 0 57%);
    background: linear-gradient(to right, rgba(255, 90, 70, .55), rgba(255, 50, 45, .2) 50%, rgba(255, 40, 40, 0));
    -webkit-mask: linear-gradient(transparent, #000 30%, #000 70%, transparent); mask: linear-gradient(transparent, #000 30%, #000 70%, transparent); }
  @media (prefers-reduced-motion: reduce) { #bgscene .bgcloud { animation: none; } }''')

    # the soundtrack: a sneaky dark-comedy cartoon score (tools/music/cues.py; MUSIC printed by tools/music/build.py)
    d.between("const MUSIC = {   // Voodoo on Bourbon", "const MUSIC_RATE = 48000;", '''const MUSIC = {   // Power Outage: a dark-comedy cartoon score (pizzicato, bassoon, tuba, glockenspiel, muted trumpet, mains hum) - tools/music
  base:  { ogg: "assets/music_base.ogg", aac: "assets/music_base.aac", frames: 3592748, aacStart: 5824, aacFrames: 3599360, bpm: 103.003, bars: 32, level: 0.299 },
  menu:  { ogg: "assets/music_menu.ogg", aac: "assets/music_menu.aac", frames: 2003110, aacStart: 5824, aacFrames: 2009088, bpm: 92.006, bars: 16, level: 0.224 },
  intro: { ogg: "assets/music_intro.ogg", aac: "assets/music_intro.aac", frames: 708709, head: 273683, headLen: 302483, aacStart: 5824, aacFrames: 1017856, bpm: 130.002, bars: 8, level: 0.335 },
  bonus: { ogg: "assets/music_bonus.ogg", aac: "assets/music_bonus.aac", frames: 2878536, aacStart: 5824, aacFrames: 2884608, bpm: 128.026, bars: 32, level: 0.398 },
  total: { ogg: "assets/music_total.ogg", aac: "assets/music_total.aac", frames: 768134, head: 204567, headLen: 262167, aacStart: 5824, aacFrames: 1036288, bpm: 119.968, bars: 8, level: 0.376 },
};
''')
    # the phone tier's frame (four bars) and cropped backing, laid on the new frame's box (art/broadway-src/mobile_fit.json,
    # written by tools/broadway/make_mobile_art.py)
    mf_path = os.path.join(ROOT, "art", "broadway-src", "mobile_fit.json")
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
        d.between("  html.mobart #paintback {\n", "</style>\n<script>\n// (phone art)", css + REVIEW_CSS + pass2_css(W_, H_, L_, T_) + pass4_css(W_, H_, L_, T_) + pass5.CSS + pass6.CSS + pass7.CSS)
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
    # owner pass 2: the breaker is thrown ON while a round plays (button, space, autoplay or the lever itself) and
    # drops back with a click when it ends; the Xtreme Bonus swaps in the red emergency room until the round is over
    d.rep("  state.playing = true; state.skip = false; state.mode = mode;\n  setButtons(false);",
          "  state.playing = true; state.skip = false; state.mode = mode;\n  document.body.classList.add(\"poweron\");   // the breaker on the frame is thrown\n  setButtons(false);")
    d.rep("  state.playing = false; state.skip = false;\n  setButtons(true);\n  return ok;",
          "  state.playing = false; state.skip = false;\n  document.body.classList.remove(\"poweron\", \"xtreme\");   // the breaker drops; back to the dark office\n"
          "  sfx(\"fsTick\");   // its click\n  setButtons(true);\n  return ok;")
    d.rep("    state.fsTotal = spins;\n    await bonusIntro(spins, true);",
          "    state.fsTotal = spins;\n    document.body.classList.add(\"xtreme\");   // the red emergency room for the Xtreme Bonus\n    await bonusIntro(spins, true);")
    d.rep('wander(() => [frame, $("paintback"), $("candleflame"), document.querySelector("#board .sprayrim")].filter(Boolean)',
          'wander(() => [frame, $("paintback"), $("candleflame"), $("leverbox"), $("cablebox"), $("sparkbox"), document.querySelector("#board .sprayrim")].filter(Boolean)')
    # (owner, 2026-11-18) every intro card has a short description too, shown where the card is small
    d.rep('  const box = (icon, title, text) => `<div class="fbox"><div class="fin"><div class="ficon">${icon}</div><h3>${title}</h3><p>${text}</p></div></div>`;',
          '  const box = (icon, title, text, short) => `<div class="fbox"><div class="fin"><div class="ficon">${icon}</div><h3>${title}</h3><p class="flong">${text}</p><p class="fshort">${short}</p></div></div>`;')
    SHORT = [("T(\"Multi\"),", "T(`Lands at <b>x1.25</b> to <b>x1000</b>, clears 5 cells and leaves its value there - winning clusters on them are multiplied.`)"),
             ("T(\"FS scatter \\u00b7 Bonus\"),", "T(`<b>3</b>, <b>4</b> or <b>5</b> award <b>10</b>, <b>12</b> or <b>15</b> free spins. Every value stays for the whole bonus.`)"),
             ("T(\"XFS scatter \\u00b7 Extreme\"),", "T(`<b>2</b> award <b>17</b> Xtreme free spins. Every Multi is <b>x2</b> or more.`)")]
    for title, short in SHORT:
        i = d.s.index(title, d.s.index("const box = (icon, title, text, short)"))   # the intro cards' own calls
        j = d.s.index("`))", i)                          # the end of this card's long text, closing box(
        d.s = d.s[:j] + "`), " + short + ")" + d.s[j + 3:]
    # owner pass 3: the Multi values are coloured by their size - green, through yellow and orange, to red at x100, on
    # to magenta, and purple for the max wins over x500 (heatHue normalised so a hue past red wraps round)
    d.rep("const HEAT_ANCHORS = [[1.25, 100], [3, 75], [5, 58], [10, 45], [20, 32], [50, 18], [100, 8], [500, 0]];   // [value, hue]",
          "const HEAT_ANCHORS = [[1.25, 125], [2, 110], [3, 92], [5, 70], [10, 48], [20, 30], [50, 12], [100, 0], [250, -22], [500, -45]];   // [value, hue]: green -> red -> magenta (owner pass 3)")
    d.rep("  if (v > 500) return HEAT_PURPLE;", "  if (v > 500) return HEAT_PURPLE;   // the max wins: purple")
    d.rep("    if (x <= v1) { const t = Math.log(x / v0) / Math.log(v1 / v0); hue = h0 + (h1 - h0) * t; break; }\n  }\n  return hue;",
          "    if (x <= v1) { const t = Math.log(x / v0) / Math.log(v1 / v0); hue = h0 + (h1 - h0) * t; break; }\n  }\n  return ((hue % 360) + 360) % 360;")
    # the glyphs' boxes: the new numerals' own proportions (the voodoo ones squeezed them), each drawn as its ink over
    # a gradient of the value's colour, masked by its silhouette (tools/broadway/vnum_ink.py)
    from PIL import Image as _I
    def _glyph(m):
        n = m.group(1)
        w, h = _I.open(os.path.join(FRONT, "assets", "vnum", n + ".webp")).size
        return (f'  .vg.g-{n} {{ --vgm: url("assets/vnum/{n}.webp"); aspect-ratio: {w} / {h}; '
                f'background-image: url("assets/vnum/ink_{n}.webp"), var(--vg-fill); }}')
    d.s, c = re.subn(r'  \.vg\.g-(\w+) \{ background-image: url\("assets/vnum/\1\.webp"\); aspect-ratio: \d+ / \d+; \}', _glyph, d.s)
    assert c == 12, c
    # the win figure's multiplier ink follows the same scale (POTION_INK by the Surge's tier)
    d.s = d.s.replace("const POTION_INK = { M: [90, 226, 255], M2: [130, 240, 120], M3: [196, 150, 255], M4: [255, 170, 60], M5: [255, 72, 64] };",
                      "const POTION_INK = { M: [110, 240, 90], M2: [240, 232, 70], M3: [255, 150, 50], M4: [255, 64, 60], M5: [196, 96, 255] };")
    # the power cord's physics (frontend/cable.js; its box is made with the frame's, before this runs)
    d.rep('<script src="boardgl.js"></script>\n', '<script src="boardgl.js"></script>\n<script src="cable.js"></script>\n<script src="spark.js"></script>\n<script src="hudfit.js"></script>\n')
    # what each symbol lands like (tools/sfx/outage_spec.py LAND)
    d.rep('''  H1: "landMask", H2: "landDoll", H3: "landBrass", H4: "landBone", H5: "landPouch", H6: "landGator", H7: "landPastry", L1: "landIron", L2: "landBeads", L3: "landShell", L4: "landPastry", L5: "landWax", L6: "landIron", L7: "landDoubloon", L8: "landTarot", L9: "landBone", L10: "landBrass", M: "landGlass",''',
          '''  H1: "landMask", H2: "landDoll", H3: "landBrass", H4: "landBone", H5: "landPouch", H6: "landGator", H7: "landPastry", L1: "landWax", L3: "landIron", L4: "landShell", M: "landGlass",''')

    # the logo sign hangs at the board's left, like the reference's wooden title board
    d.rep('''  #candleflame {
    position: absolute;''', '''  #logosign {
    position: absolute; z-index: 5; pointer-events: none; user-select: none;
    width: calc(.46 * var(--bw, 963px)); right: calc(100% + .045 * var(--bw, 963px)); top: 4%;
    rotate: -3deg;   /* (owner pass 4) a steel plate bolted on at a tilt: it neither swings nor flickers */
    filter: drop-shadow(0 10px 14px rgba(6, 8, 20, .5));
  }
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
    pass5.apply(d)   # owner pass 5: the alarm, the electric win line
    pass7.apply(d)   # iOS crash at load: the phone tier's preloader
    recolour(d)
    # the logo sign is added next to the frame (it shares the frame's parent, so it moves with the board)
    anchor = 'document.getElementById("paintframe").src = mobArt("assets/frame.webp");'
    d.rep(anchor, anchor + '''
''' + pass5.SIGN_NEW + '''      // the breaker switch on the frame (owner pass 2): its handle is its own picture (tools/broadway/frame_lever.py),
      // thrown with the round (body.poweron); clicking it is the same as pressing Spin
      const lb = document.createElement("div");
      lb.id = "leverbox"; lb.setAttribute("role", "button"); lb.setAttribute("aria-label", "Spin"); lb.title = "Spin";
      lb.innerHTML = '<img src="assets/lever.webp" alt="" draggable="false">';
      lb.addEventListener("click", e => {
        e.stopPropagation();
        if (typeof REPLAY !== "undefined" && REPLAY) return;
        const s = document.getElementById("spinBtn");
        if (s && !s.disabled) s.click();
      });
      if (pf && pf.parentNode) pf.parentNode.appendChild(lb);
      // the dangling power cord's box (frontend/cable.js swings the cord in it with physics)
      const cb = document.createElement("div"); cb.id = "cablebox"; cb.setAttribute("aria-hidden", "true");
      if (pf && pf.parentNode) pf.parentNode.appendChild(cb);
      // the frayed wire's live sparks (frontend/spark.js), over the frame
      const sb = document.createElement("div"); sb.id = "sparkbox"; sb.setAttribute("aria-hidden", "true");
      if (pf && pf.parentNode) pf.parentNode.appendChild(sb);
      // the Xtreme Bonus's room is fetched while the base game plays, so it is there the moment the bonus lands
      if (!window.MOBILE) setTimeout(() => { new Image().src = "assets/bonus_wall_xtreme.webp"; }, 8000); }''')
    d.save()
    rules().save()


if __name__ == "__main__":
    main()
