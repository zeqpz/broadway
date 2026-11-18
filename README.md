# Power Outage

A dark-comedy slot for [Stake Engine](https://stake-engine.com): the power is out across the country, the
companies are going under, and inside the president's oval office the only light is a few candles. Drawn as flat
adult-animation-sitcom cartoons with chunky, simple casual-slot shapes. It is a reskin of
[zeqpz/orleans](https://github.com/zeqpz/orleans) ("Voodoo on Bourbon", `main` ff43083); the math is unchanged
(`math-sdk/games/outage_5x5` = orleans' `voodoo_5x5`, renamed): 5x5 cluster pays, tumbles, Multis, FS / XFS
scatters, Bonus Boost, RTP 96.7%, max 10,000x. The four big books are over GitHub's file limit: they are kept locally
and uploaded to engine.io from disk (`tools/stake_upload.py`).

## What changed

| Part | Now |
|---|---|
| Symbols | H1 The President (an unnamed caricature holding a candle), H2 The Bodyguard (flashlight under his chin), H3 Bankrupt CEO (in a barrel), H4 Market Crash (a chart smashing through its screen), H5 Red Hotline, H6 AI Server (smoking, sad face), H7 Broke Piggy Bank; L1 Candle, L3 Dead Battery, L4 Blown Bulb; **M** Power Surge (colour by value: cyan, green, violet, orange, red-hot); **BS = "FS"** on a lit bulb; **ES = "XFS"** on a high-voltage sign |
| Animation | Every symbol has its own idle, land, win and multi clip, built and rendered in Blender (`tools/outage/blender/symanim.py`: the icon on a bone-bent mesh + flat cartoon effect sprites - coins, sparks, smoke, sweat, moths, red down-arrows, glass shards, cash) |
| Wins | Winners don't burn away: they swell, buzz white-hot like a bulb about to blow, and short out in a yellow-and-cyan flash with sparks (`drawHex` / `drawHexLight` in index.html). The Multi crackles and flashes before it blows |
| Background | The oval office in a blackout, flat cartoon (`assets/bonus_wall.webp`), kept alive by `frontend/bgscene.js`: live flat candle flames and their light pools, lightning in the windows (twice, with a bolt), clouds drifting past the moon behind the dead skyline, a lit window now and then, the power sputtering back on in fits and dying again, and a bodyguard's flashlight sweeping the room |
| Frame | A riveted breaker-panel frame with hazard stripes, a red breaker lever, cables over one corner, a frayed sparking wire and a dangling plug; the board backing is cut to its opening (`tools/outage/board_back.py`) |
| Layout | No character: a hanging POWER OUTAGE sign at the board's left whose bulb stutters, like the reference layout |
| UI | Candle-yellow chunky lettering (BIG / MEGA / XTREME / TOTAL WIN, BONUS), cream cards, steel and hazard-stripe plates, cyan Multi numerals in a hazard-stripe ring, lightning-bolt volatility pips, a solid navy HUD with a thick black outline |
| Music | A sneaky dark-comedy cartoon score (pizzicato strings, bassoon, oompah tuba, glockenspiel, muted trumpet, a mains hum): base D minor, intro A minor, bonus D minor, total F major, menu C (Lyria 3 Pro, `tools/music/cues.py`) |
| Sounds | 51 sets (`tools/sfx/outage_spec.py`): breaker clunks, transformer hum, light switches, zaps and arcs, a bulb flickering on, cash registers, rotary phone bells, coins, timpani and orchestra stings, a landing sound per symbol. HUD button sounds are the base build's |

## Pipeline (`tools/outage/`, run with `ClaudeRoblox/smukiez-slot/.venv`)

The OpenRouter key is read from `%USERPROFILE%\Documents\gamdevkey.txt`; scripts never print it.

1. **Symbols**: `gen_anchor.py H1` (style anchor, with a crop of the reference screenshots for shape simplicity) ->
   `gen_symbols.py` (H1 + the reference as refs; prompts in `art/outage-src/symbols.json`, `prompts/`).
2. **UI**: `gen_ui.py gen` / `gen_extra.py gen` (Multi numerals, their ring, the shop banners); `flatten_face.py`,
   `fix_checker.py` + `fix_checker2.py` clean the image model's habits (smudges in empty cards, fake checkerboards).
3. **4K**: `upscale4k.py sym|ui|bg` (Real-ESRGAN x4), `prep_icons.py`, `gen_ui.py fit`, `gen_extra.py fit`, `vnum.py`.
4. **Background**: `bg_layers.py` (window-sky mask, flame/pool/moon/chandelier positions, skyline lights ->
   `frontend/assets/bg/`). The phone backgrounds are `assets/mobile/bg_portrait.webp` (a 2:3 redraw) and
   `bg_landscape.webp`.
5. **Blender**: `make_fx_sprites.py`, `patch_symanim.py` (the personalities), then
   `sh tools/outage/blender/render_all.sh` (13 symbols, 5 at a time) -> `qa_sym.py all` -> `tools/blender/pack_frames.py`
   -> `potion_tiers.py` (the surge's value colours) -> `make_phone_sheets.py`. The scenes can be opened and played in
   Blender (`art/blender/symbols/<ID>.blend`), or built live over the MCP (`runpy` the script and call `build(ID)`).
6. **Frame**: `frame_fit.py` (the opening's fractions -> `art/outage-src/frame_fit.json`), `board_back.py`,
   `make_mobile_art.py` (phone copies + `mobile_fit.json`).
7. **Front end**: `reskin_outage.py` applies every edit to `frontend/index.html`, `rules.js` and `boardgl.js` from the
   pristine orleans copies in `tools/outage/base/` as exact replacements (a changed base fails loudly).
8. **Music**: `tools/music/lyria.py <cue> --takes 2`, `tools/music/keys.py` to pick takes by key, copy to
   `art/music-src/`, `tools/music/build.py`, paste the printed MUSIC table into `reskin_outage.py`.
9. **Sounds**: `tools/sfx/outage.py all`, then `node tools/sfx/encode_new.js <.tools/pw/node_modules/playwright> %TEMP%/outage_sfx/written.txt`.

QA: `node tools/outage/qa_screens.js` (ident, features, board, shop), `node tools/outage/qa_win.js <event> [step] [s]`
(films a Bet Replay; `MODE=bonus` for bonus books). Screenshots go to `%TEMP%/outage_qa`.

## Run it locally

```
smukiez-slot/.venv/Scripts/python.exe frontend/mock_rgs.py
```
Open http://localhost:8788/index.html?sessionID=test&rgs_url=http://localhost:8788&lang=en&device=desktop (the first
run unpacks the books, about a minute). The Claude preview launch config is `poweroutage-game`.

## Notes

- The President is an original, unnamed caricature; there are no real names, official seals, brand names or logos
  anywhere in the game (the companies "going down" are generic gags: a crashing chart, a CEO in a barrel, a broke
  piggy bank, an AI server). Keep it that way for approval.
