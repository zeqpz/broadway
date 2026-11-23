# Sound effects pipeline (2026-11-03 pass)

## Broadway on Nashville pass (2026-11-22)

Every game sound re-made as Lower Broadway honky-tonk (guitar strums and twangs, pedal steel, banjo, fiddle, boot
stomps and spurs, saloon doors, a record scratch for the Gold Record, neon buzz, marquee-bulb clicks, a bull snort, a
fryer, a jukebox, fireworks for the Xtreme stage, country stings), in the same slots and file names as Power Outage's
`outage_spec.py`, plus four new files for Encore. Seed Audio through OpenRouter, ~310 takes (~22 min of audio, about
$3.40). Nothing speaks or sings and no tune is a real song's.

- `broadway_spec.py` - the prompts, kinds, caps and outputs (the shape of `outage_spec.py`), and at its end what the
  review caught: `DERIVE` (re-edits of takes), `REJECT`, `MANUAL`, `STRETCH`, `HUD_FILES`.
- `broadway.py` - a copy of `outage.py` reading it: `gen` -> `derive` -> `cand` -> `pick` -> `build` -> `review`
  (`all` runs them in order; `cands <name>` puts a sound's best 9 candidates on one sheet). `build` refuses to write a
  HUD file; `review` draws `%TEMP%/broadway_sfx/sheets/review_NN.png` (log-frequency spectrogram + waveform of every
  written file, with flags for a late start, a gap, a click, a hard edge or clipping).
- `broadway_textures.py` - the two loops cut by hand from their raw takes (reels: the even washboard scrape, take 4;
  coin rain: the continuous shower, take 2), then `encode_new.js` on `%TEMP%/broadway_sfx/written.txt`.
- Work files in `%TEMP%/broadway_sfx/` (raw takes, candidates, picks, `built.json`, sheets, and `old_assets/` = the
  Power Outage `sfx_*` files as they were).

What was made: 103 files replaced in place (51 sets) + `sfx_encore_riff` (a ~1.5 s chicken-picking lick ending on a
ringing note), `sfx_spotlight` (a heavy switch clunk + lamp hum), `sfx_flip` (one bright guitar twang), and
`sfx_crowd_cheer` (a small-hall crowd cheering and whistling, no words), each `.wav` + `.ogg`. The Encore four are not
in `index.html`'s `SFX` table yet. Landing foley follows the same `LAND_FOLEY` keys: H1 Crooner's mic, H2 Bachelorette's
hat, H3 fiddle, H4 bull snort, H5 fryer sizzle, H6 boot + spur, H7 banjo, L1 horseshoe, L3 guitar pick, L4 harmonica,
M a record dropped on a turntable.

Not touched, byte for byte as the base build: the HUD buttons (`sfx_ui_click_1-3`, `ui_hover_1-2`, `slider_tick_1-2`,
`swish_in_1-2`, `swish_out_1-2`, `menu_open`, `menu_close`, `toggle`, `auto_start`, `auto_stop`, `bet`, `skip`,
`hover_loop`), the SMUKIEZ ident (`intro_*`, `land_brick_*`; BROADWAY.md keeps that introduction as it is), and the
Voodoo leftovers nothing plays (Doc's `cane_tap`, `magic_poof`, `hat_swish`, `cane_spin`; `land_beads`,
`land_doubloon`, `land_tarot`).

What the review sheets caught, and the fixes:
- Seed Audio answers a musical or slowly changing prompt with 4-18 s, so the first cap-length cut was often the wrong
  part. Re-edited from the takes themselves (`derive`, written as raw takes `<name>_101..` padded with the take's own
  bed so clean3 can still measure the noise): the jukebox (coin, then needle and chord, the 3 s of crackle between them
  cut), the Gold Record's value spinning up (the 2-4 s rise compressed 2-3x with the pitch kept, then its ding), the
  neon hum (its whole swell compressed), three fireworks inside 3 s (the takes spaced them 1-2.6 s apart), the spin's
  stomp and strum together, and the FS/XFS land (the band's ringing chord, not a strummed groove from mid-take).
- "A record slowing down" came back as 4-9 s of steady crackle with no audible wind-down: the Gold Record's spin-down
  is now a record stop (full speed, then slowing to a halt) on the pass's own fiddle run, guitar lick and chord.
- Sparkle twinkles came back 30-46 dB down (hiss once levelled): asked again louder and clearer (old takes in
  `raw_old/`); one new take had a 0.25 s hole and was rejected.
- The sad slide's three notes run 5-7 s: cut whole and time-compressed 2x (`STRETCH`), two takes that have all three
  notes picked by hand. The trophy is the take that is one big chord ringing out (the pick liked a three-chord riff).
- wsola's first and last half frame are under-windowed: they put a spike at the end of a compressed part, now trimmed.
- A take that is music end to end (the Encore riff) has no quiet to measure: clean3 took the music for the bed and
  gated the riff to scraps; its derived take is padded with a -84 dBFS hush instead.
- Moderation turned away 3 takes after their retries; asked again, 2 passed (one trophy take never did - five others
  were enough).
- Voices: none in the sheets; an audio-model second opinion on every file heard voices only in the crowd cheer (no
  words).

## The street pass (2026-11-03)

How the 47 sound sets (`frontend/assets/sfx_<stem>_<n>.wav` + `.ogg`) were made. Kept here so the pass can be re-run;
the raw generations and review spectrograms were left out (rebuildable, ~140 MB).

- `gen.py` / `orapi.py` - generate takes with OpenRouter's Seed Audio model (key read from
  `Documents/gamdevkey.txt`; never printed). `newlist.txt` / `cand.json` - the prompts and the takes made.
- `clean3.py` (+ `report3.json`) - the final clean (2026-11-03, after the owner still heard hiss): noise profile from
  the take's own bed (not its silent padding), per-type high-pass, noisereduce stationary (+ non-stationary on
  transients), a hard gate to exact digital zero, trims at the gate, damage checks with gentler retries.
