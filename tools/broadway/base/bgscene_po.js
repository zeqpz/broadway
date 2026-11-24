// Power Outage: the blacked-out office behind the board, kept alive.
//
// The painting (assets/bonus_wall.webp; in the Xtreme Bonus assets/bonus_wall_xtreme.webp, the same room under red
// emergency light) is the dark room; tools/outage/bg_layers.py measured where its candles, moon, chandelier and windows
// are (assets/bg/scene.json) and cut the window sky as one shape (assets/bg/sky.webp).
//
// The light is soft and alive (owner pass 2, 2026-11-18: "more realistic lighting that flickers"):
//   candles     each flame is a live flat cartoon flame over the painted one, and round it a soft halo, a pool of warm
//               light on the wall and a wide faint glow into the room - all four driven by ONE flicker signal per
//               candle (layered noise: a slow breath, a quicker waver and now and then a gutter), so the light in the
//               room moves exactly with its flame
//   room        the whole room's darkness breathes very slightly with the candles
//   flashlights two bodyguards' beams: a soft cone from off-screen (left or right) with a bright hotspot where it
//               lands, sweeping across the rug and the furniture with a hand's small jitter, on their own clocks
//   lightning   the sky in the windows flashes twice, a flat bolt cracks in it and the room blinks pale blue (in the
//               Xtreme Bonus far more often, and pinkish)
//   clouds      flat clouds drift past the moon, behind the dark towers
//   skyline     a lit window comes on somewhere in the dead city, and goes out again
//   power       now and then the power sputters back on in fits and dies again (window "bgpower" event)
//   alarm       in the Xtreme Bonus the red alarm lamp on the wall turns: its beam swings round the lamp's own
//               upright axis (long from the side, foreshortened as it comes round), the glass flares as the beam
//               passes us and the wall behind it lights as it passes the wall
// Only opacity and transform change per frame (the compositor's work); the loop runs at up to 30 fps and stops while
// the tab is hidden. Reduced motion: everything lit and still. Seeded: the room behaves the same on every load.
(function () {
  "use strict";
  const wall = document.getElementById("bgwall");
  if (!wall) return;
  const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const scene = document.createElement("div");
  scene.id = "bgscene";
  scene.setAttribute("aria-hidden", "true");
  wall.appendChild(scene);

  let seed = 2026;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;
  const rr = (a, b) => a + (b - a) * rnd();
  const pct = v => (v * 100).toFixed(3) + "%";
  const later = (ms, fn) => setTimeout(() => { if (document.hidden) later(2000, fn); else fn(); }, ms);
  const el = (cls, parent = scene) => { const e = document.createElement("i"); e.className = cls; parent.appendChild(e); return e; };
  const xtreme = () => document.body.classList.contains("xtreme");

  const FLAME = `<svg viewBox="0 0 40 100" preserveAspectRatio="none"><path d="M20 2 C27 26 38 40 37 64 C36 86 29 98 20 98 C11 98 4 86 3 64 C2 40 13 26 20 2Z" fill="#FF9A3C" stroke="#3a1e08" stroke-width="3"/><path d="M20 30 C25 46 31 56 30 70 C29 84 25 91 20 91 C15 91 11 84 10 70 C9 56 15 46 20 30Z" fill="#FFD54A"/><path d="M20 56 C23 64 25 70 24.5 78 C24 85 22.5 88 20 88 C17.5 88 16 85 15.5 78 C15 70 17 64 20 56Z" fill="#FFF6C8"/></svg>`;
  const BOLT = `<svg viewBox="0 0 60 200" preserveAspectRatio="none"><path d="M34 0 L8 92 L28 92 L12 200 L54 70 L32 70 L46 0Z" fill="#F4F8FF" stroke="#1a2440" stroke-width="3"/></svg>`;
  const CLOUD = `<svg viewBox="0 0 200 80"><path d="M20 70 C2 70 0 50 16 44 C12 26 34 18 46 28 C52 8 84 4 94 24 C104 10 132 12 136 32 C152 22 176 30 172 48 C192 50 196 70 178 70Z" fill="#2B3A66" stroke="#141B33" stroke-width="3"/><path d="M28 44 C30 34 42 30 50 36 M98 28 C104 20 120 20 126 32" fill="none" stroke="#4A5C92" stroke-width="5" stroke-linecap="round"/></svg>`;

  // a candle's flicker: 1 at rest, ~0.75-1.15 as it moves; smooth value noise on three scales plus rare gutters
  function flicker(seedOffset) {
    const ph = [rr(0, 6.3), rr(0, 6.3), rr(0, 6.3)];
    let gutter = 0, nextGutter = rr(2, 7);
    return t => {
      const s = .06 * Math.sin(t * 1.3 + ph[0]) + .05 * Math.sin(t * 3.7 + ph[1]) * Math.sin(t * 1.1 + seedOffset)
              + .04 * Math.sin(t * 9.3 + ph[2]) * Math.sin(t * 5.1);
      if (t > nextGutter) { gutter = 1; nextGutter = t + rr(2.5, 9); }
      gutter *= .9;                                                     // a quick dip that recovers
      return 1 + s - .22 * gutter * (.6 + .4 * Math.sin(t * 40));
    };
  }

  fetch("assets/bg/scene.json").then(r => r.json()).then(build).catch(() => { /* the painting alone still reads */ });

  function build(S) {
    const AR = S.size[1] / S.size[0];
    const room = el("bgroom");                     // power-back / lightning wash
    const dark = el("bgdark");                     // the room's darkness, breathing with the candles
    const [cx, cy, cr] = S.chandelier;
    const powerGlow = el("bgchand");
    Object.assign(powerGlow.style, { left: pct(cx - cr), top: pct(cy - cr / AR), width: pct(cr * 2), height: pct(cr * 2 / AR) });

    // window sky: clouds (masked to it), the flash and a bolt
    const [sx, sy, sw, sh] = S.sky;
    const skyBox = el("bgsky");
    Object.assign(skyBox.style, { left: pct(sx), top: pct(sy), width: pct(sw), height: pct(sh) });
    for (let i = 0; i < 3; i++) {
      const c = el("bgcloud", skyBox);
      c.innerHTML = CLOUD;
      c.style.top = (8 + i * 13 + rr(-3, 3)).toFixed(1) + "%";
      c.style.width = (18 + rr(0, 10)).toFixed(1) + "%";
      c.style.setProperty("--dur", (70 + i * 28 + rr(0, 20)).toFixed(0) + "s");
      c.style.setProperty("--delay", (-rr(0, 90)).toFixed(0) + "s");
    }
    const flash = document.createElement("img");
    flash.className = "bgflash"; flash.src = "assets/bg/sky.webp"; flash.alt = "";
    skyBox.appendChild(flash);
    const bolt = el("bgbolt", skyBox);
    bolt.innerHTML = BOLT;

    const lights = S.lights.map(([x, y]) => {
      const l = el("bglight");
      Object.assign(l.style, { left: pct(x - .0022), top: pct(y - .0045), width: pct(.0044), height: pct(.009) });
      return l;
    });

    // every candle: a wide faint room glow, a warm pool on the wall, a halo round the flame, the flame itself
    const placeCandle = (c, [x, y, h]) => {
      const g = .2, p = .055, hr = h * .9;
      Object.assign(c.glow.style, { left: pct(x - g), top: pct(y - h * .5 - g / AR), width: pct(g * 2), height: pct(g * 2 / AR) });
      Object.assign(c.pool.style, { left: pct(x - p), top: pct(y - h * .6 - p / AR), width: pct(p * 2), height: pct(p * 2 / AR) });
      Object.assign(c.halo.style, { left: pct(x - hr * AR), top: pct(y - h * .55 - hr), width: pct(hr * 2 * AR), height: pct(hr * 2) });
      const hh = h * 1.22, ww = hh * .46 * AR;
      Object.assign(c.f.style, { left: pct(x - ww / 2), top: pct(y - hh), width: pct(ww), height: pct(hh) });
    };
    const candles = S.flames.map((spec, i) => {
      const c = { glow: el("bgglow"), pool: el("bgpool"), halo: el("bghalo"), f: el("bgflame"), fl: flicker(i * 1.7) };
      c.f.innerHTML = FLAME;
      placeCandle(c, spec);
      return c;
    });
    // the Xtreme Bonus swaps the painting for the red emergency room: its candles sit a touch lower, its windows
    // already show the storm (the normal sky's flash, clouds and lit windows are put away), its beacon turns
    const X = S.xtreme;
    const setMode = () => {
      const on = xtreme();
      scene.classList.toggle("xtreme", on);
      candles.forEach((c, i) => placeCandle(c, (on && X ? X.flames : S.flames)[i]));
    };
    new MutationObserver(setMode).observe(document.body, { attributes: true, attributeFilter: ["class"] });

    // two flashlight beams, each a cone with a hotspot at its end, swung from off-screen
    const beams = [{ side: 1 }, { side: -1 }].map(b => {
      const root = el("bgbeam" + (b.side < 0 ? " left" : ""));
      root.innerHTML = `<i class="cone"></i><i class="spot"></i>`;
      return Object.assign(b, { root, on: 0, t0: 0, dur: 0, a0: 0, a1: 0, y: 0 });
    });

    // the Xtreme Bonus's alarm beacon on the ceiling
    const beacon = el("bgbeacon");
    beacon.innerHTML = `<i class="wash"></i><i class="ray"></i><i class="lamp"></i>`;
    const [bWash, bRay, bLamp] = beacon.children;
    const [bxp, byp] = X ? X.beacon : [cx + .07, cy - .03];
    Object.assign(beacon.style, { left: pct(bxp), top: pct(byp) });
    setMode();

    if (REDUCED) return;

    // the frame loop: candles, darkness, beams, beacon - opacity and transform only, at most 30 fps
    let last = 0;
    const loop = now => {
      requestAnimationFrame(loop);
      if (document.hidden || now - last < 33) return;
      last = now;
      const t = now / 1000;
      let sum = 0;
      for (const c of candles) {
        const k = c.fl(t);
        sum += k;
        c.f.style.transform = `scale(${(.94 + .1 * k).toFixed(3)}, ${(.82 + .2 * k).toFixed(3)}) skewX(${(Math.sin(t * 2.3 + k * 3) * 4).toFixed(2)}deg)`;
        c.halo.style.opacity = (.55 + .45 * (k - .75) / .4).toFixed(3);
        c.halo.style.transform = `scale(${(.9 + .18 * k).toFixed(3)})`;
        c.pool.style.opacity = (.45 + .55 * (k - .75) / .4).toFixed(3);
        c.pool.style.transform = `scale(${(.94 + .1 * k).toFixed(3)})`;
        c.glow.style.opacity = (.5 + .5 * (k - .75) / .4).toFixed(3);
      }
      const avg = sum / Math.max(1, candles.length);
      dark.style.opacity = (.26 - .16 * (avg - .85)).toFixed(3);
      for (const b of beams) {
        if (!b.on) { b.root.style.opacity = 0; continue; }
        const u = (now - b.t0) / b.dur;
        if (u >= 1) { b.on = 0; b.root.style.opacity = 0; continue; }
        const e = u * u * (3 - 2 * u);
        const jit = Math.sin(t * 7.1) * .6 + Math.sin(t * 13.3) * .35;            // a hand holding it
        const ang = b.a0 + (b.a1 - b.a0) * e + jit;
        b.root.style.opacity = Math.min(1, Math.min(u, 1 - u) * 6).toFixed(3);
        b.root.style.transform = `translateY(${b.y.toFixed(1)}%) rotate(${(b.side * ang).toFixed(2)}deg)`;
      }
      if (xtreme()) {
        // one reflector turning about the lamp's upright axis, a turn every 1.7 s: c is how far the beam points
        // right (+) or left (-), s how far toward us (+) or into the wall (-)
        const a = t * 3.7, c = Math.cos(a), s = Math.sin(a);
        const near = Math.max(0, s) ** 3, far = Math.max(0, -s) ** 2;
        bRay.style.transform = `scaleX(${c.toFixed(3)}) rotate(7deg)`;
        bRay.style.opacity = ((.2 + .8 * Math.abs(c)) * (1 - .5 * far)).toFixed(3);
        bLamp.style.opacity = (.5 + .5 * near).toFixed(3);
        bLamp.style.transform = `scale(${(1 + 1.5 * near).toFixed(3)})`;
        bWash.style.opacity = (.16 + .5 * far + .34 * near).toFixed(3);
      }
    };
    requestAnimationFrame(loop);

    // lightning: a double flash of the sky, a bolt, the room blinks
    const strike = () => {
      const x = rr(8, 80), hot = xtreme();
      bolt.style.left = x.toFixed(1) + "%";
      bolt.style.transform = `scaleX(${rnd() < .5 ? -1 : 1})`;
      const seq = [[0, .95], [70, 0], [160, .7], [230, .15], [330, 0]];
      for (const [tt, o] of seq) setTimeout(() => {
        flash.style.opacity = o; bolt.style.opacity = o > .5 ? 1 : 0; room.style.opacity = o * .55;
        room.style.background = hot ? "rgba(255, 190, 220, .24)" : "rgba(190, 215, 255, .22)";
      }, tt);
      window.dispatchEvent(new CustomEvent("bgthunder"));
      later(hot ? rr(3500, 8000) : rr(14000, 30000), strike);
    };
    later(rr(5000, 9000), strike);

    const power = () => {
      if (!xtreme()) {
        const fits = [[0, 1], [110, 0], [190, .8], [300, 0], [380, 1], [900, .9], [960, 0], [1040, .5], [1110, 0]];
        for (const [tt, o] of fits) setTimeout(() => {
          powerGlow.style.opacity = o; room.style.opacity = o; room.style.background = "rgba(255, 226, 150, .2)";
        }, tt);
        window.dispatchEvent(new CustomEvent("bgpower"));
      }
      later(rr(28000, 52000), power);
    };
    later(rr(16000, 24000), power);

    const blink = () => {
      const l = lights[Math.floor(rnd() * lights.length)];
      if (l) { l.classList.add("on"); later(rr(1800, 6000), () => l.classList.remove("on")); }
      later(rr(1500, 4500), blink);
    };
    later(1200, blink);

    // a beam swings across the room now and then; the two bodyguards take turns
    const sweep = b => {
      b.on = 1; b.t0 = performance.now(); b.dur = rr(5200, 8200);
      b.a0 = rr(14, 22); b.a1 = rr(-24, -10); b.y = rr(-8, 10);
      later(rr(22000, 40000), () => sweep(b));
    };
    later(rr(6000, 10000), () => sweep(beams[0]));
    later(rr(17000, 26000), () => sweep(beams[1]));
  }
})();
