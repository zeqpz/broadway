# Broadway on Nashville - math model (broadway_5x5, 5x5 cluster + Encore)

5x5 board, cluster pays, tumbling reels, RTP 0.967 in every mode, max win 10,000x. A copy of Power
Outage's `outage_5x5` (2026-11-22): every mechanic, mode, price, the reel strips, the paytable and the
optimiser targets are Power Outage's. New: the **Encore** (below) and, to make room for it, leaner Gold
Record value tables in the two bonuses. The spec is `docs/BROADWAY.md`; the systems spec and the frontend
event contract are `DESIGN.md` at the project root (written for the old 7x7 board; the mechanics are
the same, and its "Encore" subsection covers the new one).

## Wins

A cluster is 5 or more of the same symbol connected side to side (no diagonals), anywhere on the board.
Every cluster on a board pays, by size tier (5 | 6 | 7-8 | 9-11 | 12-15 | 16+), then the winning symbols
leave and the refill is paid again. There are no paylines and no wild.

## Symbols

| id | symbol | role |
|----|--------|------|
| M  | Gold Record | the Multi (booster): lands with a value from 1.25x to 1000x, rolled on landing. Every cluster on the board is paid first; then it blows out - itself and the four cells sharing an edge with it are cleared in the same tumble as the paid cluster symbols, each of those five cells has the value ADDED to its own multiplier, and new symbols drop in. A cluster covering multiplied cells is multiplied by the SUM of the values on those cells. Scatters are immune. No pay of its own. |
| BS | FS (neon marquee star) | bonus scatter; 3/4/5 trigger 10/12/15 free spins |
| ES | XFS (jukebox) | extreme scatter; 2 = direct Xtreme Bonus (17 spins), 1 + a standard trigger = upgraded Xtreme |
| H1-H7 | The Crooner, The Bachelorette, The Fiddler, Mechanical Bull, Hot Chicken, Rhinestone Boot, Banjo | premiums |
| L1, L3, L4 | Lucky Horseshoe, Guitar Pick, Harmonica | lows (they carry the hit rate; the Encore's sources) |

## Wall events and line drops

* **Gold Records everywhere.** Three per reel on every strip (`BR0`/`BRE`/`FR0`/`FRE`); most land without a
  cluster under them (teasers), while the 500x and 1000x keep turning up in the base game (a 1000x is held
  to at most one base spin in 1,500 by `tools/finish_luts.py`).
* **Hit Parade** (Wall Line). On any reveal a straight run of 3 or 4 Gold Records can land along a row or
  down a column (`wall_line_chance`: 1 in 40 base spins, 1 in 6 free spins).
* **Sold-Out Show** (Full Wall). Every cell but a scatter becomes a Gold Record (`cover_mult_values`) and
  they all blow out together. Base game only, and only in the books of criteria `wallcover`, so the
  optimiser sets its frequency (about 1 in 40,000 spins).
* **Tips** (line drops). Every paid cluster leaves a small multiplier (x1.25/1.5/2) on one of its own cells
  per five symbols it held (`line_drop_values`).

## Encore

When a spin's cascade has ended on a board that pays nothing more and holds no Gold Record (not on the
wincap, not with the tumble budget spent), a roll can start an Encore:

* chance `encore_chance_base` 1/18 (base and Bonus Boost spins), `encore_chance_free` 1/6 (standard
  free spins), `encore_chance_extreme` 1/5 (Xtreme free spins);
* source: one of L1/L3/L4 with at least 3 copies on the board (`encore_min_copies`), picked in
  proportion to its count; target: a premium by `encore_target_weights` (H1 4, H2 8, H3 12, H4 14,
  H5 18, H6 20, H7 24 - H1 the rarest);
