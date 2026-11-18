// Power Outage: the frame's dangling power cord, hanging and swinging with real physics (owner pass 3, 2026-11-18).
//
// tools/outage/frame_cable.py took the cord and its plug out of the frame picture and wrote where the cord ran
// (assets/cable.json, in frame-picture px). Here the cord is a rope of points (Verlet integration): pinned under the
// clamp on the frame's right bar, pulled down by gravity, each segment held to its length, every second point held to
// its drawn spacing too (a stiff rubber cord keeps its curve instead of folding), the plug a heavier weight at the end.
// It is alive because the world moves it: the board's knocks and shakes, the frame's idle drift (the rope keeps its
// inertia while its clamp moves), a kick when the breaker is thrown, a little draught - and you can grab the plug and
// throw it. Drawn on a canvas in #cablebox (the frame's own box, under the frame so the cord comes out from under the
// clamp), at up to 60 fps, idle when it has settled and the tab is hidden. Reduced motion: drawn once, hanging still.
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
    const R = { x: FW * .78, y: FH * .66, w: FW * .36, h: FH * .56 };     // the canvas's patch of the frame picture
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
    const L = cum[cum.length - 1], N = 15;
    const at = s => {
      let i = 1; while (i < cum.length - 1 && cum[i] < s) i++;
      const t = (s - cum[i - 1]) / Math.max(1e-6, cum[i] - cum[i - 1]);
      return [line[i - 1][0] + (line[i][0] - line[i - 1][0]) * t, line[i - 1][1] + (line[i][1] - line[i - 1][1]) * t];
    };
    const P = Array.from({ length: N }, (_, i) => { const [x, y] = at(L * i / (N - 1)); return { x, y, px: x, py: y }; });
    const seg = L / (N - 1);
    const rest2 = P.slice(0, N - 2).map((p, i) => Math.hypot(P[i + 2].x - p.x, P[i + 2].y - p.y));
    const pin = [{ x: P[0].x, y: P[0].y }, { x: P[1].x, y: P[1].y }];     // under the clamp the cord can't move
    // the plug hangs off the last point at the angle the cord went into it
    const restAng = Math.atan2(P[N - 1].y - P[N - 2].y, P[N - 1].x - P[N - 2].x);
    const neckIn = [C.neck[0] - C.plug[0], C.neck[1] - C.plug[1]];
    const THICK = C.thick, INK = Math.max(6, THICK * .13);

    const G = 6200, AIR = .996, DT = 1 / 120;
    let acc = 0, lastT = 0, lastRect = null, still = 0, drag = null, kick = 0;

    const step = () => {
      for (let i = 2; i < N; i++) {
        const p = P[i], vx = (p.x - p.px) * AIR, vy = (p.y - p.py) * AIR;
        p.px = p.x; p.py = p.y;
        p.x += vx; p.y += vy + G * DT * DT;
      }
      if (drag) {                                                     // the plug follows the hand, springily
        const e = P[N - 1];
        e.x += (drag.x - e.x) * .35; e.y += (drag.y - e.y) * .35;
      }
      for (let k = 0; k < 10; k++) {
        P[0].x = pin[0].x; P[0].y = pin[0].y; P[1].x = pin[1].x; P[1].y = pin[1].y;
        for (let i = 0; i < N - 1; i++) {                             // each segment its length
          const a = P[i], b = P[i + 1], dx = b.x - a.x, dy = b.y - a.y, d = Math.hypot(dx, dy) || 1e-6, f = (d - seg) / d;
          const wa = i < 2 ? 0 : (i + 1 === N - 1 ? .75 : .5), wb = i + 1 === N - 1 ? .25 : (i < 2 ? 1 : .5);   // the plug is heavy
          a.x += dx * f * wa; a.y += dy * f * wa; b.x -= dx * f * wb; b.y -= dy * f * wb;
        }
        for (let i = 0; i < N - 2; i++) {                             // a stiff cord: every second point keeps its spacing
          const a = P[i], b = P[i + 2], dx = b.x - a.x, dy = b.y - a.y, d = Math.hypot(dx, dy) || 1e-6;
          const f = (d - rest2[i]) / d * .12, wa = i < 2 ? 0 : .5, wb = i < 2 ? 1 : .5;
          a.x += dx * f * wa; a.y += dy * f * wa; b.x -= dx * f * wb; b.y -= dy * f * wb;
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
      // the plug, turned with the cord's end
      const e = P[N - 1], f = P[N - 2], ang = Math.atan2(e.y - f.y, e.x - f.x) - restAng;
      ctx.save(); ctx.translate(e.x, e.y); ctx.rotate(ang);
      ctx.drawImage(plugImg, -neckIn[0], -neckIn[1]);
      ctx.restore();
      // the grab handle sits on the plug
      const gx = e.x + Math.cos(ang + Math.PI / 2) * C.plug[3] * .45, gy = e.y + Math.sin(ang + Math.PI / 2) * C.plug[3] * .45;
      grab.style.left = (gx / FW * 100) + "%"; grab.style.top = (gy / FH * 100) + "%";
    };

    const fit = () => {
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      const w = Math.max(2, Math.round(cv.clientWidth * dpr)), h = Math.max(2, Math.round(cv.clientHeight * dpr));
      if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
      draw();
    };
    new ResizeObserver(fit).observe(cv);
    fit();
    if (REDUCED) return;

    // the world moving the cord: inertia while the clamp moves (board knocks, frame drift), the breaker's kick,
    // thunder, a draught
    const toFrame = () => FW / Math.max(1, box.clientWidth);
    document.body.addEventListener("transitionstart", () => {}, { passive: true });
    new MutationObserver(() => { if (document.body.classList.contains("poweron")) kick = 1; })
      .observe(document.body, { attributes: true, attributeFilter: ["class"] });
    window.addEventListener("bgthunder", () => { kick = .35; });

    const loop = now => {
      requestAnimationFrame(loop);
      if (document.hidden) { lastT = 0; return; }
      const t = now / 1000;
      if (!lastT) lastT = t;
      acc = Math.min(.1, acc + (t - lastT)); lastT = t;
      const r = box.getBoundingClientRect();
      if (lastRect) {
        const s = toFrame(), dx = (r.left - lastRect.left) * s, dy = (r.top - lastRect.top) * s;
        if (dx || dy) for (let i = 2; i < N; i++) { P[i].x -= dx; P[i].y -= dy; }   // the rope keeps its place in the world
      }
      lastRect = r;
      if (kick) {                                                    // a jolt down the cord
        for (let i = 3; i < N; i++) P[i].px -= (i / N) * 4 * kick * (i % 2 ? 1 : .7);
        kick = 0;
      }
      const breeze = Math.sin(t * .7) * Math.sin(t * .23 + 1) * .05;   // a draught through the dark office
      for (let i = 4; i < N; i++) P[i].px -= breeze * (i / N);
      let moved = 0;
      while (acc >= DT) {
        const before = P[N - 1].x + P[N - 1].y;
        step(); acc -= DT;
        moved = Math.max(moved, Math.abs(P[N - 1].x + P[N - 1].y - before));
      }
      still = moved < .01 && !drag ? still + 1 : 0;
      if (still < 30) draw();
    };
    requestAnimationFrame(loop);

    // grab the plug and throw it
    const toLocal = ev => {
      const r = box.getBoundingClientRect(), s = toFrame();
      return { x: (ev.clientX - r.left) * s, y: (ev.clientY - r.top) * s };
    };
    grab.addEventListener("pointerdown", ev => {
      ev.preventDefault(); ev.stopPropagation();
      grab.setPointerCapture(ev.pointerId);
      drag = toLocal(ev); grab.classList.add("held");
    });
    grab.addEventListener("pointermove", ev => { if (drag) drag = toLocal(ev); });
    const drop = () => { drag = null; grab.classList.remove("held"); };
    grab.addEventListener("pointerup", drop); grab.addEventListener("pointercancel", drop);
    grab.addEventListener("click", ev => ev.stopPropagation());
  }
})();
