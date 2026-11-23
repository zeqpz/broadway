"""The Broadway on Nashville sound pass (2026-11-22), end to end, on the street pass's own tools
(a copy of outage.py reading broadway_spec.py, plus a `review` step).

  python tools/sfx/broadway.py gen    [name ...]  # Seed Audio takes -> %TEMP%/broadway_sfx/raw/<name>_<t>.pcm (resumable)
  python tools/sfx/broadway.py cand   [name ...]  # every take cleaned whole and cut into events (process2) -> cand/
  python tools/sfx/broadway.py pick   [name ...]  # best + most alike `keep` per sound (pick_takes' scoring) -> picks.json
  python tools/sfx/broadway.py build  [name ...]  # clean3's strict clean + master from the raw take -> frontend/assets
  python tools/sfx/broadway.py review [name ...]  # spectrogram sheets of what build wrote + silence / click checks
  python tools/sfx/broadway.py derive [name ...]  # re-edits of takes (broadway_spec.DERIVE) -> raw/<name>_101.. .pcm
  python tools/sfx/broadway.py cands  name ...    # a sound's best 9 candidates on one sheet (to fix a bad take)
  python tools/sfx/broadway.py all    [name ...]  # gen, derive, cand, pick, build, review

A take heard wrong in review (a voice, a click, a gap, the wrong sound) goes in broadway_spec.REJECT and the sound is
built again: pick and build skip it.

The prompts and where each sound goes are in broadway_spec.py. The work files stay in %TEMP%/broadway_sfx
(rebuildable; old_assets/ holds the Power Outage files as they were). build writes the WAVs into frontend/assets and
the list of them to %TEMP%/broadway_sfx/written.txt; then the two loops (reels, coin rain) by hand from their raw takes:
  python tools/sfx/broadway_textures.py
and the Opus copies:
  node tools/sfx/encode_new.js <ClaudeRoblox>/.tools/pw/node_modules/playwright %TEMP%/broadway_sfx/written.txt
The HUD buttons' files (broadway_spec.HUD_FILES) are never written by this pass.
"""
import os, sys, json, glob, shutil, itertools, time, urllib.error, concurrent.futures as cf
import numpy as np
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import orapi, broadway_spec as FS
import process2 as P
import clean3 as C
from audiolib import write_wav, read_wav, lufs, analyze, noise_floor
from pick_takes import penalty

ROOT = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.path.join(ROOT, "frontend", "assets")
W = os.path.join(os.environ.get("TEMP", "/tmp"), "broadway_sfx")
RAW, CAND = os.path.join(W, "raw"), os.path.join(W, "cand")
SR0, SR = 24000, 44100
LOOSE_BED = -42           # see build(): the second round for textured sounds

# the street tools read their tables from module globals: hand them the fall sounds
P.K["sting"] = dict(P.K["tone"], gap=.6, hp=70, fout=200, exp=-56, tail=-56)
C.HP["sting"] = 70
for name, (_, _, kind, t, _) in FS.S.items():
    P.T[name] = t
    C.KIND[name] = kind
P.FOUT.update(FS.FOUT)
C.TONAL |= FS.TONAL
P.RAW = RAW


# ------------------------------------------------------------------ generate
def speech(prompt):
    last = None
    for a in range(4):                 # Seed Audio turns ~1% of requests away with a 400 at random: ask again
        try:
            return orapi.speech(prompt, fmt="pcm")
        except RuntimeError as e:
            last = e
            time.sleep(2 + 3 * a)
    raise last


def gen_one(name, prompt, take):
    out = os.path.join(RAW, f"{name}_{take}.pcm")
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        return name, take, "kept", 0
    try:
        b, ct = speech(prompt)
    except Exception as e:
        return name, take, f"ERR {str(e)[:160]}", 0
    if "rate=24000" not in ct or "channels=2" not in ct:
        return name, take, f"ERR content type {ct}", 0
    open(out + ".part", "wb").write(b)
    os.replace(out + ".part", out)
    return name, take, f"{len(b) / 4 / SR0:.2f}s", len(b) / 4 / SR0


