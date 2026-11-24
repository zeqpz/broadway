// Film a Bet Replay round: screenshots every `step` ms while it plays, plus any page errors, into %TEMP%/broadway_qa/win_<event>/.
// usage: node tools/broadway/qa_win.js [event=954] [step=220] [seconds=16]   (mock RGS on 8822)
const path = require("path"), fs = require("fs");
const { chromium } = require(path.join(__dirname, "..", "..", "..", ".tools", "pw", "node_modules", "playwright"));
const [ev = "954", step = "220", secs = "16"] = process.argv.slice(2);
const OUT = path.join(require("os").tmpdir(), "broadway_qa", "win_" + ev) + "/";
fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const b = await chromium.launch({ channel: "chrome", args: ["--autoplay-policy=no-user-gesture-required"] });
  const p = await b.newPage({ viewport: { width: 1600, height: 900 } });
  const errs = [];
  p.on("pageerror", e => errs.push("pageerror " + e.message));
  p.on("console", m => { if (m.type() === "error") errs.push("console " + m.text()); });
  p.on("response", r => { if (r.status() >= 400) errs.push(r.status() + " " + r.url()); });
  await p.goto(`http://localhost:8822/index.html?replay=true&game=smukiez&version=1&mode=${process.env.MODE || "base"}&event=${ev}&amount=1&currency=USD&rgs_url=http://localhost:8822&lang=en&device=desktop`);
  await p.waitForTimeout(5000);
  await p.click("#replayPlay").catch(e => errs.push("play " + e.message));
  const t0 = Date.now();
  let n = 0;
  while (Date.now() - t0 < +secs * 1000) {
    await p.screenshot({ path: OUT + String(n++).padStart(3, "0") + ".png" });
    // CLICK=1: press through the screens that wait for a click (the bonus intro, the total)
    if (process.env.CLICK && n % 4 === 0) await p.evaluate(() => {
      const w = document.querySelector(".bonusintro, .bonusend, .totalwin");
      if (w) w.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    }).catch(() => {});
    await p.waitForTimeout(+step);
  }
  console.log("frames", n, errs.length ? errs.slice(0, 12) : "no errors");
  await b.close();
})().catch(e => console.log("FAIL", e.message));
