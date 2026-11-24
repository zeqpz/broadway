// Broadway on Nashville: the inside of a honky-tonk bar behind the board, kept alive (no people in it).
//
// The painting (assets/bonus_wall.webp) is the empty bar with every neon sign and bulb LIT. tools/broadway/bg_layers_bw.py
// compared it with the same room drawn with all of them switched off and cut that difference into patches
// (assets/bg/scene.json): one "off" patch per neon sign, three chase groups each of the party bulbs and the stage's
// footlights, and the jukebox's lit tubes.
// It also says where the pieces drawn here go (scene.json "props"). Everything below is small and slow on purpose:
//   neon        every sign hums along lit; now and then one stutters (a few quick drop-outs), and one tired sign
//               (the red boot) does it often and sometimes dies for a second before it catches
//   bulbs       the string of party bulbs under the ceiling chases in three groups; the stage's footlights run the
//               other way, a little slower
//   fans        two ceiling fans turn lazily (a top view of the blades, turned, then flattened as the eye sees it)
//   stage       the pink and the blue stage light each throw a soft beam that sways and swells, crossing over the
//               stage; dust drifts up through them
//   bottles     a glint twinkles on one bottle or another along the back-bar
//   coffee      steam curls off the pot on the counter
//   jukebox     its glowing tubes run slowly through the colours
//   records     a shine sweeps across the three gold records every so often
//   Xtreme      the rooftop stage (its own painting): flat cartoon fireworks burst over the skyline
//   WallFX.surge(k, ms)  (a bonus trigger, a big win) every sign blinks together and the bulbs flash
// Only opacity, transform and (on the jukebox's small patch) a hue filter change; timers stop while the tab is hidden.
// Reduced motion: everything lit and still. Phones never run it (html.mob #bgscene is hidden: the plate alone).
(function () {
  "use strict";
  // the page asks for WallFX.start() and .surge() whether or not the scene ever builds: there from the first line
  window.WallFX = Object.assign(window.WallFX || {}, { start() {}, surge() {} });
  const wall = document.getElementById("bgwall");
  if (!wall || window.MOBILE) return;
  const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const scene = document.createElement("div");
  scene.id = "bgscene";
  scene.setAttribute("aria-hidden", "true");
  wall.appendChild(scene);

  let seed = 1997;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;
  const rr = (a, b) => a + (b - a) * rnd();
  const pct = v => (v * 100).toFixed(3) + "%";
  const later = (ms, fn) => setTimeout(() => { if (document.hidden) later(1500, fn); else fn(); }, ms);
  const xtreme = () => document.body.classList.contains("xtreme");
  const place = (e, [x, y, w, h]) => Object.assign(e.style, { left: pct(x), top: pct(y), width: pct(w), height: pct(h) });
  const AR = 16 / 9;   // the scene's box: a share of its width is this many times that share of its height

  const BURST = (c1, c2) => `<svg viewBox="-50 -50 100 100">${Array.from({ length: 14 }, (_, i) => {
    const a = i / 14 * Math.PI * 2, x = Math.cos(a), y = Math.sin(a);
    return `<path d="M${(x * 12).toFixed(1)} ${(y * 12).toFixed(1)} L${(x * 44).toFixed(1)} ${(y * 44).toFixed(1)}" stroke="#111" stroke-width="7" stroke-linecap="round"/>` +
           `<path d="M${(x * 12).toFixed(1)} ${(y * 12).toFixed(1)} L${(x * 44).toFixed(1)} ${(y * 44).toFixed(1)}" stroke="${i % 2 ? c1 : c2}" stroke-width="4" stroke-linecap="round"/>` +
           `<circle cx="${(x * 46).toFixed(1)}" cy="${(y * 46).toFixed(1)}" r="3.4" fill="${i % 2 ? c2 : c1}" stroke="#111" stroke-width="1.6"/>`;
  }).join("")}<circle r="9" fill="#FFF6D8" stroke="#111" stroke-width="2.5"/></svg>`;
  const COLOURS = [["#FF3FA4", "#FFC23A"], ["#2FA8FF", "#F7F4FF"], ["#FFC23A", "#FF3B3B"], ["#7DFF6A", "#FF3FA4"]];
  // a ceiling fan seen from straight below: four wooden paddles on brass arms (the page turns it, then flattens it)
  const BLADE = `<g><rect x="10" y="-4.5" width="22" height="9" fill="#C9A040" stroke="#111" stroke-width="3"/>` +
    `<rect x="26" y="-14" width="70" height="28" rx="13" fill="#9A6A3E" stroke="#111" stroke-width="4"/>` +
    `<path d="M36 5 H86" stroke="#6E4526" stroke-width="5" stroke-linecap="round"/></g>`;
  const FAN = `<svg viewBox="-100 -100 200 200">${[0, 90, 180, 270].map(a => `<g transform="rotate(${a})">${BLADE}</g>`).join("")}</svg>`;
  const STAR4 = `<svg viewBox="-10 -10 20 20"><path d="M0 -10 L2.2 -2.2 L10 0 L2.2 2.2 L0 10 L-2.2 2.2 L-10 0 L-2.2 -2.2Z" fill="#FFFBE8"/></svg>`;
  const WISP = `<svg viewBox="0 0 20 60" preserveAspectRatio="none"><path d="M10 58 C2 48 18 42 10 32 C2 22 18 16 10 4" fill="none" stroke="#F4F1E8" stroke-width="4" stroke-linecap="round"/></svg>`;

  fetch("assets/bg/scene.json").then(r => r.json()).then(build).catch(() => { /* the painting alone still reads */ });

  function build(S) {
    // ---- the room's lights
    const street = document.createElement("div");
    street.className = "bgstreet";
    scene.appendChild(street);
    const add = (tag, cls, parent = street) => { const e = document.createElement(tag); e.className = cls; parent.appendChild(e); return e; };
    const img = (src, box, cls) => {
      const e = add("img", cls);
      e.alt = ""; e.draggable = false; e.decoding = "async";
      e.src = "assets/" + src;
      place(e, box);
      return e;
    };
    const signs = (S.signs || []).map(s => ({ el: img(s.src, s.box, "bgoff"), area: s.area, cx: s.cx }));
    const bulbs = (S.bulbs || []).map(b => img(b.src, b.box, "bgoff bulb"));
    const foot = (S.foot || []).map(b => img(b.src, b.box, "bgoff bulb"));
    const off = (e, v) => { e.style.opacity = v ? "1" : "0"; };
    if (S.sky) for (let i = 0; i < 18; i++) {   // (a scene under the open sky: a few stars twinkle)
      const st = add("i", "bgstar");
      st.style.left = pct(S.sky[0] + rr(.02, .98) * S.sky[2]);
      st.style.top = pct(S.sky[1] + rr(.04, .8) * S.sky[3]);
      st.style.setProperty("--d", rr(2.2, 5.5).toFixed(2) + "s");
      st.style.setProperty("--o", (-rr(0, 6)).toFixed(2) + "s");
      st.style.setProperty("--s", rr(.6, 1.3).toFixed(2));
    }
    const P = S.props || {};
    // ---- the ceiling fans: rod, turning blades, brass housing and a little lamp
    for (const [i, [x, y, r]] of (P.fans || []).entries()) {
      const f = add("i", "bgfan");
      Object.assign(f.style, { left: pct(x - r), top: pct(y - r * AR), width: pct(2 * r), height: pct(2 * r * AR) });
      f.innerHTML = `<b class="bgf-rod"></b><b class="bgf-disc"><b class="bgf-spin">${FAN}</b></b><b class="bgf-hub"></b><b class="bgf-lamp"></b>`;
      f.style.setProperty("--d", (3.4 + i * .5).toFixed(2) + "s");
      f.style.setProperty("--o", (-rr(0, 3)).toFixed(2) + "s");
    }
    // ---- the jukebox's tubes run through the colours
    if (S.juke) img(S.juke.src, S.juke.box, "bgjuke");
    // ---- a shine over each gold record, one after another
    for (const [i, [x, y, r]] of (P.records || []).entries()) {
      const d = add("i", "bgrec");
      Object.assign(d.style, { left: pct(x - r), top: pct(y - r * AR), width: pct(2 * r), height: pct(2 * r * AR) });
      d.innerHTML = "<b></b>";
      d.style.setProperty("--o", (i * .28).toFixed(2) + "s");
    }
    if (REDUCED) { scene.classList.add("still"); return; }

    // ---- the stage lights' beams: each a soft cone of its lens's colour from the lamp, swaying and swelling on its own clock
    for (const [i, [x, y, deg, col]] of (P.beams || []).entries()) {
      const len = P.beam_len || .6, w = len * .42 / AR;      // the cone's length (of the height) and its width at the far end
      const bm = add("i", "bgbeam");
      Object.assign(bm.style, { left: pct(x - w / 2), top: pct(y), width: pct(w), height: pct(len) });
      bm.style.setProperty("--c", col);
      bm.style.setProperty("--r", deg + "deg");
      bm.style.setProperty("--d", (7 + i * 1.7).toFixed(1) + "s");
      bm.style.setProperty("--o", (-i * 2.6).toFixed(1) + "s");
    }
    // ---- dust drifting up through the light over the stage
    if (P.cone) {
      const [cx, cy, cw, ch] = P.cone;
      for (let i = 0; i < 16; i++) {
        const m = add("i", "bgmote");
        const v = rr(.05, .95);
        m.style.left = pct(cx + rr(.05, .95) * cw);
        m.style.top = pct(cy + v * ch);
        m.style.setProperty("--dx", rr(-1.2, 1.2).toFixed(2) + "cqw");
        m.style.setProperty("--dy", (-rr(2.5, 6)).toFixed(2) + "cqh");
        m.style.setProperty("--a", rr(.25, .6).toFixed(2));
        m.style.setProperty("--d", rr(7, 14).toFixed(1) + "s");
        m.style.setProperty("--o", (-rr(0, 14)).toFixed(1) + "s");
        m.style.setProperty("--s", rr(.6, 1.5).toFixed(2));
      }
    }
    // ---- glints along the bottles
    if (P.glints) {
      const [gx, gy, gw, gh] = P.glints, rows = P.glint_rows || [.15, .68];
      for (let i = 0; i < 7; i++) {
        const g = add("i", "bgglint");
        g.innerHTML = STAR4;
        g.style.left = pct(gx + rr(.04, .96) * gw);
        g.style.top = pct(gy + rows[i % rows.length] * gh + rr(-.03, .03) * gh);
        g.style.setProperty("--d", rr(3.6, 7.5).toFixed(2) + "s");
        g.style.setProperty("--o", (-rr(0, 7)).toFixed(2) + "s");
      }
    }
    // ---- steam off the coffee pot
    if (P.steam) for (let i = 0; i < 3; i++) {
      const w = add("i", "bgsteam");
      w.innerHTML = WISP;
      w.style.left = pct(P.steam[0] + (i - 1) * .0045);
      w.style.top = pct(P.steam[1]);
      w.style.setProperty("--d", (2.8 + i * .5).toFixed(2) + "s");
      w.style.setProperty("--o", (-i * 1.1).toFixed(2) + "s");
      w.style.setProperty("--k", i % 2 ? "-1" : "1");
    }

    // a sign's stutter: a few quick drop-outs, then lit again (a "dead" spell holds it off for a moment)
    const stutter = (e, n, dead) => {
      let t = 0;
      for (let i = 0; i < n; i++) {
        setTimeout(() => off(e, 1), t); t += 40 + rnd() * 90;
        setTimeout(() => off(e, 0), t); t += 60 + rnd() * 220;
      }
      if (dead) { setTimeout(() => off(e, 1), t); t += 450 + rnd() * 800; setTimeout(() => off(e, 0), t); t += 90; setTimeout(() => off(e, 1), t); t += 70; setTimeout(() => off(e, 0), t); }
      return t;
    };
    // the sign on its last legs: the one furthest right (the red boot, in view beside the title sign)
    const tired = signs.length > 1 ? signs.reduce((m, s) => ((s.cx || 0) > (m.cx || 0) ? s : m), signs[0]) : null;
    const flickerLoop = () => later(1800 + rnd() * 4200, () => {
      if (!xtreme() && signs.length) {
        const s = rnd() < .3 && tired ? tired : signs[Math.floor(rnd() * signs.length)];
        stutter(s.el, 2 + Math.floor(rnd() * 4), s === tired && rnd() < .25);
      }
      flickerLoop();
    });
    flickerLoop();
    // the bulbs chase: one group off at a time, round and round
    let step = 0;
    const chase = () => later(320, () => {
      if (!xtreme()) {
        bulbs.forEach((b, g) => off(b, g === step % bulbs.length));
        if (foot.length > 1 && step % 2 === 0) foot.forEach((b, g) => off(b, g === (foot.length - 1 - (step / 2) % foot.length)));
      }
      step++;
      chase();
    });
    if (bulbs.length > 1 || foot.length > 1) chase();

    // ---- the Xtreme rooftop: fireworks (made once, shown only in the Xtreme Bonus)
    const roof = document.createElement("div");
    roof.className = "bgroof";
    scene.appendChild(roof);
    const fireworks = () => later(700 + rnd() * 1500, () => {
      if (xtreme() && !document.hidden) {
        const f = document.createElement("i");
        f.className = "bgfw";
        const [c1, c2] = COLOURS[Math.floor(rnd() * COLOURS.length)];
        f.innerHTML = BURST(c1, c2);
        const s = rr(.08, .15);
        Object.assign(f.style, { left: pct(rr(.15, .85) - s / 2), top: pct(rr(.02, .22)), width: pct(s), height: pct(s * 16 / 9) });
        roof.appendChild(f);
        setTimeout(() => f.remove(), 1700);
      }
      fireworks();
    });
    fireworks();
    const sync = () => scene.classList.toggle("xtreme", xtreme());
    new MutationObserver(sync).observe(document.body, { attributes: true, attributeFilter: ["class"] });
    sync();

    // ---- every light at once, for a bonus or a big win
    window.WallFX = Object.assign(window.WallFX || {}, {
      surge(k = 1, ms = 1600) {
        if (xtreme()) return;
        const n = Math.round(3 + 2 * k);
        let t = 0;
        for (let i = 0; i < n; i++) {
          setTimeout(() => { for (const s of signs) off(s.el, 1); for (const b of [...bulbs, ...foot]) off(b, 1); }, t); t += 70;
          setTimeout(() => { for (const s of signs) off(s.el, 0); for (const b of [...bulbs, ...foot]) off(b, 0); }, t); t += Math.max(60, ms / n - 70);
        }
      },
    });
  }
})();
