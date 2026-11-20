// The live game in a real WebKit engine (Playwright's WebKit for Windows) as an iPhone 12: crash / page errors, and the
// WebKit processes' private memory through load -> features -> board -> spins.   node wk.js <base> <out.json> [spins] [extra query] [land]
const { webkit, devices } = require(require("path").join(__dirname, "..", "..", "..", "..", ".tools", "pw", "node_modules", "playwright"));
const { spawn } = require("child_process"), fs = require("fs");
const [base, out, spins = "2", extra = "", land = ""] = process.argv.slice(2);
(async () => {
  const b = await webkit.launch();
  const dev = devices[land ? "iPhone 12 landscape" : "iPhone 12"];
  const c = await b.newContext({ ...dev });
  const p = await c.newPage();
  const errs = [], marks = [], samples = [];
  let crashed = false, phase = "load", navs = 0;
  p.on("crash", () => { crashed = true; marks.push(["CRASH", Date.now()]); });
  p.on("pageerror", e => errs.push("pageerror " + String(e.message).slice(0, 240)));
  p.on("console", m => { if (m.type() === "error") errs.push("console " + m.text().slice(0, 200)); });
  p.on("framenavigated", f => { if (f === p.mainFrame()) navs++; });
  // one PowerShell process sampling the WebKit processes every 200 ms: name, private bytes
  const ps = spawn("powershell", ["-NoProfile", "-Command",
    "while ($true) { $o = Get-Process | Where-Object { $_.ProcessName -match 'WebKit|Playwright' } | ForEach-Object { $_.ProcessName + ':' + $_.PrivateMemorySize64 }; Write-Output ($o -join ','); Start-Sleep -Milliseconds 200 }"]);
  ps.stdout.on("data", d => { for (const line of String(d).split(/\r?\n/)) { if (!line.trim()) continue; const m = {}; for (const kv of line.split(",")) { const [n, v] = kv.split(":"); m[n] = (m[n] || 0) + (+v || 0); } samples.push({ t: Date.now(), phase, m }); } });
  const t0 = Date.now();
  await p.goto(`${base}/index.html?sessionID=test&rgs_url=${base}&lang=en&device=mobile${extra}`, { waitUntil: "commit" });
  const mark = n => { phase = n; marks.push([n, Date.now() - t0]); };
  await p.waitForTimeout(11000);
  const info = () => p.evaluate(() => { const cv = [...document.querySelectorAll("canvas")]; const app = document.getElementById("app"), acs = getComputedStyle(app); return { mob: document.documentElement.className, zoom: acs.zoom, appStyle: app.style.cssText.slice(0, 160), appTransform: acs.transform.slice(0, 50), fit: getComputedStyle(document.documentElement).getPropertyValue("--fit"), appBox: [app.offsetWidth, app.offsetHeight, Math.round(app.getBoundingClientRect().width)], inner: [innerWidth, innerHeight], canvases: cv.length, canvasMB: +(cv.reduce((s, c) => s + c.width * c.height * 4, 0) / 1e6).toFixed(1), big: cv.map(c => [c.className || c.id, c.width, c.height]).sort((a, b) => b[1] * b[2] - a[1] * a[2]).slice(0, 4), features: !!document.querySelector(".features, #features"), playing: typeof state !== "undefined" ? state.playing : null }; }).catch(e => ({ err: String(e.message).slice(0, 120) }));
  const res = { base, dev: land ? "iPhone 12 landscape" : "iPhone 12", atLoad: await info() };
  mark("features");
  const vp = p.viewportSize();
  await p.touchscreen.tap(vp.width / 2, vp.height * .6); await p.waitForTimeout(3500);
  await p.touchscreen.tap(vp.width / 2, vp.height * .6); await p.waitForTimeout(4000);
  mark("board"); res.atBoard = await info();
  await p.screenshot({ path: out.replace(/\.json$/, "_board.png") }).catch(() => {});
  for (let i = 0; i < +spins && !crashed; i++) {
    mark("spin" + (i + 1));
    await p.evaluate(() => { const s = document.getElementById("spinBtn"); if (s && !s.disabled) s.click(); }).catch(() => {});
    await p.waitForTimeout(7000);
  }
  mark("after"); await p.waitForTimeout(3000);
  res.atEnd = await info();
  ps.kill();
  const names = new Set(); for (const s of samples) for (const n in s.m) names.add(n);
  const by = {};
  for (const s of samples) { const web = Object.entries(s.m).filter(([n]) => /WebProcess|WebContent/i.test(n)).reduce((a, [, v]) => a + v, 0), all = Object.values(s.m).reduce((a, v) => a + v, 0); const q = by[s.phase] || (by[s.phase] = { web: 0, all: 0 }); q.web = Math.max(q.web, web); q.all = Math.max(q.all, all); }
  for (const k in by) { by[k].web = Math.round(by[k].web / 1e6); by[k].all = Math.round(by[k].all / 1e6); }
  Object.assign(res, { crashed, navigations: navs, errs: errs.slice(0, 20), procs: [...names], peakMB: by });
  fs.writeFileSync(out, JSON.stringify(res, null, 1));
  console.log(JSON.stringify(res));
  await b.close();
})().catch(e => { console.log("FAIL", e.message); process.exit(1); });
