
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
d.rep("T(`Rosie's solo turns every copy of one regular symbol into a top symbol.`)",
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
    `<p>${T(`Hit Parades - lines of <b>3</b> or <b>4</b> Gold Records - land far more often in here, every winning cluster leaves Tips (small multipliers) under itself, and Rosie plays an <b>Encore</b> far more often than in the base game.`)}</p>`;
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
d.rep("""  #rosiephone { display: none; }""", """  /* the info screen's Game Modes table: names and amounts never broken mid-word (review) */
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
  #rosiephone { display: none; }""")
