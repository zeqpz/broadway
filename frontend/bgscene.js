// Power Outage: the blacked-out office behind the board, kept alive in flat cartoon layers.
//
// The painting (assets/bonus_wall.webp) is the dark room; tools/outage/bg_layers.py measured where its candles, moon,
// chandelier and windows are (assets/bg/scene.json) and cut the window sky as one shape (assets/bg/sky.webp).
//   flames     every candle burns with a live flat cartoon flame drawn over the painted one, on its own clock,
//              and its flat pool of light on the wall breathes with it
//   lightning  now and then the sky in the windows flashes (twice, like real lightning), a flat bolt cracks in it
//              and the whole room blinks pale blue
//   clouds     flat clouds drift past the moon, masked by the window sky (behind the dark towers)
//   skyline    a lit window comes on somewhere in the dead city, and goes out again
//   power      every so often the power sputters back - the chandelier and the room light up in fits - and dies
//              again with a fizz (window "bgpower" event, for the sound)
//   flashlight a bodyguard's flashlight beam sweeps slowly across the room from the right
// Everything sits in #bgscene (a 16:9 box sized to cover #bgwall), so the layers stay on their marks at any window
// shape. Reduced motion: the flames burn still, nothing else moves. Seeded: the room behaves the same on every load.
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

  // a flat cartoon flame: outer candle yellow, a pale core, a thin dark outline - drawn on twos like a cel cartoon
  const FLAME = `<svg viewBox="0 0 40 100" preserveAspectRatio="none"><path d="M20 2 C27 26 38 40 37 64 C36 86 29 98 20 98 C11 98 4 86 3 64 C2 40 13 26 20 2Z" fill="#FF9A3C" stroke="#3a1e08" stroke-width="3"/><path d="M20 30 C25 46 31 56 30 70 C29 84 25 91 20 91 C15 91 11 84 10 70 C9 56 15 46 20 30Z" fill="#FFD54A"/><path d="M20 56 C23 64 25 70 24.5 78 C24 85 22.5 88 20 88 C17.5 88 16 85 15.5 78 C15 70 17 64 20 56Z" fill="#FFF6C8"/></svg>`;
  const BOLT = `<svg viewBox="0 0 60 200" preserveAspectRatio="none"><path d="M34 0 L8 92 L28 92 L12 200 L54 70 L32 70 L46 0Z" fill="#F4F8FF" stroke="#1a2440" stroke-width="3"/></svg>`;
  const CLOUD = `<svg viewBox="0 0 200 80"><path d="M20 70 C2 70 0 50 16 44 C12 26 34 18 46 28 C52 8 84 4 94 24 C104 10 132 12 136 32 C152 22 176 30 172 48 C192 50 196 70 178 70Z" fill="#2B3A66" stroke="#141B33" stroke-width="3"/><path d="M28 44 C30 34 42 30 50 36 M98 28 C104 20 120 20 126 32" fill="none" stroke="#4A5C92" stroke-width="5" stroke-linecap="round"/></svg>`;

  fetch("assets/bg/scene.json").then(r => r.json()).then(build).catch(() => { /* the painting alone still reads */ });

  function build(S) {
    const AR = S.size[1] / S.size[0];
    // ---- the room's light overlays (under everything else we add)
    const room = el("bgroom");
    const powerGlow = el("bgchand");
    const [cx, cy, cr] = S.chandelier;
    Object.assign(powerGlow.style, { left: pct(cx - cr), top: pct(cy - cr / AR), width: pct(cr * 2), height: pct(cr * 2 / AR) });

    // ---- the window sky: clouds (masked to it) and the lightning flash
    const [sx, sy, sw, sh] = S.sky;
    const skyBox = el("bgsky");
    Object.assign(skyBox.style, { left: pct(sx), top: pct(sy), width: pct(sw), height: pct(sh) });
    const clouds = [];
    for (let i = 0; i < 3; i++) {
      const c = el("bgcloud", skyBox);
      c.innerHTML = CLOUD;
      c.style.top = (8 + i * 13 + rr(-3, 3)).toFixed(1) + "%";
      c.style.width = (18 + rr(0, 10)).toFixed(1) + "%";
      c.style.setProperty("--dur", (70 + i * 28 + rr(0, 20)).toFixed(0) + "s");
      c.style.setProperty("--delay", (-rr(0, 90)).toFixed(0) + "s");
      clouds.push(c);
    }
    const flash = document.createElement("img");
    flash.className = "bgflash"; flash.src = "assets/bg/sky.webp"; flash.alt = "";
    skyBox.appendChild(flash);
    const bolt = el("bgbolt", skyBox);
    bolt.innerHTML = BOLT;

    // ---- the skyline's few lit windows (one comes on at a time)
    const lights = S.lights.map(([x, y]) => {
      const l = el("bglight");
      Object.assign(l.style, { left: pct(x - .0022), top: pct(y - .0045), width: pct(.0044), height: pct(.009) });
      return l;
    });

    // ---- candle light pools, then the flames over the painted ones
    const pools = S.pools.map(([x, y, r]) => {
      const p = el("bgpool");
      Object.assign(p.style, { left: pct(x - r), top: pct(y - r / AR), width: pct(r * 2), height: pct(r * 2 / AR) });
      p.style.setProperty("--dur", rr(1.6, 2.6).toFixed(2) + "s");
      return p;
    });
    const flames = S.flames.map(([x, y, h]) => {
      const f = el("bgflame");
      const hh = h * 1.22, ww = hh * .46 * AR;
      Object.assign(f.style, { left: pct(x - ww / 2), top: pct(y - hh), width: pct(ww), height: pct(hh) });
      f.innerHTML = FLAME;
      f.style.setProperty("--dur", rr(.9, 1.5).toFixed(2) + "s");
      f.style.setProperty("--delay", (-rr(0, 2)).toFixed(2) + "s");
      return f;
    });

    // ---- the flashlight beam (a flat cone from the right edge)
    const beam = el("bgbeam");

    if (REDUCED) return;

    // lightning: a double flash of the sky, a bolt, the room blinks
    const strike = () => {
      const x = rr(8, 80);
      bolt.style.left = x.toFixed(1) + "%";
      bolt.style.transform = `scaleX(${rnd() < .5 ? -1 : 1})`;
      const seq = [[0, .95], [70, 0], [160, .7], [230, .15], [330, 0]];
      for (const [t, o] of seq) setTimeout(() => {
        flash.style.opacity = o; bolt.style.opacity = o > .5 ? 1 : 0; room.style.opacity = o * .55;
        room.style.background = "rgba(190, 215, 255, .22)";
      }, t);
      window.dispatchEvent(new CustomEvent("bgthunder"));
      later(rr(14000, 30000), strike);
    };
    later(rr(5000, 9000), strike);

    // the power sputters back on, in fits, and dies with a fizz
    const power = () => {
      const fits = [[0, 1], [110, 0], [190, .8], [300, 0], [380, 1], [900, .9], [960, 0], [1040, .5], [1110, 0]];
      for (const [t, o] of fits) setTimeout(() => {
        powerGlow.style.opacity = o; room.style.opacity = o; room.style.background = "rgba(255, 226, 150, .2)";
      }, t);
      window.dispatchEvent(new CustomEvent("bgpower"));
      later(rr(28000, 52000), power);
    };
    later(rr(16000, 24000), power);

    // a lit window somewhere in the city, now and then
    const blink = () => {
      const l = lights[Math.floor(rnd() * lights.length)];
      if (l) { l.classList.add("on"); later(rr(1800, 6000), () => l.classList.remove("on")); }
      later(rr(1500, 4500), blink);
    };
    later(1200, blink);

    // the flashlight sweep
    const sweep = () => {
      beam.classList.remove("go"); void beam.offsetWidth; beam.classList.add("go");
      later(rr(38000, 62000), sweep);
    };
    later(rr(9000, 15000), sweep);
  }
})();
