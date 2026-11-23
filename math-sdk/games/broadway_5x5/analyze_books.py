"""What a player sees, by the lookup tables: every book weighted by its LUT weight.

Reads library/publish_files (books_<mode>.jsonl.zst + lookUpTable_<mode>_0.csv, or the pair named
in index.json) and prints, per mode: RTP, hit rate, the most-drawn board, the feature frequencies
(bonus, Xtreme, Sold-Out Show, Hit Parade, 1000x walls, big wins, the cap) and the Encore:

* how often it comes - per base spin, per standard free spin, per Xtreme free spin, per round;
* how often it pays, and how often its follow-up cascade sets off a Gold Record (booster event);
* its RTP share: what the follow-up cascades pay (winInfo totalWin between an encore event and the
  setTotalWin that closes it), over the mode's whole return. That is the DIRECT share; in a bonus
  the Tips and Gold Record values those cascades leave also lift the free spins after them.

and a few book ids per Encore case for frontend tests (the most-drawn book of each case).

    python analyze_books.py [mode ...] [--dir library/publish_files] [--json out.json]
"""

import argparse
import io
import json
import os
from collections import defaultdict

import zstandard

HERE = os.path.dirname(os.path.abspath(__file__))


def read_books(path):
    with open(path, "rb") as fh:
        reader = zstandard.ZstdDecompressor().stream_reader(fh, read_across_frames=True)
        for line in io.TextIOWrapper(reader, encoding="utf-8"):
            if line.strip():
                yield json.loads(line)


def read_lut(path):
    weights = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                i, w, p = (int(x) for x in line.split(","))
                weights[i] = (w, p)
    return weights


def scan(book, wincap_cents):
    """Everything this script counts in one book."""
    s = {
        "base_spins": 0, "free_spins_std": 0, "free_spins_ext": 0,
        "enc_base": 0, "enc_std": 0, "enc_ext": 0,
        "enc_paid": 0, "enc_dead": 0, "enc_booster": 0, "enc_win": 0, "enc_cap": 0,
        "enc_base_paid": 0, "enc_base_booster": 0,
        "bonus": False, "extreme": False, "cover": False, "line_base": 0, "rare_wall": False,
        "only_base": True, "enc_list": [],
    }
    gametype, bonus_kind = "basegame", "standard"
    in_encore, enc_win, enc_boost, enc_rec = False, 0, False, None
    for ev in book["events"]:
        t = ev["type"]
        if t == "reveal":
            gametype = ev.get("gameType", gametype)
            if gametype == "basegame":
                s["base_spins"] += 1
            elif bonus_kind == "standard":
                s["free_spins_std"] += 1
            else:
                s["free_spins_ext"] += 1
        elif t == "enterBonus":
            s["only_base"] = False
            bonus_kind = "extreme" if ev.get("reason", "").startswith("extreme") else "standard"
            s["extreme" if bonus_kind == "extreme" else "bonus"] = True
        elif t == "wallDrop":
            if ev["kind"] == "cover":
                s["cover"] = True
            elif ev["kind"] == "line" and gametype == "basegame":
                s["line_base"] += 1
        elif t == "booster":
            if gametype == "basegame" and any(b["mult"] >= 1000 for b in ev["boosters"]):
                s["rare_wall"] = True
            if in_encore:
                enc_boost = True
        elif t == "encore":
            key = "enc_base" if gametype == "basegame" else ("enc_std" if bonus_kind == "standard" else "enc_ext")
            s[key] += 1
            in_encore, enc_win, enc_boost = True, 0, False
            enc_rec = {"gametype": gametype if gametype == "basegame" else bonus_kind, "from": ev["from"],
                       "to": ev["to"], "cells": len(ev["positions"]), "event": ev["index"]}
        elif t == "winInfo" and in_encore:
            enc_win += ev["totalWin"]
        elif t == "wincap" and in_encore:
            s["enc_cap"] += 1
        elif t == "setTotalWin" and in_encore:
            in_encore = False
            s["enc_win"] += enc_win
            s["enc_paid" if enc_win > 0 else "enc_dead"] += 1
            s["enc_booster"] += enc_boost
            if enc_rec["gametype"] == "basegame":
                s["enc_base_paid"] += enc_win > 0
                s["enc_base_booster"] += enc_boost
            enc_rec.update(win=enc_win, booster=enc_boost)
            s["enc_list"].append(enc_rec)
    s["enc_win"] = min(s["enc_win"], book["payoutMultiplier"], wincap_cents)
    return s


