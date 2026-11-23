"""Broadway on Nashville sound pass (2026-11-22): what Seed Audio is asked for and where each sound goes.
The same slots and outputs as Power Outage's outage_spec.py (so index.html's SFX table needs no new names), with
Lower Broadway honky-tonk prompts: guitar strums, twangs and slides, pedal-steel swells, banjo plucks, fiddle runs,
boot stomps and spur jingles, saloon doors and wood knocks, cash registers and coins, a record scratch for the Gold
Record, neon-sign buzz, marquee-bulb clicks, a bull snort, a hot-chicken fryer, a jukebox coin and needle drop,
fireworks for the Xtreme stage, and country stings for the big wins. Nothing speaks or sings, and no tune is a real
song's. Plus four new files for Encore (sfx_encore_riff, sfx_spotlight, sfx_flip, sfx_crowd_cheer).

NOT made here, kept exactly as the base build has them (owner): the HUD buttons (uiClick, uiHover, sliderTick,
swishIn/Out, menuOpen/Close, toggle, autoStart/Stop, bet, skip, hoverLoop - see nola_spec.py), and the black-and-white
SMUKIEZ ident's sounds (intro_* and land_brick; BROADWAY.md keeps that introduction as it is).

name -> (prompt, takes, kind, (min s, max s, keep, mode override), out)   - the same shape as outage_spec.py
  out   ("set", stem, target LUFS, SFX_SETS key, level, what) -> sfx_<stem>_1..keep.wav
        ("files", [file names], target LUFS, what)               -> those single files, in place
Run with tools/sfx/broadway.py (a copy of outage.py reading this file), then broadway_textures.py for the two loops."""
from nola_spec import FOUT as _FOUT, TONAL as _TONAL, BED as _BED, CLOSE, st

FOUT, TONAL, BED = dict(_FOUT), set(_TONAL), dict(_BED)     # copies: nola_spec's own tables stay as they are
MANUAL, STRETCH = {}, {}
REJECT = {}      # name -> candidate files ("3_0.wav") or whole take numbers heard wrong in review; build and pick skip them

PRE = "[Sound effect only. No voice, no speech, no music.] "
PRE_STING = "[Sound effect only. No voice, no speech, no singing, no lyrics.] "     # a played lick or chord is wanted
PRE_CROWD = "[Sound effect only. No speech, no words, no singing, no music.] "
GTR = "a twangy electric country guitar"

