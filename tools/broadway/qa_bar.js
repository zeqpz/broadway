// The bar scene's live details, checked in real Chrome (the browser pane is throttled): the features screen (the whole
// room in view), then the board, shot twice 700 ms apart so what moves shows (fans, bulbs, dust, steam, jukebox);
// prints which animated pieces exist and any page error. -> %TEMP%/broadway_qa/bar_*.png
// usage: node tools/broadway/qa_bar.js [WxH=1920x1080]
const path = require("path");
const { chromium } = require(path.join(__dirname, "..", "..", "..", ".tools", "pw", "node_modules", "playwright"));
const OUT = path.join(require("os").tmpdir(), "broadway_qa") + "/";
require("fs").mkdirSync(OUT, { recursive: true });
const [W, H] = (process.argv[2] || "1920x1080").split("x").map(Number);
(async () => {
  const b = await chromium.launch({ channel: "chrome" }).catch(() => chromium.launch());
  const p = await b.newPage({ viewport: { width: W, height: H } });
  const errs = [];
  p.on("pageerror", e => errs.push(e.message));
  p.on("response", r => { if (r.status() >= 400) errs.push(r.status() + " " + r.url()); });
  await p.goto("http://localhost:8822/index.html?sessionID=bar" + Date.now() + "&rgs_url=http://localhost:8822&lang=en&device=desktop", { waitUntil: "domcontentloaded", timeout: 120000 });
  await p.waitForTimeout(9500);
  await p.screenshot({ path: OUT + `bar_features_${W}.png` });
  await p.mouse.click(W / 2, H - 30);
  await p.waitForTimeout(4500);
  await p.screenshot({ path: OUT + `bar_a_${W}.png` });
  await p.waitForTimeout(700);
  await p.screenshot({ path: OUT + `bar_b_${W}.png` });
  const parts = await p.evaluate(() => {
    const n = s => document.querySelectorAll("#bgscene " + s).length;
    const run = s => [...document.querySelectorAll("#bgscene " + s)].filter(e => e.getAnimations().some(a => a.playState === "running")).length;
    return { signs: n(".bgoff:not(.bulb)"), bulbGroups: n(".bgoff.bulb"), fans: n(".bgfan"), fansTurning: run(".bgfan .bgf-spin"), motes: n(".bgmote"),
             motesMoving: run(".bgmote"), glints: n(".bgglint"), steam: n(".bgsteam"), juke: n(".bgjuke"), jukeCycling: run(".bgjuke"),
             records: n(".bgrec"), beams: n(".bgbeam"), footGroups: (document.querySelectorAll("#bgscene .bgoff.bulb").length) };
  });
  console.log(JSON.stringify(parts));
  // how much of ten seconds each neon sign spends dark (a sign must flicker, never stay off)
  const dark = await p.evaluate(async () => {
    const els = [...document.querySelectorAll("#bgscene .bgoff:not(.bulb)")], n = els.map(() => 0);
    for (let k = 0; k < 100; k++) { els.forEach((e, i) => { if (getComputedStyle(e).opacity === "1") n[i]++; }); await new Promise(r => setTimeout(r, 100)); }
    return n.map(v => v + "%");
  });
  console.log("signs dark:", dark.join(" "));
  console.log(errs.length ? errs : "no errors");
  await b.close();
})();