def gen(names):
    os.makedirs(RAW, exist_ok=True)
    work = [(n, p, t) for n, p, takes, _ in FS.jobs() if n in names for t in range(1, takes + 1)
            if not os.path.exists(os.path.join(RAW, f"{n}_{t}.pcm"))]
    c0 = orapi.credits()
    print(f"{len(work)} takes; credits {c0:.4f}", flush=True)
    secs = errs = 0
    with cf.ThreadPoolExecutor(6) as ex:
        for i, (n, t, r, d) in enumerate(ex.map(lambda w: gen_one(*w), work)):
            secs += d
            errs += r.startswith("ERR")
            if r.startswith("ERR"):
                print(f"[{i + 1}/{len(work)}] {n}_{t}: {r}", flush=True)
    c1 = orapi.credits()
    print(f"{errs} errors, {secs:.1f}s of audio (~${secs / 60 * .15:.3f} at $0.15/min); credits {c1:.4f} "
          f"(account moved {c0 - c1:.4f} meanwhile, other work included)", flush=True)


# ------------------------------------------------------------------ candidates (process2.main, per fall sound)
def cand(names):
    path = os.path.join(W, "cand.json")
    db = json.load(open(path)) if os.path.exists(path) else {}
    for name, prompt, takes, kind in FS.jobs():
        if name not in names:
            continue
        kd = dict(P.K[kind])
        mn, mx, keep, mode = P.T[name]
        mode = mode or kd["mode"]
        d = os.path.join(CAND, name)
        shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
        db[name] = []
        raws = sorted(glob.glob(os.path.join(RAW, f"{name}_*.pcm")), key=lambda p: int(p.rsplit("_", 1)[1][:-4]))
        for p in raws:
            t = int(p.rsplit("_", 1)[1][:-4])
            st = np.frombuffer(open(p, "rb").read(), "<i2").reshape(-1, 2).astype(np.float64) / 32768
            if len(st) < 2048 or np.abs(st).max() < 1e-3:
                continue
            st = st - st.mean(0)
            nf_raw = noise_floor(st, SR0) - 20 * np.log10(np.abs(st).max())
            st = signal.sosfiltfilt(signal.butter(4, kd["hp"], "highpass", fs=SR0, output="sos"), st, axis=0)
            g, Nn, Gg = P.gate(st, *kd["gate"])
            cal = (np.abs(P.stft(np.random.default_rng(0).standard_normal(SR0))) ** 2).mean(1).sum()
            m = g.mean(1)
            if mode == "hit":
                evs = P.ev_hits(m, mn, mx, kd["tail"], single=kind in ("click", "drop") or name in FS.SINGLE)
            elif mode == "gesture":
                evs = P.ev_gesture(m, kd.get("gap", .15), kd["tail"], mx)
            else:
                evs = P.ev_sustain(m, mx)
            evs = [e for e in evs if e["pk"] > -14][:24]
            for i, ev in enumerate(evs):
                seg = g[ev["a"]:ev["b"]]
                raw_len = len(seg) / SR0
                if raw_len < mn * .8:
                    continue
                y = P.finish(seg, kd, mx, kind, name)
                if len(y) < int(mn * .8 * SR):
                    continue
                a = analyze(y, SR)
                f0, f1 = ev["a"] // P.HOP, max(ev["a"] // P.HOP + 1, min(Gg.shape[1], ev["b"] // P.HOP))
                pk_in = np.abs(seg.mean(1)).max() + 1e-12
                hiss_raw = 10 * np.log10(Nn.sum() / cal + 1e-20) - 20 * np.log10(pk_in)
                hiss = 10 * np.log10((Nn[:, None] * Gg[:, f0:f1] ** 2).sum(0).mean() / cal + 1e-20) - 20 * np.log10(pk_in)
                fn = f"{t}_{i}.wav"
                write_wav(os.path.join(d, fn), y, SR)
                db[name].append(dict(file=fn, take=t, ev=i, a=int(ev["a"]), b=int(ev["b"]), dur=a["dur"], peak=a["peak_db"],
                                     mmax=lufs(y, SR)[1], I=a["lufs"], cen=a["centroid"], nf_raw=nf_raw,
                                     nf_out=noise_floor(y, SR), ev_pk=ev["pk"], cut=bool(ev["cut"] or raw_len > mx),
                                     raw_len=raw_len, hiss_raw=hiss_raw, hiss=hiss, bands=P.bands(y)))
        print(f"{name:16s} {len(raws)} takes -> {len(db[name])} candidates", flush=True)
    json.dump(db, open(path, "w"), indent=0)