* every source cell turns into the target (scatters and Gold Records are never converted), the event
  `{"type": "encore", "from": src, "to": tgt, "positions": [{"reel", "row"}...]}` (rows +1 for the
  padding, like every positional event) is written after the cascade's closing `setWin`/`setTotalWin`,
  and the board goes through the cascade again - wins, Tips, Gold Records, tumbles - under its own budget
  (`encore_max_tumbles` 6), closed by a `setWin`/`setTotalWin` of its own;
* at most one per spin and per free spin. The spin's win runs on across both cascades
  (`updateTumbleWin` and the second `setWin` carry the spin's whole win, `setTotalWin` the round's), and
  the wincap stops everything as usual. Force-record key: `{"symbol": "encore", "kind": cells}`.

What a player sees (finished tables, every book weighted by its LUT weight - `analyze_books.py`):

| mode | Encore per base spin | per standard free spin | per Xtreme free spin | rounds with one | pays | sets off a Gold Record | direct RTP (share of the return) |
|---|---|---|---|---|---|---|---|
| base | 1 in 19.1 | 1 in 5.9 | 1 in 5.2 | 1 in 17.9 | 11.0% | 1.8% | 0.134 (13.9%) |
| bonus (100x) | 1 in 17.6 (the trigger spin) | 1 in 6.0 | - | 87% of buys (1.89 a buy) | 14.9% | 2.6% | 0.322 (33.3%) |
| extremebonus (400x) | 1 in 18.2 (the trigger spin) | - | 1 in 5.0 | 96% of buys (3.01 a buy) | 16.0% | 3.1% | 0.251 (26.0%) |
| boost (1.25x) | 1 in 19.6 | 1 in 5.9 | 1 in 5.0 | 1 in 17.7 | 8.5% | 1.5% | 0.162 (16.7%) |

"Pays" counts the Encores whose follow-up cascade pays anything; most turn a scattered low into premiums
that do not touch. A paying Encore averages ~20x in a base spin, ~115x in a standard free spin and ~210x
in an Xtreme one. The direct share is what the follow-up cascades pay; in a bonus the Tips and Gold Record
values they leave also lift the free spins after them.

In a bonus the Encore pays through the cell values the whole bonus has laid down, so on Power Outage's
bonus value tables it was worth about 0.4 of a bonus's price on top of the rest (the buy pools came to
~1.3 and ~1.4 of their price). The two bonus tables (`booster_mults_free` / `_extreme`) therefore lean
smaller: each weight is Power Outage's times `min(v, 20)^-a` (a = 0.4 standard, 0.5 Xtreme) - the small
values keep their odds, the middle leans most, the order of the values is unchanged and a 1000x is one
standard Gold Record in ~17,800 (was ~7,000). The buy pools then come out where Power Outage's did
(0.95 and 1.0 of the price before optimisation, 16,000 sims each). The base table is unchanged.

## Cell multipliers

The values a Gold Record leaves behind belong to the CELL, not the symbol on it (`grid_mults`), so they
survive every refill. In the base game they last for the rest of the spin. In a bonus they are wiped
once at bonus entry and then persist across every free spin of that bonus. Every value is a multiple of
0.25 and every pay a multiple of 0.4, so a cluster times any sum of values is exactly a whole tenth of
the bet - the RGS's granularity - with nothing rounded.

## Modes

* `base` (1x) - natural triggers
* `bonus` (100x) - buys the Standard Bonus
* `extremebonus` (400x) - buys the Xtreme Bonus
* `boost` (1.25x) - Bonus Boost: base spins with the bonus 1.6x as likely

## Free spins

A bonus plays exactly the spins its trigger awarded (no retriggers, no meter). Standard: `FR0`,
`booster_mults_free` (~2.5x a Gold Record). Xtreme: `FRE`, `booster_mults_extreme` (~4.0x, every value
2x or more). A Hit Parade on about one free spin in six, an Encore on one in six / one in five.

## Running

