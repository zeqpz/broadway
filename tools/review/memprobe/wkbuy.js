// a live bonus buy on the phone profile: what is shown / made at the shop, the intro and through the round
const { chromium, webkit, devices } = require(require("path").join(__dirname, "..", "..", "..", "..", ".tools", "pw", "node_modules", "playwright"));
const base = process.argv[2] || "http://localhost:8788", which = +(process.argv[3] || 0), secs = +(process.argv[4] || 40);
const UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Mobile/15E148 Safari/604.1";
(async () => {
  const b = await webkit.launch(); let crashed = false;
  const c = await b.newContext({ ...devices["iPhone 12"] });
  const p = await c.newPage();
  const errs = [], net = []; p.on("crash", () => { crashed = true; console.log("*** PAGE CRASHED"); }); p.on("framenavigated", f => { if (f === p.mainFrame()) console.log("nav", f.url().slice(0, 60)); });
  p.on("pageerror", e => errs.push("pageerror " + e.message.slice(0, 200)));
  p.on("console", m => { if (m.type() === "error") errs.push("console " + m.text().slice(0, 160)); });
  p.on("request", r => net.push(r.url().replace(base, "").split("?")[0]));
  await p.goto(`${base}/index.html?sessionID=wk${Date.now()}&rgs_url=${base}&lang=en&device=mobile`);
  await p.waitForTimeout(9000);
  await p.touchscreen.tap(195, 460); await p.waitForTimeout(3000);
  await p.touchscreen.tap(195, 460); await p.waitForTimeout(3500);
  const census = tag => p.evaluate(async tag => {
    const name = el => (el.id ? "#" + el.id : el.tagName.toLowerCase() + "." + String(el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className).split(" ").slice(0, 2).join("."));
    const cv = [...document.querySelectorAll("canvas")].map(c => [c.id || c.className || "?", c.width, c.height, +(c.width * c.height * 4 / 1e6).toFixed(1)]).sort((a, b) => b[3] - a[3]);
    const pics = new Map(), filt = [], blend = [], t3d = [], big = [];
    const zoom = +getComputedStyle(document.getElementById("app")).zoom || 1;
    const size = u => new Promise(res => { const i = new Image(); i.onload = () => res(i.naturalWidth * i.naturalHeight * 4 / 1e6); i.onerror = () => res(0); i.src = u; });
    for (const el of document.querySelectorAll("*")) {
      if (!el.getClientRects().length) continue;
      const s = getComputedStyle(el);
      if (el.tagName === "IMG" && el.currentSrc) pics.set(el.currentSrc, name(el));
      for (const prop of [s.backgroundImage, s.maskImage || s.webkitMaskImage || ""]) for (const m of String(prop).matchAll(/url\("?([^")]+)"?\)/g)) pics.set(m[1], name(el));
      if (s.filter !== "none") filt.push(name(el) + " " + s.filter.slice(0, 40));
      if (s.mixBlendMode !== "normal") blend.push(name(el));
      if (/matrix3d|perspective/.test(s.transform) || s.willChange !== "auto" || s.perspective !== "none") t3d.push(name(el));
    }
    let picMB = 0; const plist = [];
    for (const [u, n] of pics) { if (u.startsWith("data:")) continue; const mb = await size(u); picMB += mb; plist.push([+mb.toFixed(1), u.split("/assets/")[1] || u.slice(-40), n]); }
    plist.sort((a, b) => b[0] - a[0]);
    const an = {}; let layerMB = 0;
    for (const a of document.getAnimations()) { if (a.playState !== "running" || !a.effect || !a.effect.target) continue; const t = a.effect.target; if (!t.getClientRects || !t.getClientRects().length) continue; const k = name(t) + ":" + (a.animationName || a.transitionProperty || "?"); if (!an[k]) { an[k] = 1; const w = t.offsetWidth * zoom * 3, h = t.offsetHeight * zoom * 3; layerMB += w * h * 4 / 1e6; big.push([+(w * h * 4 / 1e6).toFixed(1), k]); } }
    big.sort((a, b) => b[0] - a[0]);
    return { tag, canvases: cv.length, canvasMB: +cv.reduce((s, c) => s + c[3], 0).toFixed(1), cvTop: cv.slice(0, 5), picMB: +picMB.toFixed(1), picTop: plist.slice(0, 9), filt: filt.slice(0, 8), blend: blend.slice(0, 6), t3d: t3d.slice(0, 8), anims: Object.keys(an).length, animLayerMB: +layerMB.toFixed(1), animTop: big.slice(0, 8), nodes: document.querySelectorAll("*").length,
      heapMB: performance.memory ? +(performance.memory.usedJSHeapSize / 1e6).toFixed(1) : 0 };
  }, tag);
  const show = r => console.log(r.tag, "cv", r.canvases, r.canvasMB, JSON.stringify((r.cvTop||[]).slice(0,3)), "pics", r.picMB, JSON.stringify((r.picTop||[]).slice(0,4)), "anims", r.anims, r.animLayerMB, JSON.stringify((r.animTop||[]).slice(0,5)), "filt", JSON.stringify(r.filt), "blend", JSON.stringify(r.blend), "3d", JSON.stringify(r.t3d), "nodes", r.nodes, r.err||"");
  show(await census("board"));
  await p.evaluate(() => document.getElementById("bonusBtn").click()); await p.waitForTimeout(2500);
  show(await census("shop"));
  const btns = await p.evaluate(() => [...document.querySelectorAll("#bonusWrap button, #bonusWrap [role=button]")].filter(b => b.getClientRects().length).map(b => (b.id || b.className) + " | " + b.textContent.trim().slice(0, 30)));
  console.log("shop buttons:", JSON.stringify(btns));
  const clicked = await p.evaluate(which => { const gos = [...document.querySelectorAll("#bonusWrap .bsget")].filter(b => b.getClientRects().length && !b.disabled); const g = gos[which]; if (g) { g.click(); return g.className + " | " + g.textContent.trim(); } return null; }, which);
  console.log("clicked:", clicked);
  await p.waitForTimeout(1500);
  const conf = await p.evaluate(() => { const c = [...document.querySelectorAll("button")].filter(b => b.getClientRects().length && /confirm|yes|buy|play/i.test(b.textContent) && b.closest("#bonusWrap, #autoPop, .confirm, [role=dialog]")); const g = c[c.length - 1]; if (g) { g.click(); return g.id + " " + g.className + " | " + g.textContent.trim(); } return null; });
  console.log("confirm:", conf);
  const t0 = Date.now(); let n = 0, peak = {};
  while (Date.now() - t0 < secs * 1000) {
    await p.waitForTimeout(1500);
    const r = await census("t" + Math.round((Date.now() - t0) / 1000)).catch(e => ({ err: e.message.slice(0, 80) }));
    if ((r.animLayerMB || 0) > 6) console.log("ANIM", r.tag, r.animLayerMB, JSON.stringify(r.animTop));
    if (n++ % 3 === 0 || (r.canvasMB || 0) > (peak.canvasMB || 0) + 3 || (r.picMB || 0) > (peak.picMB || 0) + 3) show(r);
    for (const k of ["canvasMB", "picMB", "animLayerMB", "canvases", "anims", "nodes", "heapMB"]) peak[k] = Math.max(peak[k] || 0, r[k] || 0);
    await p.evaluate(() => { const w = document.querySelector(".bonusintro, .bonusend, .totalwin"); if (w) w.dispatchEvent(new MouseEvent("click", { bubbles: true })); }).catch(() => {});
  }
  console.log("PEAK", JSON.stringify(peak));
  console.log("errors", JSON.stringify(errs.slice(0, 8)));
  console.log("big fetched:", JSON.stringify([...new Set(net)].filter(u => /bonus_wall|banner|logo_sign|\/bg\//.test(u))));
  await b.close();
})().catch(e => console.log("FAIL", e.message));