# ------------------------------------------------------------------ pick (pick_takes' scoring, no review sheets)
def pick(names):
    db = json.load(open(os.path.join(W, "cand.json")))
    path = os.path.join(W, "picks.json")
    picks = json.load(open(path)) if os.path.exists(path) else {}
    for name in names:
        bad = set(FS.REJECT.get(name, ()))
        cs = [c for c in db.get(name) or [] if c["file"] not in bad and c["take"] not in bad]
        if not cs:
            print(f"{name:16s} NO CANDIDATES"); continue
        mn, mx, keep, _ = P.T[name]
        for c in cs:
            c["pen"] = penalty(c, mn, mx)
        cs.sort(key=lambda c: c["pen"])
        if name in FS.MANUAL:
            picks[name] = FS.MANUAL[name]
            print(f"{name:16s} keep {picks[name]} (by hand)"); continue
        top = cs[:max(keep, min(9 if keep > 3 else 8, len(cs)))]
        best, bestv = None, 1e9
        for combo in itertools.combinations(range(len(top)), min(keep, len(top))):
            B = [np.array(top[i]["bands"]) for i in combo]
            dist = np.mean([np.abs(a - b).mean() for a, b in itertools.combinations(B, 2)]) if len(B) > 1 else 0
            same = len(combo) - len({top[i]["take"] for i in combo})      # a little variety: takes, not one take's echoes
            v = dist * 2 + np.mean([top[i]["pen"] for i in combo]) + 1.5 * same
            if v < bestv:
                best, bestv = combo, v
        picks[name] = [top[i]["file"] for i in best]
        print(f"{name:16s} keep {picks[name]}  " + "  ".join(f"{top[i]['dur']:.2f}s pen{top[i]['pen']:.1f}" for i in best))
    json.dump(db, open(os.path.join(W, "cand.json"), "w"), indent=0)
    json.dump(picks, open(path, "w"), indent=1)


def wsola(x, rate, sr, frame=.04, tol=.012):
    """Time-compress by `rate` keeping the pitch: waveform-similarity overlap-add (Hann frames, 50 %
    overlap out, each next frame taken where it best continues the last one within +-tol)."""
    N = int(frame * sr) // 2 * 2; Ho = N // 2; Hi = Ho * rate; T = int(tol * sr)
    win = np.hanning(N)[:, None]
    n_out = int((len(x) - N - T) / Hi)
    out = np.zeros((n_out * Ho + N, x.shape[1])); norm = np.zeros(n_out * Ho + N)
    pos = 0
    for k in range(n_out):
        c = int(round(k * Hi))
        if k:
            want = x[pos + Ho:pos + Ho + N].mean(1)            # what would naturally follow the last frame
            lo, hi = max(0, c - T), min(len(x) - N, c + T)
            seg = x[lo:hi + N].mean(1)
            cc = signal.correlate(seg, want, mode="valid")
            c = lo + int(np.argmax(cc))
        out[k * Ho:k * Ho + N] += x[c:c + N] * win
        norm[k * Ho:k * Ho + N] += win[:, 0]
        pos = c
    return out / np.maximum(norm, 1e-3)[:, None]