Python 3.12 (`C:\Users\CooperHinkel\Documents\ClaudeRoblox\smukiez-slot\.venv\Scripts\python.exe` on this
machine) with `PYTHONPATH` = `math-sdk`, run from this folder. The Rust optimiser builds with the
`stable-x86_64-pc-windows-gnu` toolchain, pinned to `optimization_program/` with a rustup override (no
MSVC linker here). At most 8 threads (Blender renders share the CPU); never two sims of this game at once.

```
python run.py --base 1000000 --bonus 100000 --extreme 100000 --boost 500000 --threads 8 --rust-threads 8 --optimize --checks
python ../../../tools/finish_luts.py library/publish_files          # after EVERY optimisation
python ../../../tools/shrink_books.py library/publish_files/books_base.jsonl.zst library/publish_files/books_bonus.jsonl.zst library/publish_files/books_extremebonus.jsonl.zst library/publish_files/books_boost.jsonl.zst
python ../../../tools/check_books.py library/publish_files/books_base.jsonl.zst --lut library/publish_files/lookUpTable_base_0.csv   # and each other mode
python verify_publish.py                                            # RGS checks on the final files, fresh sidecars
python analyze_books.py                                             # what a player sees, Encore included
python ../../../tools/gen_strips_js.py                              # the client's spin-through strips
```

The 2026-11-22 set (1,000,000 base / 100,000 bonus / 100,000 Xtreme / 500,000 boost books, the sizes of
Power Outage's published set): sims 38 minutes on 8 threads, optimisation 26 minutes, the finishing steps
about an hour. By the finished tables (`verify_publish.py`, `analyze_books.py`):

| mode | rtp | hit rate | std | cap | etl10k | most-drawn book |
|---|---|---|---|---|---|---|
| base | 0.966999992 | 1 in 2.47 | 11.1 | 1 in 5.0M | 0.002 | 1 in 587,000 |
| bonus | 0.9669999999 | every buy | 172 | 1 in 25,000 | 0.40 | 1 in 13,700 |
| extremebonus | 0.9669999999 | every buy | 446 | 1 in 13,900 | 0.72 | 1 in 8,800 |
| boost | 0.966999995 | 1 in 2.46 | 14.8 | 1 in 3.1M | 0.003 | 1 in 216,000 |

Base: a bonus 1 in 274 spins and an Xtreme 1 in 1,793 (upgraded Xtremes carry the `scatter` record and
are drawn in the freegame fence, as in Power Outage), the Sold-Out Show 1 in 40,000, a Hit Parade 1 in 44,
a 1000x Gold Record 1 in 2,057, a 100x+ win 1 in 645, 1000x+ 1 in 92,900. Boost: the bonus and the Xtreme
exactly 1.6x as often as base (1 in 171 / 1 in 1,127).

Books and lookup tables are written to `library/publish_files/` - what gets uploaded to engine.io. The
whole `library/` is gitignored (books over GitHub's limit; everything there is regenerated by the steps
above), so a simulation overwrites the last set on disk.

`run.py --checks` uses the verification sidecars the sims write (`library/configs/books_<mode>.verification.json`,
the SHA-256 of the books as simulated); `shrink_books.py` rewrites the books (same ids, payouts and event
order, compact `winInfo`), so the RGS checks must be re-run on the final files with `verify_publish.py`,
which reads every book, compares its payout with the table and writes fresh sidecars.

The optimiser weights payouts, not books: each payout's weight is split evenly over the books that pay it.
`game_optimization.base_book_scaling` therefore scales every payout of the base game's winning spins by
its book count and a target win profile (`BASE_TAIL`), read off the pool after the sims - which is why
`run.py` builds the optimisation setup after them. The bonus and Xtreme buy tables are weighted by payout.
`tools/finish_luts.py` holds a base 1000x Gold Record to one base spin in 1,500, keeps any one such board
rare, and brings each mode's exact RTP 1e-10 under 0.967 (the SDK's 3-star check is a strict float
`rtp > 0.967`). Its output says what it changed; a second run changes nothing.