def analyze(mode, cost, books_path, lut_path, wincap=10000.0):
    lut = read_lut(lut_path)
    W = sum(w for w, _ in lut.values())
    acc = defaultdict(float)
    heaviest = (0, None)
    examples = defaultdict(list)   # case -> [(weight, id, detail)]
    n = 0
    for book in read_books(books_path):
        n += 1
        w, p = lut[book["id"]]
        assert p == book["payoutMultiplier"], f"LUT/book payout mismatch at {book['id']}"
        s = scan(book, int(wincap * 100))
        acc["rtp"] += w * p
        acc["hit"] += w * (p > 0)
        acc["p100"] += w * (p >= 100 * 100)
        acc["p1000"] += w * (p >= 1000 * 100)
        acc["cap"] += w * (p >= wincap * 100)
        for k in ("base_spins", "free_spins_std", "free_spins_ext", "enc_base", "enc_std", "enc_ext", "enc_paid",
                  "enc_dead", "enc_booster", "enc_win", "enc_cap", "enc_base_paid", "enc_base_booster", "line_base"):
            acc[k] += w * s[k]
        for k in ("bonus", "extreme", "cover", "rare_wall"):
            acc[k] += w * s[k]
        acc["rounds_with_encore"] += w * bool(s["enc_list"])
        if w > heaviest[0]:
            heaviest = (w, book["id"])
        for e in s["enc_list"]:
            if e["gametype"] == "basegame" and s["only_base"]:
                if e["win"] > 0 and not e["booster"]:
                    examples["base encore that pays"].append((w, book["id"], e, p))
                if e["win"] >= 2000:
                    examples["base encore that pays 20x+"].append((w, book["id"], e, p))
                if e["win"] == 0 and p == 0:
                    examples["base encore that pays nothing (round pays 0)"].append((w, book["id"], e, p))
                if e["booster"] and e["win"] > 0:
                    examples["base encore -> Gold Record blow-out"].append((w, book["id"], e, p))
            elif e["gametype"] == "standard" and e["win"] > 0:
                examples["bonus (standard free spin) encore that pays"].append((w, book["id"], e, p))
            elif e["gametype"] == "extreme" and e["win"] > 0:
                examples["xtreme free spin encore that pays"].append((w, book["id"], e, p))
    one_in = lambda x: f"1 in {W / x:,.1f}" if x else "never"
    per = lambda a, b: f"1 in {b / a:,.2f}" if a else "never"
    print(f"\n[{mode}] cost {cost:g}x, {n:,} books, weight {W:,}")
    print(f"  rtp {acc['rtp'] / W / 100 / cost:.10f}   hit rate {one_in(acc['hit'])}   "
          f"most-drawn book {heaviest[1]} ({one_in(heaviest[0])})")
    print(f"  bonus {one_in(acc['bonus'])}   xtreme {one_in(acc['extreme'])}   sold-out show {one_in(acc['cover'])}   "
          f"base hit parade {one_in(acc['line_base'])}   base 1000x record {one_in(acc['rare_wall'])}")
    print(f"  wins >=100x {one_in(acc['p100'])}   >=1000x {one_in(acc['p1000'])}   cap {one_in(acc['cap'])}")
    total_enc = acc["enc_base"] + acc["enc_std"] + acc["enc_ext"]
    print(f"  ENCORE  per base spin {per(acc['enc_base'], acc['base_spins'])}   "
          f"per standard free spin {per(acc['enc_std'], acc['free_spins_std'])}   "
          f"per xtreme free spin {per(acc['enc_ext'], acc['free_spins_ext'])}")
    print(f"          rounds with one or more {one_in(acc['rounds_with_encore'])}   encores per round {total_enc / W:.4f}")
    if total_enc:
        print(f"          pays {acc['enc_paid'] / total_enc:.1%}   pays nothing {acc['enc_dead'] / total_enc:.1%}   "
              f"sets off a Gold Record {acc['enc_booster'] / total_enc:.1%}   reaches the cap {acc['enc_cap'] / total_enc:.3%}")
        if acc["enc_base"]:
            print(f"          base encores: pay {acc['enc_base_paid'] / acc['enc_base']:.1%}, "
                  f"Gold Record {acc['enc_base_booster'] / acc['enc_base']:.1%}")
        print(f"          direct RTP {acc['enc_win'] / W / 100 / cost:.5f} = {acc['enc_win'] / acc['rtp']:.1%} of the mode's return"
              f"   (mean follow-up win {acc['enc_win'] / max(acc['enc_paid'], 1) / 100:.2f}x a paying encore)")
    out = {}
    for case, rows in sorted(examples.items()):
        rows.sort(key=lambda r: -r[0])
        out[case] = [{"id": i, "weight_1_in": round(W / w) if w else None, "payout": p / 100, **e}
                     for w, i, e, p in rows[:4]]
        print(f"  e.g. {case}:")
        for r in out[case]:
            print(f"      id {r['id']:>7}  payout {r['payout']:>8g}x  encore at event {r['event']}: {r['from']}->{r['to']} "
                  f"x{r['cells']} cells, follow-up {r['win'] / 100:g}x{' + Gold Record' if r['booster'] else ''}"
                  f"  (drawn {('1 in %s' % format(r['weight_1_in'], ',')) if r['weight_1_in'] else 'never'})")
    return {"mode": mode, "weight": W, "acc": dict(acc), "examples": out}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("modes", nargs="*")
    ap.add_argument("--dir", default=os.path.join(HERE, "library", "publish_files"))
    ap.add_argument("--json", help="also write the numbers and examples here")
    a = ap.parse_args()
    index = json.load(open(os.path.join(a.dir, "index.json"), encoding="utf-8"))
    results = []
    for m in index["modes"]:
        if a.modes and m["name"] not in a.modes:
            continue
        results.append(analyze(m["name"], float(m["cost"]), os.path.join(a.dir, m["events"]),
                               os.path.join(a.dir, m["weights"])))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=1)


if __name__ == "__main__":
    main()