- `process.py`, `process2.py`, `audiolib.py` - the first clean: DC + high-pass, spectral gate from the take's own quiet
  stretches, cut into single events, tight start / natural tail, expander, slow-attack compression, loudness match,
  a -1.5 dBFS limiter, end fades.
- `pick_takes.py` (+ `picks.json`, `manual_picks.json`) - choose the best, most alike takes per set.
- `synth.py` - the sets made in numpy instead (paint drips, sparkles, glow, shine).
- `assemble.py` -> `final.json`, then `encode_new.js` (the same settings as `tools/encode_sfx.js`) for the Opus copies.
- `an_existing.py`, `spec.py` - loudness/noise analysis of the existing set, spectrograms for review.

Run with the venv at `ClaudeRoblox/smukiez-slot/.venv` (numpy, scipy, soundfile, noisereduce). The sets are registered
in `SFX_SETS` / `SFX_VOL` in `frontend/index.html`; `sfx(name)` picks a take other than the last and nudges its pitch.

## Fall / Thanksgiving pass (2026-11-03)

The reskin's sounds, made on the same tools: `fall_spec.py` (prompts, kinds, caps, where each sound goes) and
`fall.py` (`gen` / `cand` / `pick` / `build` / `all`: Seed Audio takes -> process2's events -> pick_takes' scoring ->
clean3's strict clean and master, written straight into `frontend/assets/`). Work files live in `%TEMP%/fall_sfx/`
(raw takes, candidates, picks, `written.txt`, and a backup of every street-pass `sfx_*`/`music_*` file in
`old_assets/`). Opus copies: `node tools/sfx/encode_new.js <ClaudeRoblox>/.tools/pw/node_modules/playwright
%TEMP%/fall_sfx/written.txt` (its DIR now points at this repo's assets).

- `orapi.py` now reads the key from `%USERPROFILE%\Documents\gamdevkey.txt`.
- Replaced in place (same names, same roles): `can_shake` (corn-husk/straw shake), `spray_short` / `spray_long`
  (straw broom swish), `paint_drip` (gravy plop), `paint_burst` (pumpkin squelch), `cap_pop` (cider cork),
  `cascade` (acorns and apples tumbling), `drip_a..f` (soft plops), `scatter_land` (golden chime + turkey gobble),
  `bonus_start` (fiddle flourish), `bust_a/b` (sad jug wah-wah).
- New: 18 `land_<material>` sets for the fall symbols, the scarecrow's `hiccup`, `straw_rustle`, `crow_caw`,
  `jug_slosh`, `rope_creak`, `wing_flap`, `crow_peck`, and an optional `rooster` (not wired).
- Kept: the UI, counters, bells, coins, glints / sparkles / shine / glow, slam, whooshes, intro ident and the
  Casino Machines singles (spin, bet, reels, line, pop, multi hit, alerts, win text, trophy, coins rain, ...).
- What the cleaning taught: a deep thud (pumpkin) kept failing clean3's guard after denoising, so `fall.py` adds a last
  pass that reduces nothing and leaves it to the gate (only taken when the take's own bed is already under -72 dBFS); a
  broom swish is itself noise, so its bed limit is -56 (`BED`); the jug wah-wahs came back ~4 s, so they are
  time-compressed 2x with pitch kept (`wsola`) and re-levelled; the "fiddle + rooster" takes put the rooster ~2.5 s in,
  so the bonus start keeps only the fiddle (1.7 s cap) and the rooster got its own prompt.
