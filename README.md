# Broadway on Nashville

A Stake Engine slot on Lower Broadway in Nashville at night: the inside of a honky-tonk bar, all neon and stage lights. Drawn in a flat adult-animation TV cartoon style with original characters. Built from
[zeqpz/poweroutage](https://github.com/zeqpz/poweroutage) (e9f5c03, the iOS-fixed live build) with the
[zeqpz/workflow](https://github.com/zeqpz/workflow) skills and agents. The spec is [docs/BROADWAY.md](docs/BROADWAY.md).

The engine is Power Outage's: 5x5 cluster pays, tumbles, cell Multis, FS / XFS scatters, Bonus Boost, RTP 96.7%, max
10,000x. New in this game: **Encore** (below), plus new art, animation, sound and music throughout.

**Kept exactly as they were (owner):** the HUD, the bonus buy menu (layout and behaviour; its banner pictures are new)
and the black-and-white SMUKIEZ introduction.

## The game

| Part | Now |
|---|---|
| Symbols | H1 The Crooner, H2 The Bachelorette, H3 The Fiddler, H4 Mechanical Bull, H5 Hot Chicken, H6 Rhinestone Boot, H7 Banjo; L1 Horseshoe, L3 Guitar Pick, L4 Harmonica; **M Gold Record** (its disc shows its value: bronze to x2, silver to x5, gold to x20, platinum to x100, diamond above); **BS "FS"** neon on a marquee star; **ES "XFS"** neon over a jukebox |
| Encore | When a spin's tumbles are over, the crowd can call an Encore: a spotlight lands on a top symbol and every copy of one regular symbol (with at least 3 copies on the board) turns into it, then the board pays and tumbles again. Event `encore` {from, to, positions}; math in `math-sdk/games/broadway_5x5` (see DESIGN.md, "Encore") |
| No character | (Owner, 2026-11-24: "get rid of the character".) Rosie, the cowgirl guitarist who stood left of the board as a live Blender rig, is out of the game: no rig, no phone stills, no reactions; the bar's empty stage shows there. Her pipeline (`gen_rosie_v2.py`, `rosie_cut.py`, `blender/rosie_rig.py`, `pack_rosie.py`, `rosie_stills.py`) and art stay in `tools/` and `art/` unused |
| Background | The inside of an empty honky-tonk bar at night (no people), from a designed layout (`tools/broadway/gen_bg_bar.py`, v2 in `art/broadway-src/bg4/`): on the left a stage with a teal star backdrop, red curtains, footlights, a drum kit, an amp stack and two coloured stage lamps, left empty; a brick wall with neon and gold records in the middle; on the right a carved back-bar with teal back-lit bottle shelves, taps, a coffee pot, red stools, a cowhide rug and a jukebox; a polished floor that mirrors the neon, with an inlaid star. It is never still - `frontend/bgscene.js` flickers each of the five neon signs on its own (LIVE MUSIC, a pink guitar, HONKY TONK, a red boot, BAR) and chases the party bulbs and the stage footlights ("off" patches cut from a lights-off copy of the painting, `tools/broadway/bg_layers_bw.py`), sways two stage-light beams, turns two ceiling fans, drifts dust through the stage light, twinkles glints on the bottles, curls steam off the coffee pot, runs the jukebox's tubes through the colours and sweeps a shine over the gold records. Phones show it as a still picture (iOS memory rules). The Xtreme Bonus plays on a rooftop stage with fireworks |
| Frame and sign | A honky-tonk stage frame with marquee bulbs; a neon BROADWAY ON NASHVILLE sign whose ON has a loose contact (`tools/broadway/sign_layers_bw.py`) |
| Win line | A hot-pink neon tube drawn symbol to symbol |
| Sound | Every sound effect remade with Seed Audio (`tools/sfx/broadway_spec.py`) except the HUD buttons; four Encore sounds; five honky-tonk music cues (`tools/music/cues.py`) |

## Pipeline (`tools/broadway/`, Python from `ClaudeRoblox/smukiez-slot/.venv`)

The OpenRouter key is read from `%USERPROFILE%\Documents\gamdevkey.txt`; scripts never print it.

1. **Symbols**: `gen_symbols_v2.py` (gpt-image-2.6, Rosie v2 as the style reference) -> `symbols_v2_chain.sh`
   (4K, icons, Blender `blender/symanim.py` for every clip, `qa_sym.py`, `tools/blender/pack_frames.py`,
   `record_tiers.py` for the Gold Record metals, `make_phone_sheets.py`, `make_mobile_art.py`).
2. **Rosie (unused since 2026-11-24)**: `gen_rosie_v2.py` (figure) -> `rosie_cut.py cut|complete|fit|faces|fitfaces` (pieces cut from the
   figure along its ink lines, hidden areas completed by the model or inpainted) -> Blender
   `blender/rosie_rig.py -- build,export,render` -> `qa_rosie.py` -> `pack_rosie.py` -> `rosie_stills.py` (phones).
3. **Backgrounds**: `gen_bg_bar.py layout|gen|detail|pick|unlit|mobile|install` (the bar; `gen_bg_v2.py` made the
   Xtreme rooftop and the earlier street, kept in `art/broadway-src/bg_street_old/`) -> `bg_layers_bw.py` (its `PROPS`
   place the live details) -> `node tools/broadway/qa_bar.js`.
4. **UI**: `gen_ui_bw.py gen|fit` (after `upscale4k.py ui`), `sign_layers_bw.py`, `frame_fit.py`, `board_back.py`,
   `vnum.py` + `vnum_ink.py` + `vborder_bw.py`, `make_mobile_art.py`.
5. **Front end**: `reskin_broadway.py` applies every edit to `frontend/index.html` and `rules.js` from Power Outage's
   files in `tools/broadway/base/` as exact replacements (a changed base fails loudly).
6. **Lobby art**: `gen_media_bw.py gen|build` (covers with no text: The Crooner on the bar's stage; separate tile background and foreground layers, `media/tiles/fg_crooner.png`). The Encore card's picture: `gen_encore_icon.py`.
7. **Upload**: GitHub `zeqpz/broadway` (public) -> `howtotuploadonengine/github_upload_tab.js` (front, Route A); the math books are too big for git, so `ONLY=math python tools/stake_upload.py manifest ../engine_upload_broadway` (Route B).

Mock RGS: `frontend/mock_rgs.py` on port 8822 (launch config `broadway-game`). QA: `node tools/broadway/qa_screens.js`,
`node tools/broadway/qa_win.js <event>` (Bet Replay film; `MODE=bonus|extremebonus`), `node tools/broadway/qa_phone.js`
(the iOS phone-tier gate - run it after every visual pass).
