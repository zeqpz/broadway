// Owner pass 4 QA (mock RGS on 8788): the board's size, the bar's figures never overlapping at any amount, the bonus
// emblem clear of the bar, the cord's stability under resizes / knocks / a wild throw, and the spark FX.
// usage: node tools/outage/qa_pass4.js   -> prints PASS/FAIL lines, screenshots in %TEMP%/outage_qa/p4_*.png
const path = require("path"), fs = require("fs");
const { chromium } = require(path.join(__dirname, "..", "..", "..", ".tools", "pw", "node_modules", "playwright"));
const OUT = path.join(require("os").tmpdir(), "outage_qa") + "/";
fs.mkdirSync(OUT, { recursive: true });
const URL = (id, mob) => `http://localhost:8788/index.html?sessionID=${id}&rgs_url=http://localhost:8788&lang=en&device=${mob ? "mobile&mobile=1" : "desktop"}`;
const SIZES = [["d1920", 1920, 1080, false], ["d1366", 1366, 768, false], ["d1280x1024", 1280, 1024, false], ["d800", 800, 600, false],
               ["phone", 390, 844, true], ["phoneL", 844, 390, true]];
let fails = 0;
const say = (ok, msg) => { if (!ok) fails++; console.log((ok ? "PASS " : "FAIL ") + msg); };
(async () => {
  const b = await chromium.launch();
  for (const [name, w, h, mob] of SIZES) {
    const c = await b.newContext(Object.assign({ viewport: { width: w, height: h } }, mob ? { deviceScaleFactor: 2, isMobile: true, hasTouch: true } : {}));
    const p = await c.newPage();
    const errs = [];
    p.on("pageerror", e => errs.push(e.message));
    p.on("response", r => { if (r.status() >= 400) errs.push(r.status() + " " + r.url().split("/").pop()); });
    await p.goto(URL("p4" + name, mob));
    await p.waitForSelector(".features .fbox", { timeout: 90000 });
    await p.waitForTimeout(900);
    await p.mouse.click(w / 2, h - 30);
    await p.waitForTimeout(3200);
    const L = await p.evaluate(() => {
      const R = s => { const e = typeof s === "string" ? document.querySelector(s) : s; if (!e) return null; const q = e.getBoundingClientRect(); return { x: q.x, y: q.y, w: q.width, h: q.height, r: q.right, b: q.bottom }; };
      return { board: R("#board"), frame: R("#paintframe"), hud: R(".hudframe"), bonus: R("#bonusBtn"), sign: R("#logosign"), lever: R("#leverbox"), vw: innerWidth, vh: innerHeight };
    });
    say(true, `${name}: board ${Math.round(L.board.w)}x${Math.round(L.board.h)} = ${(L.board.h / L.vh * 100).toFixed(1)}% of the height, ${(L.board.w / L.vw * 100).toFixed(1)}% of the width`);
    const inter = (a, c2) => a && c2 && a.x < c2.r - 2 && a.r > c2.x + 2 && a.y < c2.b - 2 && a.b > c2.y + 2;
    say(!inter(L.bonus, L.hud), `${name}: bonus emblem clear of the bar`);
    say(L.bonus.x >= -1 && L.bonus.b <= L.vh + 1, `${name}: bonus emblem on screen (${Math.round(L.bonus.x)},${Math.round(L.bonus.y)} ${Math.round(L.bonus.w)}px)`);
    say(L.lever.r <= L.vw + 1, `${name}: breaker on screen (right edge ${Math.round(L.lever.r)} of ${L.vw})`);
    say(L.board.b <= L.hud.y + 2, `${name}: board above the bar (${Math.round(L.board.b)} vs ${Math.round(L.hud.y)})`);
    // the bar's figures at growing amounts
    const amounts = [["0.00", "1,000,000.00", "1.00"], ["12,345.67", "999,999,935.20", "1,000.00"], ["1,234,567.89", "9,999,999,999.99", "10,000.00"],
                     ["123,456,789,012.34", "123,456,789,012,345.67", "1,000,000.00"]];
    let worst = "";
    for (const [win, bal, bet] of amounts) {
      const r = await p.evaluate(([win, bal, bet]) => {
        const cur = document.getElementById("balance").textContent.replace(/[\d.,\s]/g, "") || "$";
        document.getElementById("winStat").classList.remove("zero");
        document.getElementById("roundWin").textContent = cur + win; document.getElementById("balance").textContent = cur + bal; document.getElementById("betVal").textContent = cur + bet;
        return new Promise(res => requestAnimationFrame(() => requestAnimationFrame(() => {
          const q = id => { const e = document.getElementById(id), r = e.getBoundingClientRect(), s = e.closest(".hudstat").getBoundingClientRect(); return { x: r.x, r: r.right, sx: s.x, sr: s.right, fs: parseFloat(getComputedStyle(e).fontSize), sw: e.scrollWidth, cw: e.clientWidth }; };
          const a = q("balance"), b2 = q("roundWin"), c2 = q("betVal"), bar = document.querySelector(".hudbar").getBoundingClientRect();
          res({ a, b: b2, c: c2, barx: bar.x, barr: bar.right });
        })));
      }, [win, bal, bet]);
      const ok = r.a.r <= r.b.sx + .5 && r.b.x >= r.b.sx - .5 && r.b.r <= r.b.sr + .5 && r.b.r <= r.c.x + .5 && r.a.x >= r.barx - .5 && r.c.r <= r.barr + .5 &&
                 r.a.sw <= r.a.cw + 1 && r.b.sw <= r.b.cw + 1 && r.c.sw <= r.c.cw + 1;
      if (!ok) worst = `win ${win}: balance ${r.a.x.toFixed(0)}-${r.a.r.toFixed(0)} | win ${r.b.x.toFixed(0)}-${r.b.r.toFixed(0)} in slot ${r.b.sx.toFixed(0)}-${r.b.sr.toFixed(0)} | bet ${r.c.x.toFixed(0)}-${r.c.r.toFixed(0)} (bar ${r.barx.toFixed(0)}-${r.barr.toFixed(0)})`;
      if (win === "1,234,567.89") await p.screenshot({ path: OUT + `p4_hud_${name}.png`, clip: { x: Math.max(0, L.hud.x - 10), y: Math.max(0, L.hud.y - 10), width: Math.min(w, L.hud.w + 20), height: Math.min(h - Math.max(0, L.hud.y - 10), L.hud.h + 20) } });
    }
    say(!worst, `${name}: bar figures stay in their slots at every amount ${worst}`);
    await p.evaluate(() => { document.getElementById("roundWin").textContent = "$0.00"; document.getElementById("balance").textContent = "$1,000,000.00"; document.getElementById("betVal").textContent = "$1.00"; document.getElementById("winStat").classList.add("zero"); });
    await p.waitForTimeout(200);
    await p.screenshot({ path: OUT + `p4_${name}.png` });
    if (name === "d1920") {
      // the spark: fire one and catch it
      const clip = { x: L.frame.x + L.frame.w * .6, y: Math.max(0, L.frame.y - 60), width: Math.min(w - (L.frame.x + L.frame.w * .6), L.frame.w * .6), height: L.frame.h * .5 };
      for (let i = 0; i < 6; i++) {
        if (i === 0 || i === 3) await p.evaluate(() => window.__spark && window.__spark(1));
        await p.waitForTimeout(i % 3 === 0 ? 30 : 110);
        await p.screenshot({ path: OUT + `p4_spark_${i}.png`, clip });
      }
      say(await p.evaluate(() => typeof window.__spark === "function"), "spark FX loaded");
      // the cord: resizes, a wild throw, then it must hang near rest
      const plug = () => p.evaluate(() => { const g = document.querySelector(".cablegrab").getBoundingClientRect(), f = document.getElementById("cablebox").getBoundingClientRect(); return [(g.x + g.width / 2 - f.x) / f.width, (g.y + g.height / 2 - f.y) / f.height]; });
      await p.waitForTimeout(1500);
      const rest = await plug();
      for (const [vw, vh] of [[1280, 720], [900, 900], [1920, 1080], [1000, 600], [1920, 1080]]) { await p.setViewportSize({ width: vw, height: vh }); await p.waitForTimeout(350); }
      let far = 0;
      for (let i = 0; i < 12; i++) { const q = await plug(); far = Math.max(far, Math.hypot(q[0] - rest[0], q[1] - rest[1])); await p.waitForTimeout(120); }
      say(far < .12, `cord through 5 resizes: plug strayed at most ${(far * 100).toFixed(1)}% of the frame's width from rest`);
      const g = await p.evaluate(() => { const r = document.querySelector(".cablegrab").getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; });
      await p.mouse.move(g[0], g[1]); await p.mouse.down();
      for (const [dx, dy] of [[-400, -300], [200, -500], [-600, 100], [250, 60], [-300, -600]]) { await p.mouse.move(g[0] + dx, g[1] + dy, { steps: 3 }); await p.waitForTimeout(60); }
      await p.mouse.up();
      let maxFar = 0;
      for (let i = 0; i < 10; i++) { const q = await plug(); maxFar = Math.max(maxFar, Math.hypot(q[0] - rest[0], q[1] - rest[1])); await p.waitForTimeout(100); if (i === 2) await p.screenshot({ path: OUT + "p4_cord_thrown.png", clip: { x: L.frame.x + L.frame.w * .55, y: L.frame.y + L.frame.h * .45, width: L.frame.w * .6, height: Math.min(h - (L.frame.y + L.frame.h * .45), L.frame.h * .7) } }); }
      await p.waitForTimeout(3500);
      const end = await plug(), off = Math.hypot(end[0] - rest[0], end[1] - rest[1]);
      say(maxFar < .45, `cord thrown wildly: stayed within ${(maxFar * 100).toFixed(1)}% of the frame's width of rest`);
      say(off < .03, `cord back at rest after the throw (off by ${(off * 100).toFixed(2)}%)`);
    }
    say(!errs.length, `${name}: no page errors ${errs.slice(0, 4).join(" | ")}`);
    await c.close();
  }
  console.log(fails ? `${fails} FAILED` : "ALL PASS");
  await b.close();
})().catch(e => { console.log("FAIL", e.message); process.exit(1); });