# ------------------------------------------------------------------ build (clean3) -> frontend/assets
def build(names):
    db = json.load(open(os.path.join(W, "cand.json")))
    picks = json.load(open(os.path.join(W, "picks.json")))
    written = []
    wl = os.path.join(W, "written.txt")
    if os.path.exists(wl):
        written = [l.strip() for l in open(wl) if l.strip()]
    bp = os.path.join(W, "built.json")
    built = json.load(open(bp)) if os.path.exists(bp) else {}
    for name in names:
        _, _, kind, (mn, mx, keep, _), out = FS.S[name]
        tgt = out[2]
        fns = [f"sfx_{out[1]}_{i}.wav" for i in range(1, keep + 1)] if out[0] == "set" else out[1]
        bad = set(FS.REJECT.get(name, ()))             # takes heard wrong in review (a voice, a click, a gap)
        ranked = sorted([c for c in db[name] if c["file"] not in bad and c["take"] not in bad], key=lambda c: c.get("pen", 99))
        want = [c for c in ranked if c["file"] in picks[name]]
        if name in FS.MANUAL:                          # picked by hand from the sheets: those or nothing
            ranked = want
        res = []
        # Voodoo pass: a textured sound (a bead shower, a rattle, a shimmer) IS noise, so its "bed" is the sound;
        # when no take meets the strict bed, a second round takes the cleanest ones up to LOOSE_BED (the gate still
        # leaves exact digital zero outside the sound). A cut that comes back empty is skipped, not fatal.
        for limit in (FS.BED.get(name, C.BED_MAX), LOOSE_BED):
            for c in want + [c for c in ranked if c not in want]:
                if len(res) == len(fns):
                    break
                if any(r[0] is c for r in res):
                    continue
                y = None
                bed, info = 0.0, {"guard": {"ok": False}}
                for j, (prop, ns) in enumerate(((1.0, True), (1.0, False), (.85, False), (.6, False), (0.0, False))):
                    try:
                        yy, info = C.build_one(name, c, tgt, prop=prop, nonstat=ns)
                    except ValueError:
                        break
                    bed = info["n_after"] + info["gain"]
                    if info["guard"]["ok"] and bed <= limit and len(yy) >= int(max(.012, mn * .6) * SR):
                        y = yy; info["pass"] = j; break
                if y is None:
                    print(f"  {name} {c['file']}: rejected at {limit} (bed {bed:.1f}, guard {info['guard']['ok']})")
                    continue
                res.append((c, y, info))
            if len(res) == len(fns):
                break
        for fn, (c, y, info) in zip(fns, res):
            if name in FS.STRETCH:
                y = wsola(y, FS.STRETCH[name], SR)
                _, M = lufs(y, SR)                      # back to the loudness target, never over -1.5 dBFS
                y *= 10 ** (min(tgt - M, -1.5 - 20 * np.log10(np.abs(y).max() + 1e-12)) / 20)
                n = int(.06 * SR)
                y[-n:] *= (.5 + .5 * np.cos(np.linspace(0, np.pi, n)))[:, None]
                y[0] = 0; y[-1] = 0
            if fn in FS.HUD_FILES:                      # the HUD keeps the base build's files (owner)
                raise SystemExit(f"{name} would overwrite the HUD file {fn}")
            write_wav(os.path.join(ASSETS, fn), y, SR)
            built[fn] = dict(name=name, cand=c["file"], take=c["take"], pass_=info["pass"])
            if fn not in written:
                written.append(fn)
            I, M = lufs(y, SR)
            g = info["guard"]
            print(f"{fn:28s} {name}:{c['file']:7s} dur {len(y) / SR:5.2f}s pk {20 * np.log10(np.abs(y).max() + 1e-12):5.1f} "
                  f"M {M:6.1f} I {I:6.1f} bed {info['n_after'] + info['gain']:6.1f} pass {info['pass']} "
                  f"guard lvl {g['dlvl']:+.1f} cen {g['dcen'] * 100:+.0f}%", flush=True)
        if len(res) < len(fns):
            print(f"  !! {name}: {len(res)} of {len(fns)} files")
    open(wl, "w").write("\n".join(written) + "\n")
    json.dump(built, open(bp, "w"), indent=1)


