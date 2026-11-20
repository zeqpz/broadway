"""Owner pass 5 (2026-11-19) - the page's side of it, applied by reskin_outage.py after everything else:
  - the win line is a live electric arc (drawWinLine rewritten: a bolt that strikes through the cluster and crackles)
  - the title sign: G and E glitch and now and then come on; the lit letters throw light on the steel (sign_layers.py)
  - the Multi values: a bright keyline round the whole figure, and slightly see-through
  - the alarm: a klaxon whoop as an XFS lands, the full alarm as the Xtreme Bonus triggers (tools/sfx/outage_spec.py)
The Xtreme room's beacon (wall bracket: beacon_mount.py; its light: frontend/bgscene.js) and the brighter FS / XFS
(tools/outage/blender/symanim.py) are the other half of the pass."""

CSS = '''  /* ---- owner pass 5 (2026-11-19) ---- */
  /* the title sign is a stack now: the steel plate, the light its nine lit letters throw on it (a slow uneven hum),
     and G and E switched on with their own light - dead by default, stuttered and sometimes lit by the page (--ge).
     The plate itself never fades or moves (owner, pass 2: no twitching sign) */
  #logosign { filter: none; aspect-ratio: 4 / 3; --ge: 0; }
  #logosign img { position: absolute; inset: 0; width: 100%; height: 100%; display: block; pointer-events: none; user-select: none; }
  #logosign .base { filter: drop-shadow(0 10px 14px rgba(6, 8, 20, .5)); }
  #logosign .glow, #logosign .geglow { mix-blend-mode: screen; }
  #logosign .glow { animation: signHum 4.6s linear infinite; }
  #logosign .ge, #logosign .geglow { opacity: var(--ge); }
  @keyframes signHum { 0%, 100% { opacity: .88; } 6% { opacity: 1; } 7% { opacity: .78; } 8.5% { opacity: 1; } 31% { opacity: .92; }
    33% { opacity: 1; } 52% { opacity: .9; } 61% { opacity: 1; } 62% { opacity: .72; } 63% { opacity: .96; } 64.5% { opacity: .82; }
    66% { opacity: 1; } 84% { opacity: .91; } }
  @media (prefers-reduced-motion: reduce) { #logosign .glow { animation: none; } }
  /* the Multi values: a bright keyline round the whole figure (four hard shadows of the value's own colour, nearly
     white, so the black-outlined numerals read on the dark board and through the symbols in front of them), the same
     slight glow off the lettering, and slightly see-through - more so behind a symbol than in an open cell */
  .multlayer .gmult, .cell.booster .multface .mv, .fbox .fmult {
    --ol: max(1.3px, .036em); --rim: color-mix(in srgb, var(--heat, #3FE0FF) 28%, #fff); }
  .multlayer .gmult { opacity: .62;
    filter: drop-shadow(var(--ol) 0 0 var(--rim)) drop-shadow(calc(-1 * var(--ol)) 0 0 var(--rim))
      drop-shadow(0 var(--ol) 0 var(--rim)) drop-shadow(0 calc(-1 * var(--ol)) 0 var(--rim))
      drop-shadow(0 0 4px color-mix(in srgb, var(--heat, #3FE0FF) 60%, transparent)); }
  .multlayer .gmult.bare:not(.gone) { opacity: .86; }
  .cell.booster .multface .mv { opacity: .92;
    filter: drop-shadow(var(--ol) 0 0 var(--rim)) drop-shadow(calc(-1 * var(--ol)) 0 0 var(--rim))
      drop-shadow(0 var(--ol) 0 var(--rim)) drop-shadow(0 calc(-1 * var(--ol)) 0 var(--rim))
      drop-shadow(0 0 4px color-mix(in srgb, var(--heat, #3FE0FF) 60%, transparent)) !important; }
  .fbox .fmult { filter: drop-shadow(var(--ol) 0 0 var(--rim)) drop-shadow(calc(-1 * var(--ol)) 0 0 var(--rim))
      drop-shadow(0 var(--ol) 0 var(--rim)) drop-shadow(0 calc(-1 * var(--ol)) 0 var(--rim)); }
  html.mob .multlayer .gmult {   /* phones: the keyline without the blurred glow */
    filter: drop-shadow(var(--ol) 0 0 var(--rim)) drop-shadow(calc(-1 * var(--ol)) 0 0 var(--rim))
      drop-shadow(0 var(--ol) 0 var(--rim)) drop-shadow(0 calc(-1 * var(--ol)) 0 var(--rim)); }
  /* the win line's sparks: thrown from each symbol the arc earths through (drawWinLine sets --dx / --dy) */
  .lineLayer b { width: 5px !important; height: 5px !important; margin: -2.5px 0 0 -2.5px !important; border-radius: 50%;
    background: radial-gradient(circle, #fff 0, rgba(150, 238, 255, .95) 42%, rgba(63, 224, 255, 0) 74%) !important;
    filter: none !important; mix-blend-mode: screen; transform: none;
    animation: lineSpark calc(.5s * var(--tempo, 1)) cubic-bezier(.15, .6, .35, 1) forwards !important; }
  @keyframes lineSpark { 0% { translate: 0 0; scale: 1.7; opacity: 1; } 70% { opacity: 1; }
    100% { translate: var(--dx, 0px) var(--dy, 16px); scale: .35; opacity: 0; } }
'''

