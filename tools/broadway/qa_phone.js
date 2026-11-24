// The phone tier's rules, checked (iOS crash at load, 2026-11-20). An iPhone runs the game inside the casino's iframe
// and Safari kills the page when it outgrows its memory ("A problem repeatedly occurred"); the sister games' fixes
// (fallslotsga 9c3ac82, orleans db24101 ...) keep a phone to: the board's own canvases only, no CSS filters or blend
// modes, no 3D transforms / will-change, nothing animating at idle but the bonus emblem's drift, and only its own
// tier's art fetched. Owner passes 2 - 5 were checked on desktop only and broke four of those; this is the gate.
// Headless Chromium as an iPhone 12 (390x664 Safari viewport @3, iOS UA), live game on the mock RGS (8822):
// features screen -> board -> one spin.   usage: node tools/broadway/qa_phone.js   (exit code 1 on a failure)
const path = require("path");
const { chromium } = require(path.join(__dirname, "..", "..", "..", ".tools", "pw", "node_modules", "playwright"));
const BASE = process.env.BASE || "http://localhost:8822";
const UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Mobile/15E148 Safari/604.1";
const DESKTOP_ONLY = /assets\/(bonus_wall(_xtreme)?\.webp|logo_sign|bg\/|chars\/|spark\.json)/;
const CANVAS_OK = /^(boardgl|candleflame|shardlayer)$/;          // the board, the (unshown) flame, the burst layer
let fails = 0;
const say = (ok, msg) => { if (!ok) fails++; console.log((ok ? "PASS " : "FAIL ") + msg); };
(async () => {
  const b = await chromium.launch();
  for (const [name, w, h] of [["portrait", 390, 664], ["landscape", 750, 342]]) {
    const c = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 3, isMobile: true, hasTouch: true, userAgent: UA });
    const p = await c.newPage();
    const errs = [], fetched = [];
    p.on("pageerror", e => errs.push(e.message));
    p.on("console", m => { if (m.type() === "error") errs.push(m.text()); });
    p.on("request", r => fetched.push(r.url()));
    await p.goto(`${BASE}/index.html?sessionID=test&rgs_url=${BASE}&lang=en&device=mobile`);
    await p.waitForTimeout(9000);
    const census = () => p.evaluate(() => {
      const name = el => el.id ? "#" + el.id : el.tagName.toLowerCase() + "." + String(el.className).split(" ").slice(0, 2).join(".");
      const cv = [...document.querySelectorAll("canvas")].map(c => ({ id: c.id || c.className || "?", mb: c.width * c.height * 4 / 1e6 }));
      const filt = [], blend = [], t3d = [];
      for (const el of document.querySelectorAll("*")) {
        if (!el.getClientRects().length) continue;
        const s = getComputedStyle(el);
        if (s.filter !== "none") filt.push(name(el));
        if (s.mixBlendMode !== "normal") blend.push(name(el));
        if (/matrix3d|perspective/.test(s.transform) || s.willChange !== "auto") t3d.push(name(el));
      }
      const an = [];
      for (const a of document.getAnimations()) if (a.playState === "running" && a.effect && a.effect.target) an.push(name(a.effect.target) + ":" + (a.animationName || a.transitionProperty || "?"));
      return { mob: document.documentElement.classList.contains("mob"), cv, filt, blend, t3d, an };
    });
    await p.touchscreen.tap(w / 2, h * .7); await p.waitForTimeout(3000);
    await p.touchscreen.tap(w / 2, h * .7); await p.waitForTimeout(3500);
    const idle = await census();
    say(idle.mob, `${name}: the phone tier is on (html.mob)`);
    const extra = idle.cv.filter(x => !CANVAS_OK.test(x.id));
    say(!extra.length, `${name}: no canvases beside the board's (${extra.map(x => x.id + " " + x.mb.toFixed(1) + " MB").join(", ") || "none"})`);
    say(idle.cv.reduce((s, x) => s + x.mb, 0) <= 8, `${name}: canvases in the page ${idle.cv.reduce((s, x) => s + x.mb, 0).toFixed(1)} MB (<= 8)`);
    say(!idle.filt.length, `${name}: no CSS filters at idle (${idle.filt.slice(0, 4).join(", ") || "none"})`);
    say(!idle.blend.length, `${name}: no blend modes at idle (${idle.blend.slice(0, 4).join(", ") || "none"})`);
    say(!idle.t3d.length, `${name}: no 3D transforms / will-change at idle (${idle.t3d.slice(0, 4).join(", ") || "none"})`);
    const idleAn = idle.an;
    say(!idleAn.length, `${name}: nothing animating at idle (${idleAn.slice(0, 4).join(", ") || "none"})`);
    // Broadway: no character anywhere (owner, 2026-11-24); the title sign is one still picture (portrait only)
    say(await p.evaluate(() => !document.querySelector("#rosiephone, #charfx canvas")) && !fetched.some(u => /rosie|charrig|assets\/chars\//i.test(u)),
      `${name}: no character (no element, nothing of hers fetched)`);
    say(await p.evaluate(o => { const r = document.querySelector("#phonesign"); if (!r || r.tagName !== "IMG") return false;
      const shown = getComputedStyle(r).display !== "none"; return o === "portrait" ? shown : !shown; }, name),
      `${name}: the title sign is a still picture (${name === "portrait" ? "over the board" : "hidden"})`);
    await p.evaluate(() => { const s = document.getElementById("spinBtn"); if (s) s.click(); });
    await p.waitForTimeout(2200);
    const spin = await census();
    // (the win figure's popup carries will-change while it is up: the base build's own, in orleans' phone tier too)
    const hot = [...spin.filt, ...spin.blend, ...spin.t3d].filter(n => !/winpop/.test(n));
    say(!hot.length, `${name}: no filters, blends or 3D while a spin plays (${hot.slice(0, 4).join(", ") || "none"})`);
    await p.waitForTimeout(6000);
    const bad = [...new Set(fetched.filter(u => DESKTOP_ONLY.test(u)).map(u => u.split("/assets/")[1]))];
    say(!bad.length, `${name}: no desktop-only art fetched (${bad.join(", ") || "none"})`);
    say(!errs.length, `${name}: no page errors ${errs.slice(0, 2).join(" | ")}`);
    await c.close();
  }
  await b.close();
  console.log(fails ? fails + " FAILED" : "ALL PASS");
  process.exit(fails ? 1 : 0);
})().catch(e => { console.log("FAIL", e.message); process.exit(1); });