S = {
    # ---------------- the spin and the board ----------------
    "n_spin": (PRE_STING + "One hard cowboy boot stomp on a wooden stage floor together with one bright, loud strum of "
               + GTR + " playing a single open major chord that rings briefly.", 5, "hit", (.3, .9, 1, "gesture"),
               ("files", ["sfx_spin.wav"], -22, "spin: boot stomp + one twangy chord")),
    "n_reels": (PRE + "A steady, continuous, even fast rattle of a metal washboard being scraped with thimbles, with a "
                "light jingle of spurs on top, for two seconds, no accents.", 5, "foley", (.7, 2.2, 1, "sustain"),
                ("files", ["sfx_reels.wav"], -24, "reels turning: even washboard rattle (pitched by speed)")),
    "n_shake": (PRE + "Two quick jingles of metal cowboy boot spurs, a boot heel rocking twice: a bright metallic "
                "jing-jing.", 6, "foley", (.3, .8, 2, "gesture"), st("can_shake", "canShake", .34, "spin pressed: spur jingle")),
    "n_reelstop": (PRE + "One short solid knock of a cowboy boot heel stomping down on a wooden stage floor.", 5, "hit",
                   (.12, .5, 3, None), st("reel_stop", "reelStop", .3, "a column's last tile down: boot heel")),
    "n_tap": (PRE + "One soft, low, muffled knock of a knuckle on a thick wooden counter.", 6, "drop", (.06, .35, 6, None),
              ("files", ["sfx_drip_a.wav", "sfx_drip_b.wav", "sfx_drip_c.wav", "sfx_drip_d.wav", "sfx_drip_e.wav",
                         "sfx_drip_f.wav"], -25, "soft wood knocks (dripLand = drip_b on every icon landing)")),
    "n_cascade": (PRE + "A handful of plastic guitar picks, horseshoe nails and a few coins tumbling and clattering onto a "
                  "wooden table top in one quick short shower.", 5, "hit", (.3, 1.0, 2, "gesture"),
                  st("cascade", "cascade", .3, "the refill tumbling in: picks, nails and coins")),
    "n_pop": (PRE_STING + "One short sharp pluck of a single banjo string, plucked hard and muted at once: a quick dry "
              "twangy plink.", 6, "click", (.05, .3, 1, None), ("files", ["sfx_pop.wav"], -23, "one icon popping: banjo plink")),
    "n_burst": (PRE + "One short crackling buzz-pop of a neon sign tube shorting out: a quick electric fizz with a tiny "
                "glassy tinkle.", 5, "hit", (.12, .6, 3, None),
                st("paint_burst", "paintBurst", .26, "under every third icon pop: neon tube fizz")),
    "n_line": (PRE_STING + "A short bright happy country stab: " + GTR + " and a honky-tonk piano hitting one major chord "
               "together with a snare hit.", 5, "sting", (.25, .9, 1, None),
               ("files", ["sfx_line.wav"], -21, "a cluster pays: guitar + piano stab")),
    "n_scatter": (PRE_STING + "A neon sign lighting up: a soft electric buzz, then a bright pedal steel guitar swell rising "
                  "up and ringing out with a sparkling shimmer.", 6, "sting", (1.0, 2.6, 1, None),
                  ("files", ["sfx_scatter_land.wav"], -20, "FS/XFS lands: neon buzz + pedal-steel swell")),
    # ---------------- the Gold Record ----------------
    "n_multi": (PRE_STING + "A big punchy hit: a fast vinyl record scratch, then a deep booming kick drum thump with one "
                "loud twangy electric guitar chord.", 6, "hit", (.3, 1.8, 1, "gesture"),
                ("files", ["sfx_multi_hit.wav"], -19, "a Gold Record going off: record scratch + boom + chord")),
    "n_vanish": (PRE + "A vinyl record on a turntable slowing down to a stop: the sound drops in pitch in a descending "
                 "warble and winds down to nothing.", 8, "whoosh", (.5, 1.2, 3, None),
                 st("vanish", "vanish", .42, "a Gold Record spinning down (no pop)")),
    "n_reveal": (PRE + "A turntable spinning up to speed: a rising warbling whirr with a soft vinyl crackle, ending on one "
                 "tiny bright ding.", 6, "whoosh", (.4, 1.0, 2, None),
                 st("reveal", "reveal", .3, "a Gold Record's value spinning up")),
    "n_slam": (PRE + "One heavy punchy slam of a fist pounding a thick wooden table top, with a short bright metallic "
               "jingle of spurs.", 6, "hit", (.2, 1.4, 3, "gesture"),
               st("mult_slam", "multSlam", .4, "the x<N> slamming onto the figure")),
    "n_alert": (PRE_STING + "A short excited country fanfare: a fast fiddle and " + GTR + " playing a quick rising lick "
                "together, with two cowbell clanks.", 6, "sting", (.6, 1.6, 2, None),
                ("files", ["sfx_jackpot_alert_a.wav", "sfx_jackpot_alert_b.wav"], -21, "a run of Gold Records: fiddle + guitar lick")),
    "n_bust": (PRE_STING + "A comical sad country slide: a steel guitar playing three drooping notes going down, "
               "wah, wah, waaah, the last one sagging slowly down in pitch and fading away.", 6, "sting", (1.6, 3.4, 2, None),
               ("files", ["sfx_bust_a.wav", "sfx_bust_b.wav"], -22, "Gold Records landed, nothing used them: sad steel slide")),
    # ---------------- the win presentation ----------------
    "n_sweep_short": (PRE + "A quick airy whoosh of a lasso rope swinging past once through the air, half a second.", 6,
                      "whoosh", (.35, .6, 3, "sustain"), st("spray_short", "sprayShort", .2, "the win line: lasso whoosh")),
    "n_sweep_long": (PRE + "A long smooth airy whoosh of a lasso rope swinging round through the air evenly for about one "
                     "and a half seconds and stopping cleanly.", 8, "whoosh", (.9, 1.5, 2, "sustain"),
                     st("spray_long", "sprayLong", .2, "the win line, long")),
    "n_plink": (PRE + "One tiny click of a small marquee light bulb switching on: a little glassy tick.", 6, "drop",
                (.06, .4, 5, None), st("paint_drip", "paintDrip", .16, "the win line's bulbs: tiny clicks")),
    "n_glow": (PRE + "A soft warm buzzing hum of a neon sign tube glowing brighter for a moment, swelling up and fading.",
               5, "tone", (.4, 1.3, 2, None), st("glow_pulse", "glowPulse", .18, "a winning symbol lighting up: neon hum")),
    "n_shine": (PRE + "A quick bright shimmering swish, like light gleaming across glittering rhinestones and sequins.", 5,
                "tone", (.25, .9, 2, None), st("shine", "shine", .16, "a shine sweeping a symbol")),
    "n_sparkle": (PRE + "Light delicate glittering twinkles, a few tiny high chimes, like rhinestones catching the light.",
                  5, "tone", (.3, 1.2, 3, None), st("sparkle", "sparkle", .14, "twinkles")),
    "n_glint": (PRE + "One single small bright ting of a metal dinner triangle struck once lightly.", 6, "click",
                (.1, .6, 3, None), st("glint", "glint", .14, "one triangle ting")),
    "n_wintext": (PRE_STING + "A short happy ka-ching of an old brass cash register drawer popping open with a bell.", 6,
                  "sting", (.6, 1.5, 1, None), ("files", ["sfx_win_text.wav"], -21, "the win amount pops up: ka-ching")),
    "n_tick": (PRE + "One tiny crisp click of an old jukebox selector push button.", 6, "click", (.015, .08, 3, None),
               st("count_tick", "countTick", .16, "the win figure counting")),
    "n_countend": (PRE + "A heavy brass cash register drawer thunking shut with a bright bell ding and a short coin "
                   "jingle.", 5, "impact", (.4, 1.8, 1, "gesture"), st("count_end", "countEnd", .34, "the figure lands")),
    "n_rise": (PRE_STING + "A quick rising whoosh with a pedal steel guitar sliding smoothly up in pitch underneath, about "
               "one second.", 5, "whoosh", (.6, 1.4, 2, None),
               st("count_whoosh", "countWhoosh", .2, "counting up again after the slam: steel slide up")),
    "n_float": (PRE + "A soft airy descending whoosh with a faint glassy shimmer fading away.", 5, "whoosh",
                (.6, 1.8, 2, None), st("float_away", "floatAway", .16, "the figure floating away")),
    "n_tick1": (PRE + "One crisp tiny click of a single silver coin tapped on a wooden counter.", 5, "click",
                (.02, .12, 1, None), ("files", ["sfx_money_tick.wav"], -24, "the total's counter tick")),
    "n_medium": (PRE_STING + "A short cheeky country riff: " + GTR + " playing a quick happy chicken-picking lick of "
                 "about six notes, with a banjo roll underneath.", 6, "sting", (.8, 2.0, 1, None),
                 ("files", ["sfx_medium_win.wav"], -21, "a medium win: chicken-picking lick")),
    "n_trophy": (PRE_STING + "A big triumphant country finale chord: " + GTR + ", a honky-tonk piano, a fiddle and a "
                 "pedal steel all ringing one bright major chord together, with a timpani roll and a long cymbal crash.",
                 6, "sting", (1.2, 3.0, 1, None), ("files", ["sfx_trophy.wav"], -19, "the total's arrival: big country chord")),
    "n_rain": (PRE + "Lots of silver coins raining and pouring down onto a pile of coins on a wooden table, a steady "
               "jingling shower.", 5, "foley", (1.2, 2.6, 1, "sustain"), ("files", ["sfx_coins_rain.wav"], -22, "coins raining")),
    "n_coins": (PRE + "A handful of heavy silver dollar coins jingling and clinking together.", 5, "foley",
                (.3, 1.2, 1, "gesture"), ("files", ["sfx_coins.wav"], -22, "silver dollars jingling")),
    "n_bell": (PRE + "Two quick loud clanks of a cowbell, clank-clank, bright and ringing.", 5, "tone", (.4, 1.6, 1, None),
               ("files", ["sfx_bell.wav"], -22, "spins added: cowbell")),
    "n_fstick": (PRE_STING + "One bright clear chime of a single electric guitar harmonic, a pure bell-like ping.", 6,
                 "tone", (.2, .9, 2, None), st("fs_tick", "fsTick", .24, "the free spins counter turning over")),
    "n_jackpot": (PRE_STING + "A huge country win sting: a fast snare drum roll into a loud bright major chord of brass "
                  "and " + GTR + ", with a timpani hit and a cymbal crash.", 6, "sting", (1.0, 2.6, 2, None),
                  ("files", ["sfx_jackpot_a.wav", "sfx_jackpot_b.wav"], -19, "big win: drum roll + brass and guitar chord")),
    "n_bonus": (PRE_STING + "A blazing bluegrass fiddle flourish running quickly up to a high note over a snare roll and a "
                "fast banjo roll, ending on one bright twangy guitar chord.", 6, "sting", (.9, 1.8, 1, None),
                ("files", ["sfx_bonus_start.wav"], -20, "free spins start: fiddle + banjo run")),
    "n_bonusend": (PRE_STING + "A short country ending: " + GTR + " playing a quick run down to one final chord, with a "
                   "timpani hit and a choked cymbal.", 5, "sting", (.8, 2.0, 1, None),
                   ("files", ["sfx_bonus_end.wav"], -21, "free spins over: guitar run-down")),
    # ---------------- the bonus buy (its own sounds; its buttons' clicks stay HUD) ----------------
    "n_cork": (PRE + "Wooden saloon swinging doors pushed open: a short wooden creak and the doors flapping back with two "
               "soft wooden knocks.", 6, "hit", (.1, 1.0, 2, "gesture"),
               st("cap_pop", "capPop", .3, "the bonus buy opening: saloon doors")),
    "n_spell": (PRE_STING + "An old jukebox: a coin dropping into its slot and rattling down with a clunk, then a needle "
                "dropping onto a vinyl record with a crackle and one bright twangy guitar chord.", 5, "impact",
                (.6, 1.6, 1, "gesture"), st("buy_confirm", "buyConfirm", .36, "a bonus bought: jukebox coin + needle drop")),
    # ---------------- what each symbol lands like (LAND_FOLEY in index.html) ----------------
    "l_mask": (PRE + "A heavy vintage chrome microphone set down on a wooden stage: a solid soft thunk with a short "
               "metallic ring.", 4, "hit", (.08, .45, 2, None), st("land_mask", "landMask", .2, "H1 the Crooner's mic")),
    "l_doll": (PRE + "A soft sequinned cowboy hat with a veil tossed onto a table: a light soft thump with a tiny jingle "
               "of sequins.", 4, "hit", (.06, .4, 2, None), st("land_doll", "landDoll", .2, "H2 the Bachelorette's hat")),
    "l_brass": (PRE + "A wooden fiddle set down on a table: a hollow woody knock with a faint ring of its strings.", 4,
                "hit", (.1, .6, 2, None), st("land_brass", "landBrass", .2, "H3 the Fiddler")),
    "l_bone": (PRE + "One short snort of a big bull blowing air hard through its nostrils, with a heavy hoof thud.", 4,
               "hit", (.1, .6, 3, None), st("land_bone", "landBone", .2, "H4 the mechanical bull: snort")),
    "l_leather": (PRE + "A piece of breaded chicken dropped into a deep fryer of hot oil: a short burst of crackling "
                  "sizzle.", 4, "hit", (.15, .6, 2, None), st("land_pouch", "landPouch", .2, "H5 hot chicken: fryer sizzle")),
    "l_gator": (PRE + "A leather cowboy boot set down on a wooden floor: a solid heel clack with a short jingle of a spur.",
                4, "hit", (.1, .6, 2, None), st("land_gator", "landGator", .2, "H6 the rhinestone boot")),
    "l_pastry": (PRE + "A banjo set down on a table: a hollow drum-head thump with a short twangy ring of its strings.", 4,
                 "hit", (.06, .5, 2, None), st("land_pastry", "landPastry", .2, "H7 the banjo")),
    "l_metal": (PRE + "A small plastic guitar pick dropped onto a wooden table: a tiny light plastic tick.", 4, "hit",
                (.06, .45, 2, None), st("land_iron", "landIron", .2, "L3 the guitar pick")),
    "l_shell": (PRE + "A small metal harmonica set down on a wooden table: a short light metallic clink.", 4, "hit",
                (.06, .4, 2, None), st("land_shell", "landShell", .2, "L4 the harmonica")),
    "l_wax": (PRE + "An iron horseshoe dropped onto a wooden floor: a short heavy metallic clank.", 4, "hit",
              (.06, .4, 2, None), st("land_wax", "landWax", .2, "L1 the lucky horseshoe")),
    "l_glass": (PRE + "A vinyl record dropped flat onto a turntable platter: a short soft slap with a tiny needle crackle.",
                4, "hit", (.08, .5, 2, None), st("land_glass", "landGlass", .22, "M the Gold Record")),
    # ---------------- the Xtreme Bonus's rooftop stage (the two alarm slots) ----------------
    "n_xfsalarm": (PRE + "One firework rocket whistling up fast and bursting with a loud bang and a short crackle of "
                   "sparks.", 6, "sting", (.45, 1.1, 1, None),
                   ("files", ["sfx_xfs_alarm.wav"], -20, "an XFS scatter lands: one firework")),
    "n_xtalarm": (PRE + "A fireworks finale: three firework rockets whistling up and bursting one after another with loud "
                  "bangs and crackling sparkles.", 6, "sting", (1.4, 3.0, 1, None),
                  ("files", ["sfx_xtreme_alarm.wav"], -19, "the Xtreme Bonus triggers: three fireworks")),
    # ---------------- Encore (new, 2026-11-22) ----------------
    "n_encore": (PRE_STING + "A short blazing country guitar lick: " + GTR + " playing a fast flashy chicken-picking run "
                 "with string bends that climbs up and ends on one ringing high note, about one and a half seconds.", 6,
                 "sting", (1.0, 1.9, 1, None), ("files", ["sfx_encore_riff.wav"], -20, "Encore: Rosie's riff")),
    "n_spotlight": (PRE + "A big heavy theatre stage spotlight switching on: one loud deep mechanical clunk of a heavy "
                    "switch, then a low warm electrical hum of the lamp warming up, about one second.", 6, "foley",
                    (.6, 1.3, 1, "gesture"), ("files", ["sfx_spotlight.wav"], -21, "Encore: the spotlight lands")),
    "n_flip": (PRE_STING + "One quick bright twang of a single electric guitar string plucked once, with a tiny glittering "
               "sparkle on top, very short.", 6, "tone", (.15, .45, 1, None),
               ("files", ["sfx_flip.wav"], -22, "Encore: one symbol flipping")),
    "n_cheer": (PRE_CROWD + "A lively crowd in a small wooden music hall cheering, clapping and whistling loudly for about "
                "two seconds: wordless cheers, whoops and sharp whistles, no words.", 6, "foley", (1.5, 2.4, 1, "gesture"),
                ("files", ["sfx_crowd_cheer.wav"], -21, "Encore: the crowd cheering")),
}