WINLINE = '''function drawWinLine(positions) {
  // Power Outage (owner pass 5, 2026-11-19): the win line is a live arc, not a stroke - a bolt that strikes from the
  // cluster's first symbol through every other one (nearest next, so it threads the shape), jagged, white-hot with
  // a cyan corona, and then keeps crackling: a fresh jagged run every 55 ms, small forks spitting off it, a flash
  // on every symbol it earths through and a few sparks thrown as it arrives. One canvas on the cluster's sheet,
  // redrawn; it stops re-striking after a few seconds and fades with its cluster's moment (clearWinLine).
  // Returns how long the strike takes at tempo 1 (the same beat the stroke had).
  const board = $("board");
  if (!board || !positions || positions.length < 2) return 0;
  const pts = positions.map(p => {
    const c = cellCentre(p.reel, Math.min(Math.max(p.row - 1, 0), ROWS - 1));
    return { x: c.x - BURST_PAD, y: c.y - BURST_PAD, reel: p.reel, row: p.row };
  });
  const left = pts.sort((a, b) => a.reel - b.reel || a.row - b.row);
  const path = [left.shift()];
  while (left.length) {
    const last = path[path.length - 1];
    let bi = 0, bd = Infinity;
    left.forEach((q, i) => { const d = Math.abs(q.x - last.x) + Math.abs(q.y - last.y); if (d < bd) { bd = d; bi = i; } });
    path.push(left.splice(bi, 1)[0]);
  }
  let total = 0;
  for (let i = 1; i < path.length; i++) total += Math.hypot(path[i].x - path[i - 1].x, path[i].y - path[i - 1].y);
  // the sheet: the path's box with room for the bolt's kinks, its forks and its corona
  const xs = path.map(p => p.x), ys = path.map(p => p.y), PAD = window.MOBILE ? 40 : 60;   // (a phone's sheet is a GPU surface: no bigger than the bolt needs)
  const bx = Math.min(...xs) - PAD, by = Math.min(...ys) - PAD;
  const bw = Math.max(...xs) + PAD - bx, bh = Math.max(...ys) + PAD - by;
  const sh = lineSheet();
  const fit = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--fit")) || 1;
  const k = Math.max(1, Math.min(2, (devicePixelRatio || 1) * fit));
  Object.assign(sh.el.style, { left: bx + "px", top: by + "px", width: bw + "px", height: bh + "px" });
  const cv = sh.paint;
  cv.width = Math.round(bw * k); cv.height = Math.round(bh * k);
  const gp = gfxCtx(cv);
  if (!gp) return 0;   // (the safety net) no canvas for the line: the cluster still pays and pops
  gp.setTransform(k, 0, 0, k, -bx * k, -by * k);
  gp.lineJoin = "miter"; gp.miterLimit = 4; gp.lineCap = "round";   // sharp kinks, like a bolt
  sh.el.classList.add("on");
  const rnd = Math.random;
  // a jagged run through every cell of the path: each leg split three times, its midpoints knocked sideways (the
  // cells themselves stay put, so the bolt always runs symbol to symbol); s = the distance along it
  const bolt = () => {
    const out = [{ x: path[0].x, y: path[0].y, node: true, s: 0 }];
    for (let i = 0; i < path.length - 1; i++) {
      let seg = [path[i], path[i + 1]];
      let amp = Math.min(26, Math.hypot(seg[1].x - seg[0].x, seg[1].y - seg[0].y) * .2);
      for (let lvl = 0; lvl < 3; lvl++) {
        const next = [seg[0]];
        for (let j = 0; j < seg.length - 1; j++) {
          const p = seg[j], q = seg[j + 1], dx = q.x - p.x, dy = q.y - p.y, len = Math.hypot(dx, dy) || 1, off = (rnd() - .5) * 2 * amp;
          next.push({ x: (p.x + q.x) / 2 - dy / len * off, y: (p.y + q.y) / 2 + dx / len * off }, q);
        }
        seg = next; amp *= .55;
      }
      for (let j = 1; j < seg.length; j++) out.push({ x: seg[j].x, y: seg[j].y, node: j === seg.length - 1, s: 0 });
    }
    for (let i = 1; i < out.length; i++) out[i].s = out[i - 1].s + Math.hypot(out[i].x - out[i - 1].x, out[i].y - out[i - 1].y);
    return out;
  };
  // small forks spitting off the run, no further along than the strike has reached
  const forks = (B, upto) => {
    const f = [], n = Math.min(7, 2 + Math.floor(path.length / 2));
    for (let i = 0; i < n; i++) {
      const j = 1 + Math.floor(rnd() * (B.length - 1)), p = B[j], q = B[j - 1];
      if (p.s > upto) continue;
      let a = Math.atan2(p.y - q.y, p.x - q.x) + (rnd() < .5 ? -1 : 1) * (.5 + rnd() * .8), x = p.x, y = p.y;
      const leg = [{ x, y }], steps = 2 + Math.floor(rnd() * 2), len = (22 + rnd() * 34) / steps;
      for (let s = 0; s < steps; s++) { a += (rnd() - .5) * .9; x += Math.cos(a) * len; y += Math.sin(a) * len; leg.push({ x, y }); }
      f.push(leg);
    }
    return f;
  };
  const stroke = (line, upto, w, style) => {   // the run as far as `upto` px along it; returns where it ends
    gp.lineWidth = w; gp.strokeStyle = style;
    gp.beginPath(); gp.moveTo(line[0].x, line[0].y);
    let end = line[0];
    for (let i = 1; i < line.length; i++) {
      const p = line[i - 1], q = line[i];
      if (upto == null || q.s <= upto) { gp.lineTo(q.x, q.y); end = q; continue; }
      const f = (upto - p.s) / Math.max(1e-6, q.s - p.s);
      end = { x: p.x + (q.x - p.x) * f, y: p.y + (q.y - p.y) * f };
      gp.lineTo(end.x, end.y);
      break;
    }
    gp.stroke();
    return end;
  };
  const flare = (x, y, r, a) => {
    const g = gp.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, `rgba(250, 254, 255, ${a.toFixed(3)})`); g.addColorStop(.35, `rgba(120, 232, 255, ${(a * .6).toFixed(3)})`);
    g.addColorStop(1, "rgba(63, 224, 255, 0)");
    gp.fillStyle = g; gp.fillRect(x - r, y - r, r * 2, r * 2);
  };
  const paint = (B, F, upto, hot, T) => {
    const i = hot > 1 ? 1 : .68 + rnd() * .32;   // the arc's own flicker
    gp.globalCompositeOperation = "source-over";
    gp.clearRect(bx, by, bw, bh);
    stroke(B, upto, 15 * hot, "rgba(6, 16, 48, .3)");   // a dark edge, so it reads over the bright symbols
    gp.globalCompositeOperation = "lighter";
    stroke(B, upto, 28 * hot, `rgba(63, 224, 255, ${(.1 * i).toFixed(3)})`);   // the corona, wide to tight
    stroke(B, upto, 14 * hot, `rgba(63, 224, 255, ${(.28 * i).toFixed(3)})`);
    if (T) {   // a second, thinner strand arcing beside the main one
      stroke(T, upto, 6, `rgba(63, 224, 255, ${(.2 * i).toFixed(3)})`);
      stroke(T, upto, 1.5, `rgba(225, 250, 255, ${(.7 * i).toFixed(3)})`);
    }
    for (const leg of F) {
      stroke(leg, null, 5.5, `rgba(63, 224, 255, ${(.22 * i).toFixed(3)})`);
      stroke(leg, null, 1.7, `rgba(225, 250, 255, ${(.85 * i).toFixed(3)})`);
    }
    stroke(B, upto, 7 * hot, `rgba(150, 238, 255, ${(.75 * i).toFixed(3)})`);
    gp.globalCompositeOperation = "source-over";
    const head = stroke(B, upto, 3.2 * hot, "rgba(248, 253, 255, 1)");   // the white-hot core
    gp.globalCompositeOperation = "lighter";
    for (const p of B) if (p.node && p.s <= upto) flare(p.x, p.y, (20 + rnd() * 10) * hot, .78 * i);   // each symbol it earths through
    return head;
  };
  const D = Math.min(LINE_DRAW_MAX, 260 + total * .55);   // ms at tempo 1
  let B = bolt(), F = [], T = null;
  if (REDUCED_MOTION || document.hidden) { paint(B, F, Infinity, 1); return 0; }
  // (phones: the bolt re-jags half as often and for a shorter while, and throws no sparks - fewer canvas uploads)
  const PH = !!window.MOBILE;
  const dur = D * tempo(), t0 = performance.now(), STRIKE = Math.max(110, dur * .5), LIVE = PH ? 1600 : 3600, JIT = PH ? 110 : 55;
  // the current's whoosh rides the strike: the short take for a short line (a touch quicker when the strike is),
  // the long one for a long line, faded out once it has landed
  if (dur <= 620) sfx("sprayLineShort", Math.min(1.5, Math.max(.92, 550 / dur)));
  else { const hiss = sfx("sprayLineLong"); if (hiss) setTimeout(() => sfxFade(hiss, 140), dur); }
  const spark = q => {
    if (PH) return;
    const b = document.createElement("b"), a = rnd() * Math.PI * 2, r = 16 + rnd() * 30;
    b.style.left = (q.x - bx).toFixed(1) + "px"; b.style.top = (q.y - by).toFixed(1) + "px";
    b.style.setProperty("--dx", (Math.cos(a) * r).toFixed(1) + "px");
    b.style.setProperty("--dy", (Math.sin(a) * r + 12).toFixed(1) + "px");
    b.addEventListener("animationend", () => b.remove(), { once: true });
    sh.el.appendChild(b);
  };
  let jitAt = t0, seen = 0, ticks = 0, landed = 0, reAt = 0;
  const frame = now => {
    sh.raf = 0;
    if (!sh.el.classList.contains("on")) return;   // fading with its cluster: the last frame stands
    const e = now - t0, u = Math.min(1, Math.max(0, e / STRIKE));
    const re = now - jitAt >= JIT;
    if (u >= 1 && landed && !re) { sh.raf = requestAnimationFrame(frame); return; }   // landed: only redrawn as it re-jags
    if (re) { jitAt = now; B = bolt(); T = rnd() < .7 ? bolt() : null; }
    const upto = u >= 1 ? Infinity : B[B.length - 1].s * (1 - (1 - u) * (1 - u));   // off the mark fast, easing in
    if (u < 1) T = null;   // the second strand only once the strike has landed (its length is its own)
    if (re) F = forks(B, upto);
    if (u >= 1 && !landed) { landed = now; reAt = now + 300 + rnd() * 380; }
    let hot = 1;
    if (landed && now - landed < 130) hot = 1.9;                                      // it lands: a fat white frame or two
    else if (landed && now >= reAt) { hot = 1.55; reAt = now + 260 + rnd() * 520; }   // and re-strikes now and then
    const head = paint(B, F, upto, hot, T);
    if (u < 1) flare(head.x, head.y, 28, .95);                                        // the strike's head
    // every symbol the strike reaches throws a few sparks (the first couple are heard)
    let reached = 0;
    for (const p of B) if (p.node && p.s <= upto) reached++;
    for (; seen < reached; seen++) {
      for (let n = 2 + Math.floor(rnd() * 2); n--;) spark(path[seen]);
      if (ticks++ < 2) sfx("paintDrip");
    }
    if (e < LIVE) sh.raf = requestAnimationFrame(frame);
  };
  sh.raf = requestAnimationFrame(frame);
  sh.land = setTimeout(() => { if (sh.el.classList.contains("on") && !landed) paint(B, F, Infinity, 1); }, dur + 120);   // rAF stalls in a hidden tab
  return D + 200;
}

'''

