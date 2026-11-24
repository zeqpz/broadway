# Broadway on Nashville - design spec (2026-11-22)

A Stake Engine slot built from Power Outage (`zeqpz/poweroutage`, e9f5c03 - the iOS-fixed build that is live) with
the `zeqpz/workflow` skills and agents. Same engine: 5x5 cluster pays, tumbles, cell Multis, FS / XFS scatters,
Bonus Boost, RTP 96.7%, max 10,000x. New: the theme, every picture, every animation (Blender), every sound except the
HUD buttons, the music, the Multis' look, and one new mechanic - **Encore**.

**Kept exactly as they are (owner):** the HUD, the bonus buy menu (its layout and behaviour; its banner pictures are
re-themed), and the black-and-white SMUKIEZ introduction.

## Look

Flat adult-animation sitcom cartoon - the drawing style of shows like Rick and Morty / Family Guy: thick clean black
outlines, flat colour, one hard cel shade, big expressive eyes, chunky simple shapes. **Original characters only** -
no characters from those shows, no real people, no real bars, brands or signs (the owner's reference photo is a real
bar's neon sign: we take the idea - a neon cowgirl with a guitar - not its name or design).

Palette: neon hot pink, neon electric blue, neon red, marquee-bulb amber/gold, warm honky-tonk wood, deep navy night.

## No character beside the board

(Owner, 2026-11-24: "get rid of the character".) The game was first built with a cowgirl guitarist, Rosie, as a live 2D rig
left of the board with reaction clips. She is out of the game: no rig, no phone stills, no reactions, and no mention in
the cards or rules. The bar's empty stage shows where she stood; the Encore card shows a red guitar in a spotlight
(`tools/broadway/gen_encore_icon.py`). Her pipeline and source art stay in the repo, unused.

## Symbols (ids unchanged)

| id | symbol |
|---|---|
| H1 | The Crooner - an original pompadoured country star in a rhinestone suit singing into a vintage mic |
| H2 | The Bachelorette - a bride-to-be in a pink cowboy hat and veil, mid "woo!" |
| H3 | The Fiddler - a bearded old-timer sawing a fiddle |
| H4 | Mechanical Bull - bucking, with a comic face |
| H5 | Hot Chicken - fiery red Nashville hot chicken on white bread with pickles, flames |
| H6 | Rhinestone Boot - a red cowboy boot with a gold star and spur |
| H7 | Banjo |
| L1 | Lucky Horseshoe |
| L3 | Guitar Pick |
| L4 | Harmonica |
| M | **Gold Record** Multi - a spinning record whose disc shows its value's certification: black vinyl (low), silver, gold, platinum, diamond (x500+) |
| BS | "FS" in neon tube letters on a marquee star with chasing bulbs |
| ES | "XFS" in neon over a glowing retro jukebox |

Feature names: Multi = **Gold Record**; Wall Line = **Hit Parade** (a run of records); Full Wall = **Sold-Out Show**;
line drops = **Tips** (the small multipliers a paid cluster leaves). Standard Bonus / Xtreme Bonus keep their names.
Multi numerals: neon-tube figures coloured by value (glow baked into the glyph art, so phones need no filters).

## Encore (the new mechanic)

When a spin's tumbles are over and the board pays nothing more, the crowd can call an **Encore**: a stage spotlight
sweeps the board and locks onto a premium symbol (the Headliner, H1-H7), and **every copy of one regular symbol
(L1 / L3 / L4) on the board turns into the Headliner**. Then the board is paid again and the tumbles carry on as
normal (Gold Records go off, cell multipliers count). At most one Encore per spin (per free spin in a bonus). It can
come on any spin, losing or winning, more often in the bonus.

Math (`math-sdk/games/broadway_5x5`): after `settle_boosters`, if no wincap, roll `encore_chance_*` (base / free /
extreme); source = a low symbol on the board (weighted by its count, needs >= 3 copies), target = a premium by
`encore_target_weights`. Event, positions padded +1 like every other event:

```
{"type": "encore", "from": "L1", "to": "H3", "positions": [{"reel": r, "row": c}, ...]}
```

emitted after that cascade's final `setWin`/`setTotalWin`, before the follow-up cascade's events (`winInfo`,
`tumbleBoard`, `booster`, ...). The follow-up cascade has its own small tumble budget.

Frontend: a guitar riff, a spotlight sweeps and lands, ENCORE! title in neon, each `from` cell flips to `to` with
a neon flash (positions in the event), riff + crowd cheer. Phones: no spotlight canvas (a still cone image), no filters.

## Background and layout

(2026-11-23, owner: "make the background inside a nashville bar ... not static, small visual animations / details, no
people"; later the same day: "more appealing, more detailed and less bland" - the v2 painting, `art/broadway-src/bg4/`.)
The inside of an empty honky-tonk on Lower Broadway at night, seen straight on toward its back wall, in three clear
zones so it reads rich but not chaotic: **the stage** on the left (teal backdrop with gold stars, red curtains, a riser
with footlights, a drum kit, an amp stack, a mic and two coloured stage lamps - empty); **the
brick wall** in the middle (gold records, hanging guitars); **the bar** on the right (a carved back-bar with two teal
back-lit bottle shelves, taps, a coffee pot, red stools, a cowhide rug, a jukebox). The floor is dark polished wood that
mirrors the neon, with an inlaid star. Five neon signs (LIVE MUSIC, a pink guitar, HONKY TONK, a red boot, BAR) and one
string of party bulbs. The style allows painted lighting (glow, pools of colour, reflections) on top of the clean line
art. No people anywhere.
It is never still (`frontend/bgscene.js`, desktop only): each neon sign flickers on its own, the party bulbs and the
footlights chase, two stage-light beams (pink, blue) sway and swell, two ceiling fans turn, dust drifts through the
stage light, glints twinkle on the bottles, steam curls off the coffee pot, the jukebox's tubes run through the colours
and a shine sweeps the gold records. Phones show a still picture.
Xtreme Bonus: its own rooftop stage over the skyline with fireworks. Board frame: a honky-tonk stage frame (wood,
brass, marquee bulbs, neon trim). Title logo: BROADWAY ON NASHVILLE in neon, right of the board (centred over it on a phone).

## Sound

Every sound effect re-made with Seed Audio (`tools/sfx/broadway_spec.py`) except the HUD buttons, which keep the base
build's sounds. New cues for Encore: `sfx_encore_riff`, `sfx_spotlight`, `sfx_flip`, `sfx_crowd_cheer`. Music: five
instrumental honky-tonk / country cues (Lyria 3 Pro, `tools/music/cues.py`).

## Ports

Mock RGS **8822**, launch config `broadway-game`.