FOUT.update({"n_xfsalarm": 120, "n_xtalarm": 250, "n_encore": 250, "n_spotlight": 220, "n_flip": 80, "n_cheer": 350,
             "n_vanish": 150, "n_bell": 200})
TONAL |= {"n_xfsalarm", "n_xtalarm", "n_encore", "n_flip", "n_spin", "n_pop", "n_spell", "n_rise", "l_pastry", "l_brass",
          "l_mask"}
# a texture IS noise: its bed is the sound (see outage.py's LOOSE_BED round too)
BED.update({"n_cheer": -50, "l_leather": -52, "l_bone": -54, "n_xtalarm": -56, "n_xfsalarm": -56, "n_burst": -58,
            "n_glow": -58, "n_spotlight": -60})

# which symbol makes which landing sound (LAND_FOLEY in frontend/index.html: unchanged keys)
LAND = {"H1": "landMask", "H2": "landDoll", "H3": "landBrass", "H4": "landBone", "H5": "landPouch", "H6": "landGator",
        "H7": "landPastry", "L1": "landWax", "L3": "landIron", "L4": "landShell", "M": "landGlass"}

# not made by this pass: the base build's files stay byte for byte (broadway.py refuses to write them)
HUD_FILES = ["sfx_ui_click_1.wav", "sfx_ui_click_2.wav", "sfx_ui_click_3.wav", "sfx_ui_hover_1.wav", "sfx_ui_hover_2.wav",
             "sfx_slider_tick_1.wav", "sfx_slider_tick_2.wav", "sfx_swish_in_1.wav", "sfx_swish_in_2.wav",
             "sfx_swish_out_1.wav", "sfx_swish_out_2.wav", "sfx_menu_open.wav", "sfx_menu_close.wav", "sfx_toggle.wav",
             "sfx_auto_start.wav", "sfx_auto_stop.wav", "sfx_bet.wav", "sfx_skip.wav", "sfx_hover_loop.wav"]