# the sign's element (main() in reskin_outage.py puts it next to the frame) and the life in its last two letters
SIGN_NEW = '''    { const pf = document.getElementById("paintframe"), sign = document.createElement("div");   // Power Outage: the title board
      sign.id = "logosign"; sign.setAttribute("aria-hidden", "true");
      // (owner pass 5) the plate, the light its lit letters throw, and G and E switched on with theirs (sign_layers.py)
      // (phones never show the sign: its four pictures are not even made there, so they are never fetched)
      if (pf && pf.parentNode && !window.MOBILE) {
        sign.innerHTML = '<img class="base" src="assets/logo_sign.webp" alt="" draggable="false"><img class="glow" src="assets/logo_sign_glow.webp" alt="" draggable="false">'
          + '<img class="ge" src="assets/logo_sign_ge.webp" alt="" draggable="false"><img class="geglow" src="assets/logo_sign_ge_glow.webp" alt="" draggable="false">';
        pf.parentNode.appendChild(sign);
      }
      // G and E are dead: every few seconds they stutter, and now and then they catch and burn for a moment (with the
      // odd dip of a bad contact) before dying again; when the room's power sputters back (bgscene.js "bgpower") they
      // come on with it. --ge is how lit they are, 0..1
      if (sign.parentNode && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
        const ge = v => sign.style.setProperty("--ge", v);
        let busy = false;
        const play = (steps, then) => {
          busy = true;
          let t = 0;
          for (const [ms, v] of steps) { setTimeout(() => ge(v), t); t += ms; }
          setTimeout(() => { ge(0); busy = false; if (then) then(); }, t);
        };
        const stutter = n => {
          const s = [];
          for (let i = 0; i < n; i++) { s.push([28 + Math.random() * 70, (.4 + Math.random() * .6).toFixed(2)]); s.push([45 + Math.random() * 170, Math.random() < .25 ? .1 : 0]); }
          return s;
        };
        const hold = ms => {
          const s = [];
          for (let rest = ms; rest > 0;) { const run = Math.min(rest, 260 + Math.random() * 700); s.push([run, 1]); rest -= run; if (rest > 0) s.push([30 + Math.random() * 40, .55]); }
          return s;
        };
        const idle = () => setTimeout(() => {
          if (document.hidden || busy) return idle();
          const steps = stutter(2 + Math.floor(Math.random() * 4));
          if (Math.random() < .4) steps.push(...hold(1100 + Math.random() * 2400), ...stutter(1 + Math.floor(Math.random() * 3)));
          play(steps, idle);
        }, 1700 + Math.random() * 4300);
        idle();
        addEventListener("bgpower", () => { if (!busy) play([[110, 1], [80, 0], [110, .8], [80, 0], [520, 1], [60, .9], [80, 0], [70, .5]]); });
      }
'''
SIGN_OLD = '''    { const pf = document.getElementById("paintframe"), sign = document.createElement("img");   // Power Outage: the title board
      sign.id = "logosign"; sign.alt = ""; sign.draggable = false; sign.src = "assets/logo_sign.webp";
      if (pf && pf.parentNode && !window.MOBILE) pf.parentNode.appendChild(sign);
'''