# ------------------------------------------------------------------ review: sheets + automatic checks
def checks(y, sr):
    """what a listen catches first: a late start, a gap in the middle, a click, a hard edge, clipping"""
    pk = np.abs(y).max() + 1e-12
    n5 = int(.005 * sr)
    e = np.sqrt(np.convolve(y.mean(1) ** 2, np.ones(n5) / n5, "same")) / pk
    db = 20 * np.log10(e + 1e-9)
    live = np.nonzero(db > -40)[0]
    lead = live[0] / sr if len(live) else len(y) / sr
    gap, run = 0.0, 0                                  # longest stretch under -60 dB between the first and last sound
    for v in (db[live[0]:live[-1]] if len(live) else []):
        run = run + 1 if v < -60 else 0
        gap = max(gap, run / sr)
    d = np.diff(y.mean(1))                             # a click: one sample step far over the local slope
    loc = np.sqrt(np.convolve(d ** 2, np.ones(441) / 441, "same")) + 1e-4
    click = float((np.abs(d) / loc).max())
    flags = []
    if lead > .03: flags.append(f"starts {lead * 1000:.0f} ms late")
    if gap > .15: flags.append(f"gap {gap * 1000:.0f} ms")
    if click > 25: flags.append(f"click x{click:.0f}")
    if np.abs(y[0]).max() > 1e-3 or np.abs(y[-1]).max() > 1e-3: flags.append("hard edge")
    if pk > .99: flags.append("clips")
    return dict(dur=len(y) / sr, pk=float(20 * np.log10(pk)), lead=float(lead), gap=float(gap), click=click, flags=flags)


