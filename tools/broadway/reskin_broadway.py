"""Broadway on Nashville: every frontend edit on top of Power Outage's frontend (zeqpz/poweroutage e9f5c03, the
iOS-fixed build), as exact replacements.

Reads the pristine Power Outage files in tools/broadway/base/ and writes frontend/. Each edit must match its base text
the stated number of times, so a changed base fails loudly instead of half-applying.
Kept exactly (owner): the HUD, the bonus buy menu (panel, cards, buttons - only its banner pictures are new art) and the
black-and-white SMUKIEZ introduction.
usage: python tools/broadway/reskin_broadway.py      (rewrites frontend/index.html and frontend/rules.js)"""
import os, re

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
            raise SystemExit(f"{self.name}: expected {n} x {old[:100]!r}, found {c}")
        self.s = self.s.replace(old, new)

    def between(self, start, end, new):
        """Replace everything from `start` up to (not including) `end` - `start` must be unique."""
        assert self.s.count(start) == 1, (self.name, start[:80], self.s.count(start))
        i = self.s.index(start)
        j = self.s.index(end, i)
        self.s = self.s[:i] + new + self.s[j:]

    def save(self):
        with open(os.path.join(FRONT, self.name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(self.s)
        print("wrote", self.name, len(self.s))


d = Doc("index.html")

# ------------------------------------------------------------------------------------------------ title
d.rep("<title>Power Outage</title>", "<title>Broadway on Nashville</title>")
d.rep('alt="${T("Power Outage")}"', 'alt="${T("Broadway on Nashville")}"')

# ------------------------------------------------------------------------------------------------ scripts
# no breaker cord or frayed-wire sparks - and no character rig (owner, 2026-11-24: "get rid of the character")
d.rep('<script src="cable.js"></script>\n<script src="spark.js"></script>\n', '')

# ------------------------------------------------------------------------------------------------ the title sign, no breaker
d.between('    { const pf = document.getElementById("paintframe"), sign = document.createElement("div");   // Power Outage: the title board',
          '    </script>\n    <div class="ticker" id="ticker">',
          '''    { const pf = document.getElementById("paintframe"), sign = document.createElement("div");   // Broadway: the neon title sign
      sign.id = "logosign"; sign.setAttribute("aria-hidden", "true");
      // the sign as drawn with ON dark, the light its lit tubes throw, and ON switched on with its own light
      // (tools/broadway/sign_layers_bw.py; phones never show the sign: its pictures are not even fetched there)
      if (pf && pf.parentNode && !window.MOBILE) {
        sign.innerHTML = '<img class="base" src="assets/logo_sign.webp" alt="" draggable="false"><img class="glow" src="assets/logo_sign_glow.webp" alt="" draggable="false">'
          + '<img class="ge" src="assets/logo_sign_ge.webp" alt="" draggable="false"><img class="geglow" src="assets/logo_sign_ge_glow.webp" alt="" draggable="false">';
        pf.parentNode.appendChild(sign);
      }
      // ON has a loose contact: it is lit most of the time, and every few seconds it stutters, drops out and catches
      // again; on a big moment (bgscene.js "bgpower") it blinks with the street. --ge is how lit it is, 0..1
      if (sign.parentNode && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
        const ge = v => sign.style.setProperty("--ge", v);
        ge(1);
        let busy = false;
        const play = (steps, then) => {
          busy = true;
          let t = 0;
          for (const [ms, v] of steps) { setTimeout(() => ge(v), t); t += ms; }
          setTimeout(() => { ge(1); busy = false; if (then) then(); }, t);
        };
        const stutter = n => {
          const s = [];
          for (let i = 0; i < n; i++) { s.push([28 + Math.random() * 70, Math.random() < .3 ? .15 : 0]); s.push([45 + Math.random() * 170, (.7 + Math.random() * .3).toFixed(2)]); }
          return s;
        };
        const idle = () => setTimeout(() => {
          if (document.hidden || busy) return idle();
          const steps = stutter(2 + Math.floor(Math.random() * 4));
          if (Math.random() < .3) steps.push([600 + Math.random() * 1400, 0], ...stutter(1 + Math.floor(Math.random() * 2)));
          play(steps, idle);
        }, 2200 + Math.random() * 5200);
        idle();
        addEventListener("bgpower", () => { if (!busy) play([[110, 0], [80, 1], [110, 0], [80, 1], [90, 0], [60, 1]]); });
      } else if (sign.parentNode) sign.style.setProperty("--ge", 1);
      // the Xtreme Bonus's rooftop is fetched while the base game plays, so it is there the moment the bonus lands
      if (!window.MOBILE) setTimeout(() => { new Image().src = "assets/bonus_wall_xtreme.webp"; }, 8000); }
''')
d.rep('document.body.classList.add("poweron");   // the breaker on the frame is thrown',
      'document.body.classList.add("poweron");   // (kept: the class some styles key on while a round plays)')

# ------------------------------------------------------------------------------------------------ no character
# (owner, 2026-11-24: "get rid of the character".) Rosie the cowgirl stood on the left of the board as a live rig
# (tools/broadway/blender/rosie_rig.py, frontend/charrig.js) with a still on phones. She is out of the game: no rig, no
# stills, no reactions - the empty stage of the bar shows where she stood. Her pipeline stays in tools/ and art/.
d.rep("const CHARACTERS = [];   // Power Outage has no character beside the board: the logo sign hangs there instead",
      "const CHARACTERS = [];   // Broadway has no character beside the board (owner, 2026-11-24): the bar's empty stage shows there")

# ------------------------------------------------------------------------------------------------ words on the board
d.rep("tick(`<b>MULTI x${fmtMult(b.mult)}</b> hits ${(b.cells || []).length} cells`);",
      "tick(`<b>GOLD RECORD x${fmtMult(b.mult)}</b> hits ${(b.cells || []).length} cells`);")
d.rep("tick(`<b>GRID OVERLOAD</b> \\u2014 every cell is a Multi`);", "tick(`<b>SOLD-OUT SHOW</b> \\u2014 every cell is a Gold Record`);")
d.rep("tick(`<b>SURGE LINE</b> \\u2014 ${cells.length} Multis in a row`);", "tick(`<b>HIT PARADE</b> \\u2014 ${cells.length} Gold Records in a row`);")
d.rep('''  { mode: "bonus", key: "fs", title: "Free Spins", desc: "10, 12 or 15 free spins. Multis stay all bonus.", heat: 3, acc: "#FFD54A", icon: () => SYM.BS.img },
  { mode: "extremebonus", key: "xfs", title: "Xtreme Spins", desc: "17 free spins. Every Multi is x2 or more.", heat: 5, acc: "#3FE0FF", icon: () => SYM.ES.img, x: true },''',
      '''  { mode: "bonus", key: "fs", title: "Free Spins", desc: "10, 12 or 15 free spins. Record values stay all bonus.", heat: 3, acc: "#FFD54A", icon: () => SYM.BS.img },
  { mode: "extremebonus", key: "xfs", title: "Xtreme Spins", desc: "17 free spins. Every Gold Record is x2 or more.", heat: 5, acc: "#3FE0FF", icon: () => SYM.ES.img, x: true },''')

# each symbol's own light (the win burst, the glow)
d.rep('''  H1: "#FFD54A", H2: "#FFF2B0", H3: "#FF9A3C", H4: "#FF5A5A", H5: "#FF5A5A", H6: "#3FE0FF", H7: "#FF9EC0",   // blackout: each symbol's own colour
  L1: "#FFD54A", L3: "#FF6A5A", L4: "#BFD9FF", M: "#3FE0FF", BS: "#FFD54A", ES: "#3FE0FF",''',
      '''  H1: "#FFC23A", H2: "#FF3FA4", H3: "#FFB04A", H4: "#FF6A3A", H5: "#FF5A2A", H6: "#FF3B3B", H7: "#FFF0C8",   // Broadway: each symbol's own neon
  L1: "#FFC23A", L3: "#FF4A5A", L4: "#7FC8FF", M: "#FFD45A", BS: "#FF3FA4", ES: "#2FA8FF",''')

# ------------------------------------------------------------------------------------------------ sounds + music
d.rep('''  xfsAlarm: "assets/sfx_xfs_alarm.wav", xtremeAlarm: "assets/sfx_xtreme_alarm.wav",
};''', '''  xfsAlarm: "assets/sfx_xfs_alarm.wav", xtremeAlarm: "assets/sfx_xtreme_alarm.wav",
  // Encore (Broadway): the guitar riff, the spotlight landing, a symbol flipping, the crowd
  encoreRiff: "assets/sfx_encore_riff.wav", spotlight: "assets/sfx_spotlight.wav", flip: "assets/sfx_flip.wav",
  crowdCheer: "assets/sfx_crowd_cheer.wav",
};''')
d.rep("  dripLand: .3, xfsAlarm: .5, xtremeAlarm: .55,\n",
      "  dripLand: .3, xfsAlarm: .5, xtremeAlarm: .55, encoreRiff: .6, spotlight: .5, flip: .32, crowdCheer: .5,\n")
mt = open(os.path.join(HERE, "music_table.txt"), encoding="utf-8").read()
m0 = mt.index("\nconst MUSIC = {") + 1   # (the header prose mentions "const MUSIC = {" too: the table starts a line)
music = mt[m0:mt.index("};", m0) + 2]
d.between("const MUSIC = {   // Power Outage:", "\n", music.split("\n")[0])
start = d.s.index(music.split("\n")[0])
end = d.s.index("};", start) + 2
d.s = d.s[:start] + music + d.s[end:]

# ------------------------------------------------------------------------------------------------ Encore
d.rep('''  async setWin() { await delay(120); },''', '''  // Encore (Broadway on Nashville): the board had stopped paying; a guitar riff strikes up, a stage spotlight sweeps
  // the board and lands, and every copy of one regular symbol (ev.from) turns into the Headliner (ev.to), one after
  // another; the clusters the new board makes are paid by the events that follow (winInfo, tumbleBoard, booster...)
  async encore(ev) { await encoreShow(ev); },

  async setWin() { await delay(120); },''')
d.rep('''/** Animate a round's event stream, then settle it.''', '''// ---- Encore: the spotlight, the neon ENCORE! and the flips (the symbols change on the board's own cells)
const ENCORE_FLIP_GAP = 85;      // ms between one flip and the next
async function encoreShow(ev) {
  const at = p => ({ r: p.reel, y: Math.min(Math.max(p.row - 1, 0), ROWS - 1) });
  const cells = (ev.positions || []).map(at).filter(c => cellEls[c.r] && cellEls[c.r][c.y]);
  const to = ev.to, label = s => (SYM[s] || { label: s }).label;
  sfx("encoreRiff");
  tick(`<b>ENCORE!</b> \\u2014 every ${label(ev.from)} turns into ${label(to)}`);
  const board = $("board");
  let spot = null, title = null;
  if (!REDUCED_MOTION) {
    title = document.createElement("div");
    title.className = "encoretitle";
    title.innerHTML = `<span>${T("ENCORE!")}</span>`;
    board.appendChild(title);
    if (!window.MOBILE) {            // a board-sized moving light: never on a phone (iOS layers)
      spot = document.createElement("div");
      spot.className = "encorespot";
      spot.innerHTML = "<i></i>";
      board.appendChild(spot);
    }
  }
  if (spot) { await hold(40); spot.classList.add("on"); }
  await hold(REDUCED_MOTION ? 200 : 900);
  sfx("spotlight");
  if (spot) spot.classList.add("land");
  await hold(260);
  for (const [k, c] of cells.entries()) {
    const el = cellEls[c.r][c.y];
    if (!REDUCED_MOTION) { el.classList.remove("eflipin"); restyle(el); el.classList.add("eflipout"); }
    sfx("flip", 1 + .04 * k);
    setTimeout(() => {
      const prev = shownSym[c.r] && shownSym[c.r][c.y] ? shownSym[c.r][c.y] : {};
      setCell(c.r, c.y, Object.assign({}, prev, { name: to }));
      if (!REDUCED_MOTION) { el.classList.add("eflipin"); winFx(el); }
      rigPlay(el, "land");
    }, REDUCED_MOTION ? 0 : 170);
    await hold(ENCORE_FLIP_GAP);
  }
  await hold(420);
  sfx("crowdCheer");
  if (window.WallFX && WallFX.surge) WallFX.surge(.6, 900);
  await hold(520);
  for (const c of cells) cellEls[c.r][c.y].classList.remove("eflipout", "eflipin");
  if (spot) { spot.classList.add("off"); setTimeout(() => spot.remove(), 600); }
  if (title) { title.classList.add("off"); setTimeout(() => title.remove(), 500); }
}

/** Animate a round's event stream, then settle it.''')

# ------------------------------------------------------------------------------------------------ features screen
d.between('''      box(`<img src="${SYM.M.img}" alt="${T("Multi")}" draggable="false">''', '''    `</div>` +
    `<div class="fcont"><span class="fhit">''', '''      box(`<img src="${SYM.M.img}" alt="${T("Gold Record")}" draggable="false"><div class="fmult" id="featMult" aria-label="x${fmtMult(FEATURE_VALUES[0])}">${[..."x" + fmtMult(FEATURE_VALUES[0])].map(ch => `<i class="vg g-${VGLYPH[ch] || ch}"></i>`).join("")}</div>`,
        T("Gold Record \\u00b7 Multi"),
        T(`Lands with a value from <b>x1.25</b> to <b>x1000</b> - its disc shows how much: bronze, silver, gold, platinum, diamond. Every winning cluster is {paid|counted} first; then it goes off and leaves its value on five cells, and a cluster on those cells is multiplied by their sum.`),
        T(`Values <b>x1.25</b> to <b>x1000</b>, left on five cells; clusters on them are multiplied.`)) +
      box(`<img src="${mobArt("assets/flat/encore_icon.webp")}" alt="${T("Encore")}" draggable="false">`,
        T("Encore!"),
        T(`When the board stops {paying|winning}, the crowd can call an <b>Encore</b>: the spotlight lands on a top symbol and every copy of one regular symbol on the board turns into it - then the board is {paid|counted} again. More often in the bonus.`),
        T(`An Encore turns every copy of one regular symbol into a top symbol.`)) +
      box(`<img src="${mobArt(SYM.BS.img)}" alt="${T("FS scatter")}" draggable="false"><img src="${mobArt(SYM.ES.img)}" alt="${T("XFS scatter")}" draggable="false">`,
        T("FS \\u00b7 XFS \\u00b7 Free Spins"),
        T(`<b>3</b>, <b>4</b> or <b>5</b> FS award <b>10</b>, <b>12</b> or <b>15</b> free spins; <b>2</b> XFS award <b>17</b> Xtreme spins where every Gold Record is <b>x2</b> or more. Every value stays on the board for the whole bonus.`),
        T(`<b>3+</b> FS: 10-15 free spins. <b>2</b> XFS: 17 Xtreme spins.`)) +
''')

# ------------------------------------------------------------------------------------------------ CSS
BW_CSS = """
  /* ==== Broadway on Nashville (2026-11-22) ============================================================ */
  /* the neon title sign stands to the RIGHT of the board (the bar's stage shows on the left); a slight tilt, no swing */
  #logosign { right: auto; left: calc(100% + .05 * var(--bw, 963px)); top: 6%; rotate: 2.5deg; width: calc(.44 * var(--bw, 963px)); }
  #logosign .ge, #logosign .geglow { opacity: var(--ge, 1); }
  /* the street: neon "off" patches and the bulbs' chase groups over the lit painting (bgscene.js) */
  #bgscene .bgstreet, #bgscene .bgroof { position: absolute; inset: 0; pointer-events: none; }
  #bgscene .bgoff { position: absolute; display: block; opacity: 0; pointer-events: none; user-select: none; }
  #bgscene .bgstar { position: absolute; width: .32%; aspect-ratio: 1; margin: -.16%; border-radius: 50%; background: #FFF6D8;
    box-shadow: 0 0 6px 2px rgba(255, 246, 216, .6); scale: var(--s, 1); animation: bgtwinkle var(--d, 3s) ease-in-out var(--o, 0s) infinite; }
  @keyframes bgtwinkle { 0%, 100% { opacity: .25; } 50% { opacity: 1; } }
  #bgscene .bgroof { display: none; }
  #bgscene.xtreme .bgroof { display: block; }
  #bgscene.xtreme .bgstreet { display: none; }
  #bgscene .bgfw { position: absolute; display: block; pointer-events: none; animation: bgfw 1.6s cubic-bezier(.2, .8, .3, 1) forwards; }
  #bgscene .bgfw svg { display: block; width: 100%; height: 100%; overflow: visible; }
  @keyframes bgfw { 0% { transform: scale(.1); opacity: 1; } 55% { opacity: 1; } 100% { transform: scale(1.15) translateY(6%); opacity: 0; } }
  #bgscene .bgbeam2 { position: absolute; bottom: 30%; width: 22%; height: 95%; transform-origin: 50% 100%; mix-blend-mode: screen;
    background: linear-gradient(to top, rgba(255, 246, 220, .5), rgba(255, 240, 200, .16) 60%, rgba(255, 240, 200, 0));
    clip-path: polygon(44% 100%, 56% 100%, 100% 0, 0 0); pointer-events: none; }
  #bgscene .bgbeam2.l { left: 8%; }
  #bgscene .bgbeam2.r { right: 8%; }
  @media (prefers-reduced-motion: reduce) { #bgscene .bgstar { animation: none; } }
  /* ---- inside the bar (2026-11-23): the small things that move (bgscene.js places them from scene.json "props") ---- */
  #bgscene { container-type: size; }
  #bgscene .bgstreet > i, #bgscene .bgstreet > i b { position: absolute; display: block; pointer-events: none; }
  /* a ceiling fan: a top view of its blades turning, flattened to how it looks from the floor; rod, housing and lamp over it */
  #bgscene .bgfan .bgf-disc { inset: 0; transform: scaleY(.2); }
  #bgscene .bgfan .bgf-spin { inset: 0; animation: bgfan var(--d, 3.4s) linear var(--o, 0s) infinite; }
  #bgscene .bgfan .bgf-spin svg { display: block; width: 100%; height: 100%; overflow: visible; }
  @keyframes bgfan { to { transform: rotate(360deg); } }
  #bgscene .bgfan .bgf-rod { left: 48.6%; width: 2.8%; top: 28%; height: 22%; background: #2a1a12; box-shadow: 0 0 0 2px #111; }
  #bgscene .bgfan .bgf-hub { left: 41%; width: 18%; top: 46.5%; height: 8%; border-radius: 50%; background: #C9A040; box-shadow: 0 0 0 2.5px #111, inset 0 -3px 0 #9a7426; }
  #bgscene .bgfan .bgf-lamp { left: 46.2%; width: 7.6%; top: 53.4%; height: 5%; border-radius: 0 0 50% 50% / 0 0 100% 100%; background: #FFF2C0;
    box-shadow: 0 0 0 2px #111, 0 6px 14px 4px rgba(255, 226, 150, .45); }
  /* the jukebox's lit tubes, cut from the painting: they run through the colours */
  #bgscene .bgjuke { position: absolute; display: block; pointer-events: none; user-select: none; animation: bgjuke 11s linear infinite; }
  @keyframes bgjuke { to { filter: hue-rotate(360deg); } }
  /* a shine across each gold record, one after another, every nine seconds */
  #bgscene .bgrec { border-radius: 50%; overflow: hidden; }
  #bgscene .bgrec b { top: -20%; bottom: -20%; left: 0; width: 34%; transform: translateX(-160%) skewX(-22deg);
    background: linear-gradient(to right, rgba(255, 255, 255, 0), rgba(255, 252, 232, .75), rgba(255, 255, 255, 0));
    animation: bgrec 9s ease-in-out var(--o, 0s) infinite; }
  @keyframes bgrec { 0%, 82% { transform: translateX(-160%) skewX(-22deg); } 96%, 100% { transform: translateX(420%) skewX(-22deg); } }
  /* the stage lights' beams: a soft cone of the lens's colour hung from the lamp; it sways and swells (dust drifts in it) */
  #bgscene .bgbeam { transform-origin: 50% 0; rotate: var(--r, 0deg); mix-blend-mode: screen; opacity: .2;
    clip-path: polygon(44% 0, 56% 0, 100% 100%, 0 100%);
    background: linear-gradient(to bottom, var(--c, #fff), color-mix(in srgb, var(--c, #fff) 55%, transparent) 55%, transparent);
    animation: bgbeam var(--d, 8s) ease-in-out var(--o, 0s) infinite alternate; }
  @keyframes bgbeam { from { transform: rotate(-5deg); opacity: .14; } to { transform: rotate(6deg); opacity: .36; } }
  #bgscene .bgmote { width: .2cqw; height: .2cqw; margin: -.1cqw; border-radius: 50%; background: #FFF3CF; opacity: 0; scale: var(--s, 1);
    animation: bgmote var(--d, 10s) linear var(--o, 0s) infinite; }
  @keyframes bgmote { 0% { transform: translate(0, 0); opacity: 0; } 15% { opacity: var(--a, .5); } 80% { opacity: var(--a, .5); }
    100% { transform: translate(var(--dx, 0), var(--dy, -4cqh)); opacity: 0; } }
  /* a glint on a bottle */
  #bgscene .bgglint { width: 1.1cqw; height: 1.1cqw; margin: -.55cqw; opacity: 0; animation: bgglint var(--d, 5s) ease-in-out var(--o, 0s) infinite; }
  #bgscene .bgglint svg { display: block; width: 100%; height: 100%; }
  @keyframes bgglint { 0%, 68% { transform: scale(0) rotate(0deg); opacity: 0; } 80% { transform: scale(1) rotate(30deg); opacity: 1; }
    92%, 100% { transform: scale(0) rotate(60deg); opacity: 0; } }
  /* steam off the coffee pot: three wavy lines rising, one after another */
  #bgscene .bgsteam { width: .9cqw; height: 4.4cqh; margin: -4.4cqh 0 0 -.45cqw; opacity: 0; transform-origin: 50% 100%;
    animation: bgsteam var(--d, 3s) ease-out var(--o, 0s) infinite; }
  #bgscene .bgsteam svg { display: block; width: 100%; height: 100%; }
  @keyframes bgsteam { 0% { transform: translateY(18%) scale(calc(.6 * var(--k, 1)), .5); opacity: 0; } 25% { opacity: .62; }
    100% { transform: translateY(-62%) scale(calc(1.25 * var(--k, 1)), 1.15); opacity: 0; } }
  #bgscene.still .bgfan .bgf-spin, #bgscene.still .bgjuke, #bgscene.still .bgrec b { animation: none; }
  /* Encore: the neon ENCORE! over the board and the stage spotlight that sweeps it (desktop only) */
  .encoretitle { position: absolute; left: 50%; top: -9.5%; z-index: 40; translate: -50% 0; pointer-events: none;
    font: 900 calc(.11 * var(--bw, 963px)) / 1 "Fredoka", system-ui, sans-serif; letter-spacing: .02em; color: #FFF0FA;
    -webkit-text-stroke: calc(.006 * var(--bw, 963px)) #FF3FA4;
    text-shadow: 0 0 calc(.01 * var(--bw, 963px)) #FF3FA4, 0 0 calc(.03 * var(--bw, 963px)) #FF3FA4, 0 calc(.008 * var(--bw, 963px)) 0 #2a0820;
    animation: encorein .5s cubic-bezier(.2, 1.6, .4, 1) both; }
  .encoretitle.off { animation: encoreout .45s ease-in forwards; }
  @keyframes encorein { 0% { transform: scale(.3) rotate(-8deg); opacity: 0; } 100% { transform: none; opacity: 1; } }
  @keyframes encoreout { to { transform: scale(1.2); opacity: 0; } }
  html.mob .encoretitle { text-shadow: 0 calc(.008 * var(--bw, 963px)) 0 #2a0820; }
  .encorespot { position: absolute; inset: -12% -6% -2%; z-index: 35; pointer-events: none; opacity: 0; overflow: hidden;
    transition: opacity .3s ease; }
  .encorespot.on { opacity: 1; }
  .encorespot.off { opacity: 0; transition: opacity .5s ease; }
  .encorespot i { position: absolute; top: -30%; left: 50%; width: 52%; height: 140%; translate: -50% 0; mix-blend-mode: screen;
    transform-origin: 50% 0; rotate: -26deg;
    background: radial-gradient(60% 18% at 50% 92%, rgba(255, 250, 230, .55), rgba(255, 244, 210, 0) 70%),
                linear-gradient(to bottom, rgba(255, 248, 220, .05), rgba(255, 244, 210, .32) 70%, rgba(255, 244, 210, .12));
    clip-path: polygon(42% 0, 58% 0, 100% 100%, 0 100%); }
  .encorespot.on i { animation: encoresweep .9s ease-in-out forwards; }
  .encorespot.land i { animation: none; rotate: 0deg; }
  @keyframes encoresweep { 0% { rotate: -26deg; } 60% { rotate: 18deg; } 100% { rotate: 0deg; } }
  .cell.eflipout { animation: eflipout .17s ease-in forwards; }
  .cell.eflipin { animation: eflipin .34s cubic-bezier(.2, 1.5, .4, 1) both; }
  @keyframes eflipout { from { transform: none; } to { transform: scale(.06, 1.1); } }
  @keyframes eflipin { from { transform: scale(.06, 1.1); } to { transform: none; } }
  html.reduced .cell.eflipout, html.reduced .cell.eflipin { animation: none; }
  /* the title sign on a phone (phoneSign): one still picture (assets/mobile/logo_sign_phone.webp, ON lit), no glow
     layers, centred over the board */
  #phonesign { display: none; }
  @media (orientation: portrait) {
    html.mob #phonesign { display: block; position: absolute; z-index: 2; left: 50%; translate: -50% 0; bottom: 103%; width: 62%; height: auto;
      pointer-events: none; user-select: none; rotate: -1.5deg; }
  }
"""
d.rep("</style>\n</head>", BW_CSS + "</style>\n</head>", 1) if d.s.count("</style>\n</head>") == 1 else None
if BW_CSS not in d.s:   # the page's last stylesheet ends elsewhere: put the block before the first </head>
    i = d.s.index("</head>")
    d.s = d.s[:i] + "<style>" + BW_CSS + "</style>\n" + d.s[i:]

# ------------------------------------------------------------------------------------------------ the frame's fit
# The honky-tonk frame is symmetrical with no cords or levers hanging off it: its opening's fractions
# (tools/broadway/frame_fit.py) replace Power Outage's everywhere they were written, the board's margins follow its
# overhang, and the phone copies' cut boxes come from tools/broadway/make_mobile_art.py.
import json as _json
FIT = _json.load(open(os.path.join(ROOT, "art", "broadway-src", "frame_fit.json")))
for old, new in (("/ 0.7164", f"/ {FIT['fw']:.4f}"), ("/ 0.5979", f"/ {FIT['fh']:.4f}"),
                 ("* 0.17766", f"* {FIT['kx']:.5f}"), ("* 0.32489", f"* {FIT['ky']:.5f}")):
    assert d.s.count(old) >= 4, (old, d.s.count(old))
    d.s = d.s.replace(old, new)
MT, MB, ML, MR = .17, .165, .125, .125
d.rep("  .board { margin: calc(0.262 * var(--bh, 781px)) calc(0.185 * var(--bw, 963px)) calc(0.120 * var(--bh, 781px)) calc(0.155 * var(--bw, 963px)); }",
      f"  .board {{ margin: calc({MT:.3f} * var(--bh, 781px)) calc({MR:.3f} * var(--bw, 963px)) calc({MB:.3f} * var(--bh, 781px)) calc({ML:.3f} * var(--bw, 963px)); }}")
MF = _json.load(open(os.path.join(ROOT, "art", "broadway-src", "mobile_fit.json")))
W_ = f"(100% - 36px) / {FIT['fw']:.4f}"
H_ = f"(100% - 36px) / {FIT['fh']:.4f}"
L_ = f"18px - (100% - 36px) * {FIT['kx']:.5f}"
T_ = f"18px - (100% - 36px) * {FIT['ky']:.5f}"
bx = MF["back"]
mob = (f"  html.mobart #paintback {{\n    width: calc({W_} * {bx[2]:.5f}); height: calc({H_} * {bx[3]:.5f});\n"
       f"    left: calc({L_} + {W_} * {bx[0]:.5f});\n    top: calc({T_} + {H_} * {bx[1]:.5f});\n  }}\n"
       "  html.mobart #paintframe { visibility: hidden; }\n"
       "  html.mobart .fbar { position: absolute; z-index: 3; pointer-events: none; user-select: none; display: block; }\n")
for k in ("top", "bottom", "left", "right"):
    x, y, w, h = MF[k]
    mob += (f"  html.mobart .fbar.fb-{k} {{ left: calc({L_} + {W_} * {x:.5f}); top: calc({T_} + {H_} * {y:.5f}); "
            f"width: calc({W_} * {w:.5f}); height: calc({H_} * {h:.5f}); }}\n")
d.between("  html.mobart #paintback {\n", "  /* ---- Power Outage review fixes (2026-11-18) ---- */", mob)
# the Multi numerals' aspect ratios, read off the new glyph files (tools/broadway/vnum.py)
from PIL import Image as _Image
for g in ("x", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "dot"):
    w, h = _Image.open(os.path.join(FRONT, "assets", "vnum", g + ".webp")).size
    d.s, n = re.subn(r'(\.vg\.g-' + re.escape(g) + r' \{ --vgm: url\("assets/vnum/' + re.escape(g) + r'\.webp"\); aspect-ratio: )\d+ / \d+',
                     lambda m: f"{m.group(1)}{w} / {h}", d.s)
    assert n >= 1, g


# ------------------------------------------------------------------------------------------------ the title sign on a phone
# A phone never fetches the desktop sign's four layers: it shows one still picture of the sign (ON lit) over the board.
# Portrait phones only. (Rosie's still poses stood beside it until 2026-11-24.)
d.rep("""  if (window.MOBILE || !CHARACTERS.length) { for (const id of ["charfx", "camnear"]) { const el = $(id); if (el) el.remove(); } return; }   // no character""",
      """  if (window.MOBILE || !CHARACTERS.length) {   // no character canvas
    for (const id of ["charfx", "camnear"]) { const el = $(id); if (el) el.remove(); }
    if (window.MOBILE) phoneSign();
    return;
  }""")
d.rep("""// the loading screen waits for both characters (their walk-on and idle decoded)""",
      """// the title sign on a phone: one still picture over the board (no layers, nothing moving)
function phoneSign() {
  const board = $("board");
  if (!board) return;
  const sign = document.createElement("img");
  sign.id = "phonesign"; sign.alt = ""; sign.draggable = false; sign.setAttribute("aria-hidden", "true");
  sign.src = "assets/mobile/logo_sign_phone.webp";
  board.appendChild(sign);
}

// the loading screen waits for both characters (their walk-on and idle decoded)""")


# ------------------------------------------------------------------------------------------------ the win line: a neon tube
# Power Outage struck a jagged electric bolt symbol to symbol and kept it crackling; on Broadway the line is a NEON
# TUBE: it still draws itself symbol to symbol, but it bends gently (no jags, forks, second strand or sparks), hums
# rather than crackles, and glows hot pink round a white core.
i0 = d.s.index("function drawWinLine(positions) {")
i1 = d.s.index("\nfunction ", i0 + 10)
wl = d.s[i0:i1]
for a, b in (('gp.lineJoin = "miter"; gp.miterLimit = 4; gp.lineCap = "round";   // sharp kinks, like a bolt',
              'gp.lineJoin = "round"; gp.lineCap = "round";   // a bent glass tube: no kinks'),
             ("let amp = Math.min(26, Math.hypot(seg[1].x - seg[0].x, seg[1].y - seg[0].y) * .2);",
              "let amp = Math.min(5, Math.hypot(seg[1].x - seg[0].x, seg[1].y - seg[0].y) * .035);"),
             ("const f = [], n = Math.min(7, 2 + Math.floor(path.length / 2));", "const f = [], n = 0;   // (no forks off a neon tube)"),
             ("T = rnd() < .7 ? bolt() : null;", "T = null;"),
             ("const i = hot > 1 ? 1 : .68 + rnd() * .32;   // the arc's own flicker", "const i = hot > 1 ? 1 : .9 + rnd() * .1;   // the tube's hum"),
             ("JIT = PH ? 110 : 55;", "JIT = PH ? 1400 : 900;"),
             ('    if (PH) return;\n    const b = document.createElement("b")', '    if (PH || true) return;   // (a neon tube throws no sparks)\n    const b = document.createElement("b")'),
             ("rgba(63, 224, 255", "rgba(255, 63, 164"), ("rgba(150, 238, 255", "rgba(255, 150, 210"),
             ("rgba(120, 232, 255", "rgba(255, 140, 200"), ("rgba(225, 250, 255", "rgba(255, 228, 244"),
             ("rgba(250, 254, 255", "rgba(255, 250, 252"), ("rgba(248, 253, 255, 1)", "rgba(255, 250, 253, 1)")):
    assert wl.count(a) >= 1, ("drawWinLine", a[:60])
    wl = wl.replace(a, b)
d.s = d.s[:i0] + wl + d.s[i1:]
# the winners' light: gold and hot pink (was candle yellow and electric cyan)
d.rep('glow: glowSprite("#FFD54A"),\n    vglow: glowSprite("#3FE0FF"),', 'glow: glowSprite("#FFC23A"),\n    vglow: glowSprite("#FF3FA4"),')

# Power Outage's window-sky mask is gone (the street has no window): its url() would be fetched by the preloader
assert d.s.count('url("assets/bg/sky.webp")') == 2
d.s = d.s.replace('-webkit-mask: url("assets/bg/sky.webp") center / 100% 100% no-repeat; mask: url("assets/bg/sky.webp") center / 100% 100% no-repeat;', '')
assert 'assets/bg/sky.webp' not in d.s

# ------------------------------------------------------------------------------------------------ approval review fixes
# (stake-approval-reviewer pass, 2026-11-22)
# the symbol table's labels (the hidden ticker, fallback alt texts) were Power Outage's
d.between('  M:  { label: "SURGE", sub: "MULTI",      cls: "booster", img: "assets/flat/M.webp" },   // the power surge, its value over it',
          '};\n// The 5x5 game', '''  M:  { label: "GOLD RECORD", sub: "MULTI", cls: "booster", img: "assets/flat/M.webp" },   // the Gold Record, its value over it
  BS: { label: "FS",    sub: "BONUS",      cls: "scat",  img: "assets/flat/BS.webp" },
  ES: { label: "XFS",   sub: "EXTREME",    cls: "escat", img: "assets/flat/ES.webp" },
  H1: { label: "CROONER", sub: "THE CROONER", cls: "high", img: "assets/flat/H1.webp" },
  H2: { label: "BRIDE", sub: "BACHELORETTE", cls: "high", img: "assets/flat/H2.webp" },
  H3: { label: "FIDDLER", sub: "THE FIDDLER", cls: "high", img: "assets/flat/H3.webp" },
  H4: { label: "BULL",  sub: "MECHANICAL", cls: "high", img: "assets/flat/H4.webp" },
  H5: { label: "CHICKEN", sub: "HOT",      cls: "high", img: "assets/flat/H5.webp" },
  L1: { label: "HORSESHOE", sub: "",       cls: "low",  img: "assets/flat/L1.webp" },
  L3: { label: "PICK",  sub: "GUITAR",     cls: "low",  img: "assets/flat/L3.webp" },
  L4: { label: "HARMONICA", sub: "",       cls: "low",  img: "assets/flat/L4.webp" },
  H6: { label: "BOOT",  sub: "RHINESTONE", cls: "high", img: "assets/flat/H6.webp" },
  H7: { label: "BANJO", sub: "",           cls: "high", img: "assets/flat/H7.webp" },
''')
# saved settings and the recent-rounds history under the game's own name (they shared Power Outage's on one CDN origin)
assert d.s.count('"poweroutage.') >= 6
d.s = d.s.replace('"poweroutage.', '"broadway.')
# the hidden ticker's developer line
d.rep('<div class="ticker" id="ticker">Draws come from the optimized 96.7% RTP lookup tables — the real math.</div>',
      '<div class="ticker" id="ticker"></div>')
# the feature cards' short texts fit a 400 x 225 popout
d.rep("T(`Values <b>x1.25</b> to <b>x1000</b>, left on five cells; clusters on them are multiplied.`)",
      "T(`<b>x1.25</b> to <b>x1000</b> on five cells.`)")
d.rep("T(`An Encore turns every copy of one regular symbol into a top symbol.`)",
      "T(`One regular symbol turns into a top one.`)")
d.rep("T(`<b>3+</b> FS: 10-15 free spins. <b>2</b> XFS: 17 Xtreme spins.`)",
      "T(`<b>3+</b> FS: 10-15 spins. <b>2</b> XFS: 17.`)")
# the bonus intro's "how it works": Gold Records, Hit Parades, Tips and the Encore - and nothing the math does not do
d.between('function bonusIntroHow(extreme) {', '\nfunction bonusIntro(spins, extreme) {', '''function bonusIntroHow(extreme) {
  return `<p><strong>${T("How the Gold Records work in here")}</strong></p>` +
    `<p>${T(`A Gold Record lands with a value from <b>${MULTI_RANGE[0]}</b> to <b>${MULTI_RANGE[1]}</b>. Every winning cluster is {paid|counted} first; then the record goes off, clearing itself and the four symbols beside it, and each of those five cells keeps its value. A cluster that lands on those cells is multiplied by the <strong>sum</strong> of the values it covers, and values that meet add together.`)}</p>` +
    `<p>${T(extreme
      ? `In the Xtreme Bonus every value stays on the board for the whole feature, and every Gold Record is <b>x2</b> or more.`
      : `In the bonus every value stays on the board for the whole feature: nothing is wiped between spins, so the board only gets richer.`)}</p>` +
    `<p>${T(`Hit Parades - lines of <b>3</b> or <b>4</b> Gold Records - land far more often in here, every winning cluster leaves Tips (small multipliers) under itself, and an <b>Encore</b> comes far more often than in the base game.`)}</p>`;
}''')
d.rep('const MULTI_RANGE = ["x1.25", "x1000"];   // the Multi\'s values, as rules.js states them',
      'const MULTI_RANGE = ["x1.25", "x1000"];   // the Gold Record\'s values, as rules.js states them')
# the volatility pips: gold stars (were Power Outage's lightning bolts)
d.rep('''    --drip: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 24'><path d='M12.5 1 3 14h6.2L7 23l10-13.2h-6.3L12.5 1z'/></svg>");''',
      '''    --drip: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M12 1.5l3.1 6.6 7.2.9-5.3 5 1.4 7.2L12 17.7l-6.4 3.5L7 14l-5.3-5 7.2-.9z'/></svg>");''')
# an unfinished round: Continue or Skip, asked first (Engine, Falcos 2026-11-22: a resumed round may never jump to
# its result on its own, and Skip settles it without naming the amount)
d.rep('''    await introDone;   // never replay a round behind the opening screen
    state.playing = true;
    setButtons(false);
    notice(T("Resuming your round..."), false, 2600);
    try { await presentRound(open, { from: resumePoint(open) }); } catch (e) { /* surfaced by presentRound */ }
    state.playing = false;
    setButtons(true);''', '''    await introDone;   // never replay a round behind the opening screen
    state.playing = true;
    setButtons(false);
    const go = await resumeAsk();
    if (go === "skip") {
      try { await RGS.endRound(); setBalance(RGS.state.balance); } catch (err) { notice(`<b>${rgsMessage(err)}</b>`, true, 6000); }
    } else {
      try { await presentRound(open, { from: resumePoint(open) }); } catch (e) { /* surfaced by presentRound */ }
    }
    state.playing = false;
    setButtons(true);''')
d.rep('''function bonusIntroHow(extreme) {''', '''// The card an unfinished round asks first: Continue plays it from where it stood, Skip settles it as it is
function resumeAsk() {
  return new Promise(resolve => {
    const w = document.createElement("div");
    w.className = "resumeask";
    w.setAttribute("role", "dialog"); w.setAttribute("aria-modal", "true"); w.setAttribute("aria-label", T("Unfinished round"));
    w.innerHTML = `<div class="rabox"><h3>${T("Unfinished round")}</h3><p>${T("You have a round in progress. Continue to play it out, or skip to finish it now.")}</p>` +
      `<div class="rabtns"><button type="button" class="racont">${T("Continue")}</button><button type="button" class="raskip">${T("Skip")}</button></div></div>`;
    document.body.appendChild(w);
    const done = v => { w.remove(); removeEventListener("keydown", key, true); resolve(v); };
    const key = e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); e.stopPropagation(); done("continue"); } };
    w.querySelector(".racont").addEventListener("click", e => { e.stopPropagation(); done("continue"); });
    w.querySelector(".raskip").addEventListener("click", e => { e.stopPropagation(); done("skip"); });
    addEventListener("keydown", key, true);
    setTimeout(() => { const b = w.querySelector(".racont"); if (b) b.focus(); }, 30);
  });
}
function bonusIntroHow(extreme) {''')
d.rep("""  #phonesign { display: none; }""", """  /* the info screen's Game Modes table: names and amounts never broken mid-word (review) */
  html .infopanel table.modes td:nth-child(-n+2), html .infopanel table.modes th:nth-child(-n+2) { overflow-wrap: normal; white-space: nowrap; }
  /* an unfinished round's Continue / Skip card */
  .resumeask { position: fixed; inset: 0; z-index: 9000; display: grid; place-items: center; background: rgba(8, 8, 20, .62); }
  .resumeask .rabox { width: min(420px, 88vw); padding: 22px 24px 20px; border-radius: 18px; background: #151a3e; color: #f7f4ff;
    border: 3px solid #111; box-shadow: 0 0 0 3px #FFC23A inset, 0 12px 30px rgba(0, 0, 0, .5); text-align: center; font-family: "Fredoka", system-ui, sans-serif; }
  .resumeask h3 { margin: 0 0 8px; font-size: 22px; color: #FFC23A; letter-spacing: .03em; }
  .resumeask p { margin: 0 0 16px; font-size: 15px; line-height: 1.4; }
  .resumeask .rabtns { display: flex; gap: 12px; justify-content: center; }
  .resumeask button { min-width: 120px; padding: 10px 16px; border-radius: 12px; border: 3px solid #111; font: 700 16px "Fredoka", system-ui, sans-serif; cursor: pointer; }
  .resumeask .racont { background: #FFC23A; color: #241505; }
  .resumeask .raskip { background: #2a3168; color: #f7f4ff; }
  #phonesign { display: none; }""")

d.save()

# ================================================================================================ rules.js
r = Doc("rules.js")
r.rep('''    M: "Multi", BS: "FS scatter", ES: "XFS scatter",
    H1: "The President", H2: "The Bodyguard", H3: "Bankrupt CEO", H4: "Market Crash", H5: "Red Hotline",
    H6: "AI Server", H7: "Broke Piggy Bank",
    L1: "Candle", L3: "Dead Battery", L4: "Blown Bulb",''', '''    M: "Gold Record", BS: "FS scatter", ES: "XFS scatter",
    H1: "The Crooner", H2: "The Bachelorette", H3: "The Fiddler", H4: "Mechanical Bull", H5: "Hot Chicken",
    H6: "Rhinestone Boot", H7: "Banjo",
    L1: "Horseshoe", L3: "Guitar Pick", L4: "Harmonica",''')
r.rep('''<div class="pname">${t("Surge Line and Grid Overload")}''', '''<div class="pname">${t("Hit Parade and Sold-Out Show")}''')
r.rep('''<div class="pname">${t("Line Drops")}</div>''', '''<div class="pname">${t("Tips")}</div>''')
r.rep('''<div class="ptile multi"><span>x1.25</span><small>DROP</small></div>''', '''<div class="ptile multi"><span>x1.25</span><small>TIP</small></div>''')
r.rep('''<div class="pname">${t("Multi — Multiplier")}<small>M</small></div>''', '''<div class="pname">${t("Gold Record — Multiplier")}<small>M</small></div>''')
# the words through the rules text
for a, b in (("Surge Lines", "Hit Parades"), ("Surge Line", "Hit Parade"), ("Grid Overload", "Sold-Out Show"),
             ("A line drop", "A tip"), ("a line drop's", "a tip's"), ("line drop", "tip"),
             ("Multis", "Gold Records"), ("a Multi's", "a Gold Record's"), ("the Multi's", "the Gold Record's"),
             ("Every Multi", "Every Gold Record"), ("every Multi", "every Gold Record"), ("the Multi and", "the Gold Record and"),
             ("becomes a Multi", "becomes a Gold Record"), ("two Multis", "two Gold Records"), ("When two Gold Records", "When two Gold Records")):
    r.s = r.s.replace(a, b)
# Encore, after the special symbols
r.rep('''<section>
  <h4>${t("Free spins")}</h4>''', '''<section>
  <h4>${t("Encore")}</h4>
  <p>${t("When a spin's tumbles are over and the board {pays|wins} nothing more, the crowd can call an Encore. The spotlight picks a top symbol (The Crooner, The Bachelorette, The Fiddler, Mechanical Bull, Hot Chicken, Rhinestone Boot or Banjo) and every copy of one regular symbol (Horseshoe, Guitar Pick or Harmonica) on the board turns into it. Scatters and Gold Records never change. The new board is then {paid|counted} like any other: its clusters pay through the values on their cells, Gold Records go off and the tumbles carry on.")}</p>
  <p>${t("An Encore can come on any spin, winning or losing, at most once per spin (once per free spin in a bonus), and more often in the bonus than in the base game. It is part of the outcome of the spin: it never changes what the spin costs.")}</p>
</section>

<section>
  <h4>${t("Free spins")}</h4>''')
# ---- rules.js: review fixes (2026-11-22)
r.rep("""    if (sym === "M") return `<div class="ptile multi"><span>x5</span><small>MULTI</small></div>`;""",
      """    if (sym === "M") return `<img class="ptile" src="${art("assets/flat/M3.webp")}" alt="${esc(T("Gold Record", social))}" draggable="false">`;""")
r.rep("Gold Records land more often than in the base game and Hit Parades far more often",
      "Hit Parades land far more often than in the base game")
r.rep("Gold Records land more often still, every Gold Record is worth x2 or more", "every Gold Record is worth x2 or more")
r.rep("and every copy of one regular symbol (Horseshoe, Guitar Pick or Harmonica) on the board turns into it.",
      "and every copy of one regular symbol (Horseshoe, Guitar Pick or Harmonica) that has at least 3 copies on the board turns into it.")
r.rep('''<div class="pname">${t("Hit Parade and Sold-Out Show")}''', '''<div class="pname">${t("Record colours")}</div>
    <div class="ptext">${t("A Gold Record's disc shows how much it is worth: bronze up to x2, silver up to x5, gold up to x20, platinum up to x100, and diamond (pink) above x100.")}</div></div>
  <div class="prow">${tile("M")}<div class="pname">${t("Hit Parade and Sold-Out Show")}''')

r.rep('''"Power Outage"''', '''"Broadway on Nashville"''') if r.s.count('"Power Outage"') == 1 else None
r.s = r.s.replace("Power Outage", "Broadway on Nashville")
r.save()