def apply(d):
    """The page edits (index.html), after every earlier pass."""
    # the alarm sounds
    d.rep('''  dripLand: "assets/sfx_drip_b.wav",             // an icon landing on the pile during the reveal
};''', '''  dripLand: "assets/sfx_drip_b.wav",             // an icon landing on the pile during the reveal
  // (owner pass 5) the alarm: one klaxon whoop as an XFS lands, the full alarm as the Xtreme Bonus triggers
  xfsAlarm: "assets/sfx_xfs_alarm.wav", xtremeAlarm: "assets/sfx_xtreme_alarm.wav",
};''')
    d.rep('''  dripLand: .3,
''', '''  dripLand: .3, xfsAlarm: .5, xtremeAlarm: .55,
''')
    d.rep('''        sfxGap("scatterLand", 140, 1 + r * .02);''', '''        sfxGap("scatterLand", 140, 1 + r * .02);
        if (!crew) sfxGap("xfsAlarm", 450);   // (owner pass 5) an XFS lands: the alarm whoops''')
    d.rep('''    document.body.classList.add("xtreme");   // the red emergency room for the Xtreme Bonus''',
          '''    document.body.classList.add("xtreme");   // the red emergency room for the Xtreme Bonus
    sfx("xtremeAlarm");   // (owner pass 5) and its alarm goes off''')
    # the electric win line
    d.between("function drawWinLine(positions) {", "// The light show's sound, once per cluster", WINLINE)