def jobs():
    for name, (prompt, takes, kind, _, _) in S.items():
        yield name, prompt + CLOSE, takes, kind


# one event per take: the landings, the clicks and the single hits are cut to their first event only
SINGLE = {n for n in S if n.startswith("l_")} | {"n_pop", "n_tick", "n_tick1", "n_reelstop", "n_flip"}


# ---------------- what the review sheets caught (2026-11-22), and the fixes ----------------
# Seed Audio answers a musical or "slowly changing" prompt with 4-18 s of audio, so the first cap-length cut of a take
# was often the wrong part: the spin-up before the ding, the coin before the jukebox's chord, a long record wind-down's
# first second, a sparkle wash too quiet to be anything but hiss. Those are re-edited from their own takes (DERIVE):
# a window, time-compressed with the pitch kept (wsola) or a montage of two or three parts, written as extra raw takes
# <name>_101.. that cand / pick / build treat like any other; the plain takes are then REJECTed.
#   DERIVE[name] = [dict(segs=[(source sound, take, t0 s, t1 s, rate), ...], fx=None | ("tapestop", out s, hold s, power)), ...]
#   rate > 1 compresses (wsola, pitch kept); parts are joined with a 12 ms equal-power crossfade;
#   "tapestop" plays the joined audio at full speed for `hold` s, then slows it to a stop over the rest of `out` s
#   (speed = (1 - u) ** power): a record running down.
OLD = list(range(1, 100))                     # every plain take of a sound
DERIVE = {
    # a Gold Record spinning down: a record stop on the pass's own country takes (a fiddle-and-banjo run, a
    # chicken-picking lick, a ringing chord) - the plain "record slowing down" takes were 4-9 s of steady crackle
    "n_vanish": [dict(segs=[("n_bonus", 1, .30, 1.0, 1)], fx=("tapestop", 1.0, .12, 1.6)),
                 dict(segs=[("n_medium", 3, .12, .8, 1)], fx=("tapestop", 1.0, .12, 1.6)),
                 dict(segs=[("n_line", 5, .26, .9, 1)], fx=("tapestop", 1.0, .10, 1.4))],
    # a value spinning up: the takes' 2-4 s rise, compressed, and their ding
    "n_reveal": [dict(segs=[("n_reveal", 3, .11, 1.75, 2.2), ("n_reveal", 3, 5.44, 5.90, 1)]),
                 dict(segs=[("n_reveal", 2, .55, 3.35, 3.0)]),
                 dict(segs=[("n_reveal", 1, 2.2, 4.4, 2.5), ("n_reveal", 1, 5.88, 6.20, 1)])],
    # the neon hum swelling and fading: the whole 3-4 s swell, compressed
    "n_glow": [dict(segs=[("n_glow", 3, .08, 2.9, 2.2)]), dict(segs=[("n_glow", 1, 2.2, 6.2, 3.1)])],
    # the jukebox: the coin going in, then the needle and the chord (3 s of crackle between them cut out)
    "n_spell": [dict(segs=[("n_spell", 3, .14, .72, 1), ("n_spell", 3, 2.70, 3.75, 1)]),
                dict(segs=[("n_spell", 2, .32, 1.0, 1), ("n_spell", 2, 2.95, 3.90, 1)])],
    # three fireworks inside 3 s (the takes space them 1-2.6 s apart)
    "n_xtalarm": [dict(segs=[("n_xtalarm", 2, 1.30, 2.50, 1), ("n_xtalarm", 2, 2.78, 3.95, 1), ("n_xtalarm", 2, 4.05, 4.70, 1)]),
                  dict(segs=[("n_xtalarm", 5, .62, 3.62, 1)])],
    # FS/XFS lands: the band's bright chord ringing out (the first cut was a strummed groove from the middle of a take)
    "n_scatter": [dict(segs=[("n_scatter", 1, 1.38, 3.98, 1)])],
    # spin: the stomp and the strum together (the takes leave 0.4 s between them)
    "n_spin": [dict(segs=[("n_spin", 4, .16, .30, 1), ("n_spin", 4, .56, 1.32, 1)]),
               dict(segs=[("n_spin", 3, .11, .25, 1), ("n_spin", 3, .52, 1.28, 1)])],
    # Encore's riff: the lick that ends on a ringing note inside 2 s, given a bed to measure (the take is music from
    # its first sample to its last, so clean3's gate took the "bed" for noise and cut the riff to scraps)
    "n_encore": [dict(segs=[("n_encore", 5, .08, 2.1, 1)])],
}
REJECT.update({n: OLD for n in DERIVE})
# the trophy: the take that is one big chord ringing out (the pick's first choice was a three-chord riff)
# the fireworks: the montage with three big bangs (the pick liked the plain window, which has two)
# the sad slide: two takes with all three notes (the pick's second had two)
MANUAL.update({"n_trophy": ["5_0.wav"], "n_xtalarm": ["101_0.wav"], "n_bust": ["6_0.wav", "5_0.wav"]})
REJECT.update({"n_sparkle": ["5_0.wav"]})           # the new sparkle's take 5: 0.25 s of nothing, then blips
# the sad slide: three notes over 5-7 s, cut whole and time-compressed 2x with the pitch kept (as the fall pass's jug)
STRETCH.update({"n_bust": 2.0})
_T = {"n_bust": (3.2, 6.8, 2, None), "n_encore": (1.0, 2.0, 1, None), "n_reveal": (.4, 1.2, 2, None),
      "n_spell": (.6, 1.8, 1, None), "n_spin": (.3, 1.0, 1, "gesture"), "n_glow": (.4, 1.35, 2, None)}
for _n, _t in _T.items():
    S[_n] = S[_n][:3] + (_t,) + S[_n][4:]
# sparkle: "delicate glittering twinkles" came back 30-46 dB down - hiss once levelled. Asked again, louder and clearer
# (the first five takes are kept in raw_old/)
S["n_sparkle"] = (PRE + "A quick bright run of small glassy chimes twinkling up, like a tiny glockenspiel sparkle, crisp, "
                  "clear and loud, about one second.",) + S["n_sparkle"][1:]
FOUT.update({"n_vanish": 120, "n_reveal": 150, "n_xtalarm": 300})
# the jukebox as a sting (gap .6 s: the coin, the needle and the chord stay one event; a chord must ring, not be tightened)
S["n_spell"] = S["n_spell"][:2] + ("sting",) + S["n_spell"][3:]
# a played take that is music from end to end has no quiet bed to measure (the "bed" is the music itself, and clean3
# then reduces nothing): let the hand-picked ones through
BED.update({"n_trophy": -24})