def review(names):
    """one sheet per 8 sounds (%TEMP%/broadway_sfx/sheets/review_NN.png): each written file's spectrogram (50 Hz - 16 kHz, log)
    with its waveform, titled with the candidate it came from and any flag from checks()"""
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    built = json.load(open(os.path.join(W, "built.json")))
    sheets = os.path.join(W, "sheets"); os.makedirs(sheets, exist_ok=True)
    rows = [(n, sorted(fn for fn, b in built.items() if b["name"] == n)) for n in names]
    rows += [(t, [fn]) for t, n, fn in (("tex", "n_reels", "sfx_reels.wav"), ("tex", "n_rain", "sfx_coins_rain.wav"))
             if n in names and os.path.exists(os.path.join(ASSETS, fn))]
    rows = [r for r in rows if r[1]]
    per, report = 8, {}
    for page in range(0, len(rows), per):
        chunk = rows[page:page + per]
        cols = max(len(f) for _, f in chunk)
        fig, axes = plt.subplots(len(chunk), cols, figsize=(3.2 * cols + .4, 1.7 * len(chunk)), squeeze=False)
        for ax in axes.flat:
            ax.axis("off")
        for r, (name, fns) in enumerate(chunk):
            for k, fn in enumerate(fns):
                y, sr, _ = read_wav(os.path.join(ASSETS, fn))
                ck = checks(y, sr); report[fn] = ck
                ax = axes[r, k]; ax.axis("on")
                mm = y.mean(1)
                nper = 2048 if len(mm) > sr * .6 else 512 if len(mm) > sr * .3 else 256
                f, t, Sg = signal.spectrogram(mm, sr, nperseg=nper, noverlap=nper * 7 // 8)
                ax.pcolormesh(t, f / 1000, 10 * np.log10(Sg + 1e-14), vmin=-120, vmax=-30, cmap="magma", shading="auto")
                ax.set_yscale("log"); ax.set_ylim(.05, 16)        # kHz, log: slides and harmonics show
                ax2 = ax.twinx(); ax2.plot(np.arange(len(mm)) / sr, mm, color="cyan", lw=.3, alpha=.7)
                ax2.set_ylim(-1, 1); ax2.axis("off")
                b = built.get(fn, {})
                ax.set_title(f"{fn[4:-4]} [{name}:{b.get('cand', 'loop')}] {ck['dur']:.2f}s pk{ck['pk']:.1f}"
                             + (" ! " + ", ".join(ck["flags"]) if ck["flags"] else ""), fontsize=6,
                             color="red" if ck["flags"] else "black")
                ax.tick_params(labelsize=4)
        fig.tight_layout()
        out = os.path.join(sheets, f"review_{page // per + 1:02d}.png")
        fig.savefig(out, dpi=100); plt.close(fig)
        print("sheet", out)
    for fn, ck in report.items():
        print(f"  {fn:28s} {ck['dur']:5.2f}s pk {ck['pk']:5.1f} click x{ck['click']:4.0f}  " + ", ".join(ck["flags"]))
    rp = os.path.join(W, "review.json")
    old = json.load(open(rp)) if os.path.exists(rp) else {}
    old.update(report)
    json.dump(old, open(rp, "w"), indent=1)


def cands(names):
    """for fixing a bad take: a sheet of a sound's best 9 candidates (by pick penalty), the built ones in green,
    the rejected in red -> %TEMP%/broadway_sfx/sheets/cand_<name>.png"""
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    db = json.load(open(os.path.join(W, "cand.json")))
    built = json.load(open(os.path.join(W, "built.json")))
    for name in names:
        cs = sorted(db.get(name) or [], key=lambda c: c.get("pen", 99))[:9]
        used = {b["cand"] for b in built.values() if b["name"] == name}
        bad = set(FS.REJECT.get(name, ()))
        fig, axes = plt.subplots(3, 3, figsize=(10, 5.4), squeeze=False)
        for ax in axes.flat:
            ax.axis("off")
        for ax, c in zip(axes.flat, cs):
            ax.axis("on")
            y, sr, _ = read_wav(os.path.join(CAND, name, c["file"]))
            mm = y.mean(1)
            nper = 2048 if len(mm) > sr * .6 else 512 if len(mm) > sr * .3 else 256
            f, t, Sg = signal.spectrogram(mm, sr, nperseg=nper, noverlap=nper * 7 // 8)
            ax.pcolormesh(t, f / 1000, 10 * np.log10(Sg + 1e-14), vmin=-120, vmax=-30, cmap="magma", shading="auto")
            ax.set_yscale("log"); ax.set_ylim(.05, 16)        # kHz, log: slides and harmonics show
            ax2 = ax.twinx(); ax2.plot(np.arange(len(mm)) / sr, mm, color="cyan", lw=.3, alpha=.7)
            ax2.set_ylim(-1, 1); ax2.axis("off")
            col = "red" if (c["file"] in bad or c["take"] in bad) else "green" if c["file"] in used else "black"
            ax.set_title(f"{c['file']} {c['dur']:.2f}s pen{c.get('pen', 0):.1f}{' CUT' if c['cut'] else ''}", fontsize=7, color=col)
            ax.tick_params(labelsize=5)
        fig.suptitle(name, fontsize=8); fig.tight_layout()
        out = os.path.join(W, "sheets", f"cand_{name}.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        fig.savefig(out, dpi=90); plt.close(fig)
        print("sheet", out)


# ------------------------------------------------------------------ derive: re-edits of the takes (broadway_spec.DERIVE)
def raw_take(name, take):
    return np.frombuffer(open(os.path.join(RAW, f"{name}_{take}.pcm"), "rb").read(), "<i2").reshape(-1, 2).astype(np.float64) / 32768


def tapestop(x, out_s, hold_s, power, sr=SR0):
    """play x at full speed for hold_s, then slow it to a stop over the rest of out_s (speed (1 - u) ** power)"""
    n, h = int(out_s * sr), int(hold_s * sr)
    u = np.clip((np.arange(n) - h) / max(1, n - h), 0, 1)
    pos = np.concatenate([[0.0], np.cumsum((1 - u) ** power)[:-1]])
    if pos[-1] > len(x) - 2:
        raise ValueError(f"tapestop needs {pos[-1] / sr:.2f}s of source, has {len(x) / sr:.2f}s")
    return np.stack([np.interp(pos, np.arange(len(x)), x[:, c]) for c in range(x.shape[1])], 1)


def derive(names):
    xf = int(.012 * SR0)
    for name in names:
        for i, d in enumerate(FS.DERIVE.get(name, ())):
            parts = []
            for src, take, t0, t1, rate in d["segs"]:
                seg = raw_take(src, take)[int(t0 * SR0):int(t1 * SR0)]
                seg = seg - seg.mean(0)
                if rate != 1:
                    h = int(.04 * SR0) // 2               # wsola's first and last half frame are under-windowed
                    seg = wsola(seg, rate, SR0)[h:-h]       # (divided by a small norm): a spike at the end
                parts.append(seg)
            y = parts[0]
            for p in parts[1:]:                       # equal-power crossfade into the next part
                k = min(xf, len(y), len(p))
                a = np.cos(np.linspace(0, np.pi / 2, k))[:, None]
                y = np.vstack([y[:-k], y[-k:] * a + p[:k] * np.sqrt(1 - a ** 2), p[k:]])
            if d.get("fx") and d["fx"][0] == "tapestop":
                y = tapestop(y, *d["fx"][1:])
            # either side, 0.4 s of the source take's own bed (its quietest 0.25 s that is not the generator's digital
            # silence), as a real take has: clean3 reads its noise profile from there and gates to exact zero after
            s0 = raw_take(*d["segs"][0][:2])
            wl = int(.25 * SR0)
            cs = np.concatenate([[0], np.cumsum(np.square(s0).mean(1))])
            st0 = np.arange(int(.1 * SR0), max(int(.1 * SR0) + 1, len(s0) - wl - int(.1 * SR0)), wl // 5)
            lv = 10 * np.log10((cs[st0 + wl] - cs[st0]) / wl + 1e-30)
            ok = lv > -92
            if ok.any() and lv[ok].min() < -70:
                bed = s0[st0[ok][np.argmin(lv[ok])]:][:wl]
                bed = bed - bed.mean(0)
            else:                                     # music from end to end: no quiet to borrow, so a faint
                bed = np.random.default_rng(101 + i).standard_normal((wl, 2)) * 10 ** (-84 / 20)   # -84 dBFS hush
            pad = np.vstack([bed, bed[::-1]])[:int(.4 * SR0)]   # mirrored, so no seam in the middle
            k1, k2 = int(.004 * SR0), int(.02 * SR0)           # in fast (keep the attack), out slower
            y = y.copy()
            y[:k1] *= np.linspace(0, 1, k1)[:, None]; y[-k2:] *= np.linspace(1, 0, k2)[:, None]
            y = np.vstack([pad[:-k1], pad[-k1:] + y[:k1], y[k1:-k2], y[-k2:] + pad[:k2], pad[k2:]])
            y *= min(1.0, .89 / (np.abs(y).max() + 1e-9))
            out = os.path.join(RAW, f"{name}_{101 + i}.pcm")
            open(out, "wb").write((np.clip(y, -1, 1) * 32767).round().astype("<i2").tobytes())
            src = " + ".join(f"{s}_{t}[{a}-{b}s]" + (f"/{r}" if r != 1 else "") for s, t, a, b, r in d["segs"])
            print(f"{name}_{101 + i}: {len(y) / SR0:.2f}s from {src}" + (f" -> {d['fx'][0]}" if d.get("fx") else ""))


def main():
    step, names = sys.argv[1], [a for a in sys.argv[2:]] or list(FS.S)
    for s in (("gen", "derive", "cand", "pick", "build", "review") if step == "all" else (step,)):
        globals()[s](names)


if __name__ == "__main__":
    main()
