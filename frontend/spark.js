// Power Outage: the frayed wire at the frame's top-right corner throws real sparks (owner pass 4, 2026-11-18).
//
// tools/outage/frame_spark.py took the painted yellow star off the wire and wrote where it sat (assets/spark.json, in
// frame-picture px). Every few seconds the bare copper arcs:
//   flash      a white-hot core at the strand ends with a wider blue-white bloom, stuttering two or three times the
//              way a shorting wire does
//   arcs       thin jagged filaments of electricity jumping from the tip - to the other frayed ends and into the air -
//              redrawn each stutter, white with a cyan halo
//   sparks     hot metal thrown out in a cone, each a streak that follows its own path: fast and white-yellow at
//              first, slowing in the air, falling under gravity, cooling through orange to dull red as it dies; the
//              ones that land on the frame's top bar bounce once and skitter
//   smoke      after a big one, a small grey wisp rises and thins out
// Between the big arcs there are small crackles (a few sparks, one faint filament). The breaker being thrown, the
// power sputtering back (bgscene's "bgpower") and thunder each set it off too.
// One additive canvas in #sparkbox (the frame's own box, above the frame); it only runs while something is alive.
// Reduced motion: no sparks. Seeded per burst from Math.random: ambient decoration, never part of a round's result.
// Phones (window.MOBILE; iOS crash at load, Engine live test 2026-11-20): no sparks either - the canvas was a
// 1121 x 1208 px GPU surface laid over the frame's corner, and on iOS everything it overlaps is pushed onto layers of
// its own. The sister games' phone tier has no particle effects for the same reason.
(function () {
  "use strict";
  if (window.MOBILE) return;
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const box = document.getElementById("sparkbox");
  if (!box) return;
  fetch("assets/spark.json").then(r => r.json()).then(start).catch(() => { /* no sparks: the wire still reads */ });

  function start(S) {
    const [FW, FH] = S.frame, O = S.origin, tips = S.others || [];
    // the canvas's patch of the frame picture: wide and tall enough for the sparks' flight (it hangs past the frame)
    const R = { x: FW * .62, y: -FH * .16, w: FW * .56, h: FH * .62 };
    const cv = document.createElement("canvas");
    cv.className = "sparkcv";
    Object.assign(cv.style, { left: (R.x / FW * 100) + "%", top: (R.y / FH * 100) + "%",
      width: (R.w / FW * 100) + "%", height: (R.h / FH * 100) + "%" });
    box.appendChild(cv);
    const ctx = cv.getContext("2d");
    const BAR_TOP = S.bar_top || FH * .12, BAR_RIGHT = S.bar_right || FW * .955;   // the top bar sparks can land on
    const rnd = (a, b) => a + Math.random() * (b - a);

    let sparks = [], arcs = [], flashes = [], smoke = [], raf = 0, last = 0, k = 1;
    const fit = () => {
      const dpr = Math.min(1.5, window.devicePixelRatio || 1);
      const w = Math.max(2, Math.round(cv.clientWidth * dpr)), h = Math.max(2, Math.round(cv.clientHeight * dpr));
      if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
      k = cv.width / R.w;
    };
    new ResizeObserver(fit).observe(cv);
    fit();

    // a jagged filament from a to b: midpoint displacement, a few levels
    const bolt = (ax, ay, bx, by, rough) => {
      let pts = [[ax, ay], [bx, by]];
      for (let lvl = 0; lvl < 4; lvl++) {
        const next = [pts[0]];
        for (let i = 1; i < pts.length; i++) {
          const [x0, y0] = pts[i - 1], [x1, y1] = pts[i], len = Math.hypot(x1 - x0, y1 - y0);
          const nx = -(y1 - y0) / (len || 1), ny = (x1 - x0) / (len || 1), off = rnd(-1, 1) * len * rough;
          next.push([(x0 + x1) / 2 + nx * off, (y0 + y1) / 2 + ny * off], pts[i]);
        }
        pts = next;
      }
      return pts;
    };
    const strike = power => {                       // one stutter of the arc: its filaments and its flash
      const n = power > .6 ? 2 + (Math.random() < .5 ? 1 : 0) : 1;
      for (let i = 0; i < n; i++) {
        const toTip = tips.length && Math.random() < .45 ? tips[Math.floor(Math.random() * tips.length)] : null;
        const a = rnd(-2.6, -.2), len = rnd(50, 170) * (.5 + power * .7);
        const bx = toTip ? toTip[0] + rnd(-8, 8) : O[0] + Math.cos(a) * len, by = toTip ? toTip[1] + rnd(-8, 8) : O[1] + Math.sin(a) * len;
        arcs.push({ pts: bolt(O[0], O[1], bx, by, .22), life: rnd(.045, .085), age: 0, w: 2.2 + power * 2.2 });
      }
      flashes.push({ age: 0, life: rnd(.08, .14), r: 80 + power * 170, a: .6 + power * .4 });
    };
    const throwSparks = (n, power) => {
      for (let i = 0; i < n; i++) {
        // the wire is at the top of the screen: most fly out to the right and arc down beside the frame, a third
        // go left over the frame's top bar (and land on it), a few straight up; hot metal leaves fast
        const u = Math.random();
        const a = u < .52 ? rnd(-1.05, .45) : u < .86 ? rnd(-2.95, -2.05) : rnd(-2.0, -1.1), sp = rnd(420, 1500) * (.55 + power * .6);
        sparks.push({ x: O[0] + rnd(-6, 6), y: O[1] + rnd(-6, 6), vx: Math.cos(a) * sp, vy: Math.sin(a) * sp,
          life: rnd(.35, 1.25), age: 0, w: rnd(3.6, 7.6), heat: rnd(.85, 1), bounced: false,
          trail: [], drag: rnd(1.5, 3) });
      }
    };
    const burst = power => {
      strike(power);
      throwSparks(Math.round(8 + power * 34), power);
      // a shorting wire stutters: one or two re-strikes a moment later, each throwing a few more
      const re = power > .55 ? 1 + (Math.random() < .6 ? 1 : 0) : (Math.random() < .3 ? 1 : 0);
      for (let i = 1; i <= re; i++) setTimeout(() => {
        if (document.hidden) return;
        strike(power * rnd(.5, .9)); throwSparks(Math.round(2 + power * 8), power * .7); wake();
      }, i * rnd(70, 150));
      if (power > .6) setTimeout(() => {
        for (let i = 0; i < 2; i++) smoke.push({ x: O[0] + rnd(-12, 12), y: O[1] - 10, vx: rnd(-18, 30), vy: rnd(-70, -40), r: rnd(16, 26), age: 0, life: rnd(.9, 1.4) });
        wake();
      }, 160);
      wake();
    };

    const G = 2500;
    const heatColour = h => {                       // white-yellow -> orange -> dull red as the metal cools
      if (h > .75) { const t = (h - .75) / .25; return [255, 238 + 17 * t, 170 + 70 * t]; }
      if (h > .45) { const t = (h - .45) / .3; return [255, 150 + 88 * t, 40 + 130 * t]; }
      const t = Math.max(0, h) / .45; return [150 + 105 * t, 40 + 110 * t, 20 + 20 * t];
    };
    const frame = now => {
      raf = 0;
      const dt = Math.min(.04, last ? (now - last) / 1000 : .016);
      last = now;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, cv.width, cv.height);
      ctx.setTransform(k, 0, 0, k, -R.x * k, -R.y * k);
      // smoke first (drawn normally, under the light)
      ctx.globalCompositeOperation = "source-over";
      for (const s of smoke) {
        s.age += dt; s.x += s.vx * dt; s.y += s.vy * dt; s.vx *= 1 - dt * .8;
        const q = s.age / s.life, rr = s.r * (1 + q * 1.6);
        const g = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, rr);
        g.addColorStop(0, `rgba(150, 156, 170, ${(.22 * (1 - q)).toFixed(3)})`); g.addColorStop(1, "rgba(150, 156, 170, 0)");
        ctx.fillStyle = g; ctx.fillRect(s.x - rr, s.y - rr, rr * 2, rr * 2);
      }
      smoke = smoke.filter(s => s.age < s.life);
      ctx.globalCompositeOperation = "lighter";
      ctx.lineCap = "round"; ctx.lineJoin = "round";
      // the flash: a white core in a blue-white bloom
      for (const f of flashes) {
        f.age += dt;
        const q = Math.min(1, f.age / f.life), a = f.a * (1 - q) * (1 - q), r = f.r * (.7 + .5 * q);
        const g = ctx.createRadialGradient(O[0], O[1], 0, O[0], O[1], r);
        g.addColorStop(0, `rgba(255, 255, 255, ${a.toFixed(3)})`); g.addColorStop(.18, `rgba(255, 248, 210, ${(a * .85).toFixed(3)})`);
        g.addColorStop(.5, `rgba(150, 205, 255, ${(a * .32).toFixed(3)})`); g.addColorStop(1, "rgba(120, 180, 255, 0)");
        ctx.fillStyle = g; ctx.fillRect(O[0] - r, O[1] - r, r * 2, r * 2);
      }
      flashes = flashes.filter(f => f.age < f.life);
      // the filaments
      for (const a of arcs) {
        a.age += dt;
        const al = 1 - a.age / a.life;
        if (al <= 0) continue;
        const path = () => { ctx.beginPath(); ctx.moveTo(a.pts[0][0], a.pts[0][1]); for (let i = 1; i < a.pts.length; i++) ctx.lineTo(a.pts[i][0], a.pts[i][1]); };
        path(); ctx.strokeStyle = `rgba(90, 200, 255, ${(.35 * al).toFixed(3)})`; ctx.lineWidth = a.w * 4.5; ctx.stroke();
        path(); ctx.strokeStyle = `rgba(190, 235, 255, ${(.7 * al).toFixed(3)})`; ctx.lineWidth = a.w * 1.9; ctx.stroke();
        path(); ctx.strokeStyle = `rgba(255, 255, 255, ${al.toFixed(3)})`; ctx.lineWidth = a.w * .8; ctx.stroke();
      }
      arcs = arcs.filter(a => a.age < a.life);
      // the sparks
      for (const s of sparks) {
        s.age += dt;
        s.trail.push([s.x, s.y]); if (s.trail.length > 7) s.trail.shift();
        const dr = Math.exp(-s.drag * dt);
        s.vx *= dr; s.vy = s.vy * dr + G * dt;
        s.x += s.vx * dt; s.y += s.vy * dt;
        // the frame's top bar is solid: a spark that lands on it bounces once, losing most of its speed
        if (!s.bounced && s.vy > 0 && s.y >= BAR_TOP && s.y - s.vy * dt < BAR_TOP + 14 && s.x < BAR_RIGHT) {
          s.y = BAR_TOP; s.vy *= -rnd(.22, .42); s.vx *= rnd(.45, .75); s.bounced = true; s.life = Math.min(s.life, s.age + rnd(.18, .45));
        }
        const q = s.age / s.life, heat = s.heat * (1 - q * q), [r, g, b] = heatColour(heat), al = Math.min(1, (1 - q) * 2.2);
        const t0 = s.trail[0];
        ctx.beginPath(); ctx.moveTo(t0[0], t0[1]);
        for (let i = 1; i < s.trail.length; i++) ctx.lineTo(s.trail[i][0], s.trail[i][1]);
        ctx.lineTo(s.x, s.y);
        ctx.strokeStyle = `rgba(${r | 0}, ${g | 0}, ${b | 0}, ${(al * .7).toFixed(3)})`; ctx.lineWidth = s.w * (1 - q * .6); ctx.stroke();
        ctx.beginPath(); ctx.arc(s.x, s.y, s.w * (.95 - q * .4), 0, 6.283);   // the bright head
        ctx.fillStyle = `rgba(${Math.min(255, r + 30) | 0}, ${Math.min(255, g + 40) | 0}, ${Math.min(255, b + 60) | 0}, ${al.toFixed(3)})`; ctx.fill();
      }
      sparks = sparks.filter(s => s.age < s.life && s.y < R.y + R.h + 40);
      if (sparks.length || arcs.length || flashes.length || smoke.length) wake();
      else { last = 0; ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, cv.width, cv.height); }
    };
    function wake() { if (!raf) raf = requestAnimationFrame(frame); }

    // every few seconds: mostly a proper arc, sometimes only a crackle; never while the tab is hidden
    const next = () => setTimeout(() => {
      if (!document.hidden && cv.clientWidth > 4) burst(Math.random() < .62 ? rnd(.65, 1) : rnd(.15, .4));
      next();
    }, rnd(2400, 5600));
    setTimeout(() => { burst(.9); next(); }, 1800);
    // the game setting it off: the breaker thrown, the power sputtering back, thunder
    let wasOn = false;                                // only as the breaker goes over, not on every class change
    new MutationObserver(() => {
      const on = document.body.classList.contains("poweron");
      if (on && !wasOn && !document.hidden) burst(rnd(.5, .8));
      wasOn = on;
    }).observe(document.body, { attributes: true, attributeFilter: ["class"] });
    addEventListener("bgpower", () => { if (!document.hidden) { burst(1); setTimeout(() => burst(.7), 420); } });
    addEventListener("bgthunder", () => { if (!document.hidden && Math.random() < .5) burst(.45); });
    window.__spark = burst;                           // (QA) fire one by hand
  }
})();
