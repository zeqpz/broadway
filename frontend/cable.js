// Power Outage: the frame's dangling power cord, hanging and swinging with physics.
//
// tools/outage/frame_cable.py took the cord and its plug out of the frame picture and wrote where the cord ran
// (assets/cable.json, in frame-picture px). Here the cord is a rope of points (Verlet): pinned under the clamp on the
// frame's right bar, pulled down by gravity, each segment held to its length, bending resisted (a stiff rubber cord),
// the plug a heavier weight at the end.
//
// Owner pass 4 (2026-11-18: "more smoothed out and not glitchy, sometimes it flies off") - what made it jump, and
// what holds it now:
//   - the board being re-fitted (a resize, the free-spin counter coming in) moved the frame hundreds of px in one frame
//     and the rope, keeping its place in the world, was flung: a jump that big is a layout change, not motion - the
//     rope moves with it. Real motion (knocks, the frame's drift) is fed in low-passed and capped per frame.
//   - the pointer was mapped with layout px against a scaled page, so a dragged plug overshot the hand, and letting go
//     of a cord stretched past its length launched it: the hand's point is mapped by the box's on-screen size and
//     kept within the cord's reach of the clamp.
//   - every point's speed is capped, the air drags harder, the solver runs more passes, the cord can't pass through
//     the frame's bar, and if any number ever goes bad the cord is hung back at rest.
//   - the plug turned with its last segment and twitched: its angle now eases after the cord's end.
// It still swings with the board's knocks, the breaker and thunder, and the plug can be grabbed and thrown.
// Drawn on a canvas in #cablebox (the frame's box, under the frame: the cord comes out from under the clamp); asleep
// once it has settled. Reduced motion: drawn once, hanging still.
(function () {
  "use strict";
  const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const box = document.getElementById("cablebox");
  if (!box) return;
  Promise.all([fetch("assets/cable.json").then(r => r.json()), new Promise((res, rej) => {
    const im = new Image(); im.onload = () => res(im); im.onerror = rej; im.src = "assets/plug.webp";
  })]).then(([C, plugImg]) => start(C, plugImg)).catch(() => { /* no cord: the frame still reads */ });

  function start(C, plugImg) {
    const [FW, FH] = C.frame;
    const R = { x: FW * .74, y: FH * .64, w: FW * .42, h: FH * .6 };      // the canvas's patch of the frame picture
    const cv = document.createElement("canvas");
    cv.className = "cablecv";
    Object.assign(cv.style, { left: (R.x / FW * 100) + "%", top: (R.y / FH * 100) + "%",
      width: (R.w / FW * 100) + "%", height: (R.h / FH * 100) + "%" });
    box.appendChild(cv);
    const grab = document.createElement("i");                              // the plug's handle: grab it and throw it
    grab.className = "cablegrab";
    box.appendChild(grab);
    const ctx = cv.getContext("2d");

    // the rope's starting shape: the drawn centreline from the clamp to where it goes into the plug, resampled
    const line = C.line.filter(p => p[1] <= C.neck[1]).concat([C.neck]);
    const cum = [0];
    for (let i = 1; i < line.length; i++) cum.push(cum[i - 1] + Math.hypot(line[i][0] - line[i - 1][0], line[i][1] - line[i - 1][1]));
    // (owner pass 4) the board is bigger now and the bar sits right under the frame: the cord is 62% of its drawn
    // length and the plug 78% of its size, so the plug dangles beside the frame's corner instead of over the bar
    const LEN_K = .62, PLUG_K = .78;
    const L = cum[cum.length - 1] * LEN_K, N = 12;
    const at = s => {
      let i = 1; while (i < cum.length - 1 && cum[i] < s) i++;
      const t = (s - cum[i - 1]) / Math.max(1e-6, cum[i] - cum[i - 1]);
      return [line[i - 1][0] + (line[i][0] - line[i - 1][0]) * t, line[i - 1][1] + (line[i][1] - line[i - 1][1]) * t];
    };
    const REST = Array.from({ length: N }, (_, i) => at(L * i / (N - 1)));
    const P = REST.map(([x, y]) => ({ x, y, px: x, py: y }));
    const seg = L / (N - 1);
    const pin = [REST[0], REST[1]];                                        // under the clamp the cord can't move
    const neckIn = [(C.neck[0] - C.plug[0]) * PLUG_K, (C.neck[1] - C.plug[1]) * PLUG_K];
    const PW = C.plug[2] * PLUG_K, PH = C.plug[3] * PLUG_K;
    const THICK = C.thick, INK = Math.max(6, THICK * .13);
    // the way the cord runs into the plug in the drawing (the END of the whole drawn line): the plug's own "down"
    const FULL = cum[cum.length - 1], e1 = at(FULL), e0 = at(FULL - 70);
    const restAng = Math.atan2(e1[1] - e0[1], e1[0] - e0[0]);
    // the frame's right bar the cord hangs beside: it can't go left of this while it is above the frame's bottom
    const BAR_X = (C.bar_right || FW * .93) + THICK * .42, BAR_BOTTOM = C.frame_bottom || FH * .876;

    const G = 5200, DT = 1 / 120, DAMP = .985, VMAX = 46, ITER = 16;      // frame px, s; VMAX per step
    let acc = 0, lastT = 0, lastRect = null, still = 99, drag = null, kick = 0, plugAng = 0, shakeX = 0, shakeY = 0;

    const hang = () => { P.forEach((p, i) => { p.x = p.px = REST[i][0]; p.y = p.py = REST[i][1]; }); plugAng = 0; };
    const sane = () => P.every(p => Number.isFinite(p.x) && Number.isFinite(p.y) &&
      Math.hypot(p.x - pin[0][0], p.y - pin[0][1]) < L * 1.6);

    const step = () => {
      for (let i = 2; i < N; i++) {
        const p = P[i];
        let vx = (p.x - p.px) * DAMP, vy = (p.y - p.py) * DAMP;
        const v = Math.hypot(vx, vy);
        if (v > VMAX) { vx *= VMAX / v; vy *= VMAX / v; }
        p.px = p.x; p.py = p.y;
        p.x += vx; p.y += vy + G * DT * DT;
      }
      if (drag) {                                                     // the plug follows the hand, springily
        const e = P[N - 1];
        e.x += (drag.x - e.x) * .3; e.y += (drag.y - e.y) * .3;
      }
      for (let k = 0; k < ITER; k++) {
        P[0].x = pin[0][0]; P[0].y = pin[0][1]; P[1].x = pin[1][0]; P[1].y = pin[1][1];
        for (let i = 1; i < N - 1; i++) {                             // each segment its length (the plug is heavy)
          const a = P[i], b = P[i + 1], dx = b.x - a.x, dy = b.y - a.y, d = Math.hypot(dx, dy) || 1e-6, f = (d - seg) / d;
          const wa = i < 2 ? 0 : (i + 1 === N - 1 ? .7 : .5), wb = 1 - wa;
          a.x += dx * f * wa; a.y += dy * f * wa; b.x -= dx * f * wb; b.y -= dy * f * wb;
        }
        for (let i = 0; i < N - 2; i++) {                             // bending: a point is pulled toward the middle
          const a = P[i], m = P[i + 1], b = P[i + 2];                 // of its neighbours (soft, so it still swings)
          if (i + 1 < 2) continue;
          const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
          m.x += (mx - m.x) * .09; m.y += (my - m.y) * .09;
        }
        for (let i = 2; i < N; i++) {                                 // the frame's bar is solid
          const p = P[i];
          if (p.y < BAR_BOTTOM && p.x < BAR_X) p.x = BAR_X;
        }
      }
    };

    const draw = () => {
      const k = cv.width / R.w;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, cv.width, cv.height);
      ctx.setTransform(k, 0, 0, k, -R.x * k, -R.y * k);
      ctx.lineCap = "round"; ctx.lineJoin = "round";
      const path = () => {
        ctx.beginPath(); ctx.moveTo(P[0].x, P[0].y);
        for (let i = 1; i < N - 1; i++) ctx.quadraticCurveTo(P[i].x, P[i].y, (P[i].x + P[i + 1].x) / 2, (P[i].y + P[i + 1].y) / 2);
        ctx.lineTo(P[N - 1].x, P[N - 1].y);
      };
      path(); ctx.strokeStyle = "#0b0b0d"; ctx.lineWidth = THICK; ctx.stroke();                 // its black outline
      path(); ctx.strokeStyle = "#383b42"; ctx.lineWidth = THICK - 2 * INK; ctx.stroke();       // the rubber
      ctx.save(); ctx.translate(-THICK * .14, -THICK * .06);
      path(); ctx.strokeStyle = "rgba(120, 126, 140, .55)"; ctx.lineWidth = THICK * .16; ctx.stroke();   // its sheen
      ctx.restore();
      // the plug: its angle eases after the cord's end (averaged over the last two segments), so it never twitches
      const e = P[N - 1], f = P[N - 3];
      let want = Math.atan2(e.y - f.y, e.x - f.x) - restAng;
      want = Math.atan2(Math.sin(want), Math.cos(want));
      let d = want - plugAng; d = Math.atan2(Math.sin(d), Math.cos(d));
      plugAng += d * .22;
      ctx.save(); ctx.translate(e.x, e.y); ctx.rotate(plugAng);
      ctx.drawImage(plugImg, -neckIn[0], -neckIn[1], PW, PH);
      ctx.restore();
      const gx = e.x + Math.cos(plugAng + Math.PI / 2) * PH * .45, gy = e.y + Math.sin(plugAng + Math.PI / 2) * PH * .45;
      grab.style.left = (gx / FW * 100) + "%"; grab.style.top = (gy / FH * 100) + "%";
    };

    const fit = () => {
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      const w = Math.max(2, Math.round(cv.clientWidth * dpr)), h = Math.max(2, Math.round(cv.clientHeight * dpr));
      if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
      lastRect = null;                                               // the layout moved: nothing to carry over
      draw();
    };
    // it starts where it hangs: the drawn curve is let fall and settle before anything is shown, and that pose is
    // the rest it is put back to if it ever needs to be
    for (let i = 0; i < 900; i++) step();
    P.forEach((p, i) => { p.px = p.x; p.py = p.y; REST[i] = [p.x, p.y]; });
    new ResizeObserver(fit).observe(cv);
    addEventListener("resize", () => { lastRect = null; });
    fit();
    if (REDUCED) return;

    let wasOn = false;                                // only as the breaker goes over, not on every class change
    new MutationObserver(() => {
      const on = document.body.classList.contains("poweron");
      if (on && !wasOn) kick = 1;
      wasOn = on;
    }).observe(document.body, { attributes: true, attributeFilter: ["class"] });
    addEventListener("bgthunder", () => { kick = Math.max(kick, .4); });

    const loop = now => {
      requestAnimationFrame(loop);
      if (document.hidden) { lastT = 0; lastRect = null; return; }
      const t = now / 1000;
      if (!lastT) lastT = t;
      const frame = Math.min(.05, t - lastT);                         // a stalled tab doesn't dump its backlog on the rope
      acc += frame; lastT = t;
      const r = box.getBoundingClientRect();
      if (r.width < 20) { lastRect = null; return; }                 // not laid out (hidden, mid-fit)
      const s = FW / r.width;                                        // frame px per screen px
      if (lastRect && Math.abs(r.width - lastRect.width) < .5) {
        let dx = (r.left - lastRect.left) * s, dy = (r.top - lastRect.top) * s;
        // a real knock moves the frame a few px a frame; more than that is the page being laid out again
        if (Math.hypot(dx, dy) < 90) {
          shakeX += (dx - shakeX) * .55; shakeY += (dy - shakeY) * .55;   // low-passed
          const cap = 16, m = Math.hypot(shakeX, shakeY), q = m > cap ? cap / m : 1;
          for (let i = 2; i < N; i++) { const w = i / (N - 1); P[i].x -= shakeX * q * w; P[i].y -= shakeY * q * w; }
        } else { shakeX = shakeY = 0; }
      }
      lastRect = r;
      if (kick) {                                                    // a soft jolt down the cord
        for (let i = 3; i < N; i++) P[i].px -= (i / N) * 3.2 * kick;
        kick = 0; still = 0;
      }
      const breeze = Math.sin(t * .7) * Math.sin(t * .23 + 1) * .03;   // a draught through the dark office
      for (let i = 5; i < N; i++) P[i].px -= breeze * (i / N);
      let moved = 0, steps = 0;
      while (acc >= DT && steps < 8) {
        const bx = P[N - 1].x, by = P[N - 1].y;
        step(); acc -= DT; steps++;
        moved = Math.max(moved, Math.abs(P[N - 1].x - bx) + Math.abs(P[N - 1].y - by));
      }
      if (acc > DT * 2) acc = 0;
      if (!sane()) { hang(); still = 0; }
      still = moved < .02 && !drag ? still + 1 : 0;
      if (still < 40) draw();
    };
    requestAnimationFrame(loop);

    // grab the plug and throw it: the hand's point in frame px, kept within the cord's reach of the clamp
    const toLocal = ev => {
      const r = box.getBoundingClientRect(), s = FW / Math.max(1, r.width);
      let x = (ev.clientX - r.left) * s, y = (ev.clientY - r.top) * s;
      const dx = x - pin[0][0], dy = y - pin[0][1], d = Math.hypot(dx, dy), reach = L * .97;
      if (d > reach) { x = pin[0][0] + dx / d * reach; y = pin[0][1] + dy / d * reach; }
      return { x, y };
    };
    grab.addEventListener("pointerdown", ev => {
      ev.preventDefault(); ev.stopPropagation();
      try { grab.setPointerCapture(ev.pointerId); } catch (e) { /* not capturable */ }
      drag = toLocal(ev); grab.classList.add("held"); still = 0;
    });
    grab.addEventListener("pointermove", ev => { if (drag) drag = toLocal(ev); });
    const drop = () => { drag = null; grab.classList.remove("held"); };
    grab.addEventListener("pointerup", drop); grab.addEventListener("pointercancel", drop);
    grab.addEventListener("lostpointercapture", drop);
    addEventListener("pointerup", drop, true); addEventListener("pointercancel", drop, true); addEventListener("blur", drop);
    grab.addEventListener("click", ev => ev.stopPropagation());
  }
})();
