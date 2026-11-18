"""Power Outage sound pass (2026-11-18): what Seed Audio is asked for and where each sound goes.
The same slots and outputs as Voodoo on Bourbon's nola_spec.py (so index.html's SFX table needs no new names), with
blackout dark-comedy prompts: mains hum, zaps, sparks, breaker switches, candle whooshes, rotary phones, cash registers,
coins, timpani hits. As before, the HUD buttons keep the base build's sounds, and Doc's foley is not made (no Doc).
Run with tools/sfx/outage.py (a copy of nola.py reading this file)."""
from nola_spec import FOUT, TONAL, BED, MANUAL, STRETCH, CLOSE, st   # the cleaner's tables are the same

PRE = "[Sound effect only. No voice, no speech, no music.] "
PRE_STING = "[Sound effect only. No voice, no speech, no singing.] "

S = {
    # ---------------- the spin and the board ----------------
    "n_spin": (PRE_STING + "A big heavy electrical breaker switch being thrown: a loud mechanical clunk followed by a short "
               "rising electrical whine as power surges up.", 5, "hit", (.3, .9, 1, "gesture"),
               ("files", ["sfx_spin.wav"], -22, "spin: breaker clunk + power whine")),
    "n_reels": (PRE + "A steady, continuous, even electrical buzzing hum of a big transformer, with a light fast clicking "
                "relay chatter on top, for two seconds, no accents.", 5, "foley", (.7, 2.2, 1, "sustain"),
                ("files", ["sfx_reels.wav"], -24, "reels turning: even transformer hum + relay chatter")),
    "n_shake": (PRE + "Flicking a light switch on and off quickly twice: click-click, click-click, a dry plastic switch.",
                6, "foley", (.3, .8, 2, "gesture"), st("can_shake", "canShake", .34, "spin pressed: light switch flicks")),
    "n_reelstop": (PRE + "One short solid heavy clunk of a metal electrical fuse box door shutting.", 5, "hit",
                   (.12, .5, 3, None), st("reel_stop", "reelStop", .3, "a column's last tile down")),
    "n_tap": (PRE + "One soft, low, muffled tap of a fingertip on a wooden desk.", 6, "drop", (.06, .35, 6, None),
              ("files", ["sfx_drip_a.wav", "sfx_drip_b.wav", "sfx_drip_c.wav", "sfx_drip_d.wav", "sfx_drip_e.wav",
                         "sfx_drip_f.wav"], -25, "soft desk taps (dripLand = drip_b on every icon landing)")),
    "n_cascade": (PRE + "A handful of coins, paper clips and a stapler tumbling and clattering onto a wooden desk in one "
                  "quick short shower.", 5, "hit", (.3, 1.0, 2, "gesture"),
                  st("cascade", "cascade", .3, "the refill tumbling in: desk clutter")),
    "n_pop": (PRE + "One short sharp electrical zap pop, like a light bulb blowing with a tiny tinkle of glass.", 6, "click",
              (.05, .3, 1, None), ("files", ["sfx_pop.wav"], -23, "one icon shorting out")),
    "n_burst": (PRE + "One short crackling electric spark burst, a quick fizzing zzzt.", 5, "hit", (.12, .6, 3, None),
                st("paint_burst", "paintBurst", .26, "under every third icon pop: a spark burst")),
    "n_line": (PRE_STING + "A short bright cartoon orchestra stab: a muted trumpet and pizzicato strings hitting one happy "
               "chord with a glockenspiel ting.", 5, "sting", (.25, .9, 1, None),
               ("files", ["sfx_line.wav"], -21, "a cluster pays: orchestra stab")),
    "n_scatter": (PRE_STING + "A big old light bulb flickering and then switching on with a bright glassy electric chime and "
                  "a warm rising hum.", 6, "sting", (1.0, 2.6, 1, None),
                  ("files", ["sfx_scatter_land.wav"], -20, "FS/XFS lands: the bulb comes on")),
    "n_multi": (PRE + "A big powerful electrical surge: a deep booming thump with a loud crackling high-voltage arc and "
                "sizzling sparks.", 6, "hit", (.3, 1.8, 1, "gesture"),
                ("files", ["sfx_multi_hit.wav"], -19, "a Multi going off: power surge boom + arc")),
    "n_vanish": (PRE + "A short electrical fizzle dying away, like a fuse blowing: a crackle that drops in pitch and "
                 "sputters out.", 8, "whoosh", (.5, 1.2, 3, None),
                 st("vanish", "vanish", .42, "a surge shorting out (no pop)")),
    "n_reveal": (PRE + "A soft rising electric charge-up whine with a little sparkle on top, ending on a tiny ding.", 6,
                 "whoosh", (.4, 1.0, 2, None), st("reveal", "reveal", .3, "a Multi's value charging up")),
    "n_slam": (PRE + "One heavy punchy cartoon stamp thud, like a rubber stamp slammed on a desk, with a short electric "
               "zap.", 6, "hit", (.2, 1.4, 3, "gesture"), st("mult_slam", "multSlam", .4, "the x<N> slamming onto the figure")),
    "n_alert": (PRE_STING + "A short urgent cartoon alarm: an old electric bell ringing fast for a moment with an orchestra "
                "stab.", 6, "sting", (.6, 1.6, 2, None),
                ("files", ["sfx_jackpot_alert_a.wav", "sfx_jackpot_alert_b.wav"], -21, "a run of Multis: alarm bell")),
    "n_bust": (PRE_STING + "A sad cartoon power-down: an electrical hum winding down slowly in pitch to silence with a final "
               "little click, like everything switching off.", 6, "sting", (1.6, 3.4, 2, None),
               ("files", ["sfx_bust_a.wav", "sfx_bust_b.wav"], -22, "Multis landed, nothing used them: power-down")),
    "n_sweep_short": (PRE + "A short smooth electric whoosh, like current racing along a wire.", 6, "whoosh",
                      (.35, .6, 3, "sustain"), st("spray_short", "sprayShort", .2, "the win line: current whoosh")),
    "n_sweep_long": (PRE + "A long smooth electric whoosh with a soft crackle, like current racing along a long wire.", 8,
                     "whoosh", (.9, 1.5, 2, "sustain"), st("spray_long", "sprayLong", .2, "the win line, long")),
    "n_plink": (PRE + "One tiny high electric spark tick, a single short tsk.", 6, "drop", (.06, .4, 5, None),
                st("paint_drip", "paintDrip", .16, "sparks off the win line: tiny ticks")),
    "n_glow": (PRE + "A soft warm electrical hum swelling up and fading, like a light bulb glowing brighter for a moment.",
               5, "tone", (.4, 1.3, 2, None), st("glow_pulse", "glowPulse", .18, "a winning symbol lighting up")),
    "n_shine": (PRE + "A quick bright shimmering glassy swish, like light gleaming across glass.", 5, "tone",
                (.25, .9, 2, None), st("shine", "shine", .16, "a shine sweeping a symbol")),
    "n_sparkle": (PRE + "Light delicate glittering twinkles, a few tiny high chimes.", 5, "tone", (.3, 1.2, 3, None),
                  st("sparkle", "sparkle", .14, "twinkles")),
    "n_glint": (PRE + "One single bright tiny glassy ting.", 6, "click", (.1, .6, 3, None), st("glint", "glint", .14, "one ting")),
    "n_wintext": (PRE_STING + "A short happy cartoon ka-ching of an old cash register drawer popping open with a bell.", 6,
                  "sting", (.6, 1.5, 1, None), ("files", ["sfx_win_text.wav"], -21, "the win amount pops up: ka-ching")),
    "n_tick": (PRE + "One tiny crisp click of an old mechanical counter digit flipping.", 6, "click", (.015, .08, 3, None),
               st("count_tick", "countTick", .16, "the win figure counting")),
    "n_countend": (PRE + "A satisfying heavy cash register thunk with a bright bell ding.", 5, "impact",
                   (.4, 1.8, 1, "gesture"), st("count_end", "countEnd", .34, "the figure lands")),
    "n_rise": (PRE + "A quick rising electric whine whoosh, power charging up.", 5, "whoosh", (.6, 1.4, 2, None),
               st("count_whoosh", "countWhoosh", .2, "counting up again after the slam")),
    "n_float": (PRE + "A soft airy descending whoosh with a faint electric fizz.", 5, "whoosh", (.6, 1.8, 2, None),
                st("float_away", "floatAway", .16, "the figure floating away")),
    "n_tick1": (PRE + "One crisp tiny coin click.", 5, "click", (.02, .12, 1, None),
                ("files", ["sfx_money_tick.wav"], -24, "the total's counter tick")),
    "n_medium": (PRE_STING + "A short cheeky cartoon fanfare: a muted trumpet and clarinet playing a quick happy little "
                 "riff with pizzicato strings.", 6, "sting", (.8, 2.0, 1, None),
                 ("files", ["sfx_medium_win.wav"], -21, "a medium win: cheeky fanfare")),
    "n_trophy": (PRE_STING + "A big triumphant cartoon orchestra chord with a timpani roll and a cymbal crash, bright and "
                 "victorious.", 6, "sting", (1.2, 3.0, 1, None),
                 ("files", ["sfx_trophy.wav"], -19, "the total's arrival: big orchestra chord")),
    "n_rain": (PRE + "Lots of coins raining and pouring down onto a pile of coins, a steady jingling shower.", 5, "foley",
               (1.2, 2.6, 1, "sustain"), ("files", ["sfx_coins_rain.wav"], -22, "coins raining")),
    "n_coins": (PRE + "A handful of coins jingling and clinking together.", 5, "foley", (.3, 1.2, 1, "gesture"),
                ("files", ["sfx_coins.wav"], -22, "coins jingling")),
    "n_bell": (PRE + "One ring of an old red rotary telephone bell, a short loud brrring.", 5, "tone", (.4, 1.6, 1, None),
               ("files", ["sfx_bell.wav"], -22, "the hotline rings (spins added)")),
    "n_fstick": (PRE + "One crisp click of a big electric light switch.", 6, "tone", (.2, .9, 2, None),
                 st("fs_tick", "fsTick", .24, "the free spins counter turning over")),
    "n_jackpot": (PRE_STING + "A huge cartoon win: a fast timpani and snare roll into a loud bright orchestra chord with a "
                  "big electrical surge zap.", 6, "sting", (1.0, 2.6, 2, None),
                  ("files", ["sfx_jackpot_a.wav", "sfx_jackpot_b.wav"], -19, "big win: drum roll + chord + zap")),
    "n_bonus": (PRE_STING + "Every light in a building switching back on at once: a big breaker clunk, a rising electrical "
                "hum and a bright cartoon orchestra flourish.", 6, "sting", (.9, 1.8, 1, None),
                ("files", ["sfx_bonus_start.wav"], -20, "free spins start: the power comes back")),
    "n_bonusend": (PRE_STING + "A cartoon orchestra ending flourish with a timpani hit, then one light switch click off.", 5,
                   "sting", (.8, 2.0, 1, None), ("files", ["sfx_bonus_end.wav"], -21, "free spins over: ending")),
    "n_cork": (PRE + "A heavy metal fuse box door creaking open with a clunk.", 6, "hit", (.1, 1.0, 2, "gesture"),
               st("cap_pop", "capPop", .3, "the bonus buy opening: fuse box door")),
    "n_spell": (PRE + "A big electrical power-up: a deep breaker clunk and a strong rising hum ending in a bright zap.", 5,
                "impact", (.6, 1.6, 1, None), st("buy_confirm", "buyConfirm", .36, "a bonus bought")),
    # ---------------- what each symbol lands like (LAND_FOLEY in index.html) ----------------
    "l_mask": (PRE + "A soft heavy cloth thump, like a man in a thick wool suit plopping down into a leather chair.", 4,
               "hit", (.08, .45, 2, None), st("land_mask", "landMask", .2, "H1 the President")),
    "l_doll": (PRE + "A firm soft thump with a click of a flashlight switch.", 4, "hit", (.06, .4, 2, None),
               st("land_doll", "landDoll", .2, "H2 the bodyguard")),
    "l_brass": (PRE + "One hollow wooden barrel thunk.", 4, "hit", (.1, .6, 2, None),
                st("land_brass", "landBrass", .2, "H3 the bankrupt CEO's barrel")),
    "l_bone": (PRE + "A plastic computer monitor clunking down with a tiny glass crack.", 4, "hit", (.06, .4, 3, None),
               st("land_bone", "landBone", .2, "H4 the crashing chart")),
    "l_leather": (PRE + "A heavy old rotary telephone clunking down with a short faint bell ding inside it.", 4, "hit",
                  (.08, .45, 2, None), st("land_pouch", "landPouch", .2, "H5 the hotline phone")),
    "l_gator": (PRE + "A metal computer server box clunking down with a short electrical buzz blip.", 4, "hit",
                (.1, .6, 2, None), st("land_gator", "landGator", .2, "H6 the AI server")),
    "l_pastry": (PRE + "A ceramic piggy bank clunking down with one coin rattling inside.", 4, "hit", (.06, .4, 2, None),
                 st("land_pastry", "landPastry", .2, "H7 the broke piggy bank")),
    "l_metal": (PRE + "A small metal battery tapping down on a desk, a light tink.", 4, "hit", (.06, .45, 2, None),
                st("land_iron", "landIron", .2, "L3 the dead battery")),
    "l_shell": (PRE + "A glass light bulb set down on a desk with a delicate glassy clink.", 4, "hit", (.06, .4, 2, None),
                st("land_shell", "landShell", .2, "L4 the blown bulb")),
    "l_wax": (PRE + "A small candle in a brass holder set down on wood, a soft clink and a tiny flame flutter.", 4, "hit",
              (.06, .4, 2, None), st("land_wax", "landWax", .2, "L1 the candle")),
    "l_glass": (PRE + "One short crackling electric zap.", 4, "hit", (.08, .5, 2, None),
                st("land_glass", "landGlass", .22, "M the power surge")),
}


LAND = {"H1": "landMask", "H2": "landDoll", "H3": "landBrass", "H4": "landBone", "H5": "landPouch", "H6": "landGator",
        "H7": "landPastry", "L1": "landWax", "L3": "landIron", "L4": "landShell", "M": "landGlass"}


def jobs():
    for name, (prompt, takes, kind, _, _) in S.items():
        yield name, prompt + CLOSE, takes, kind


# one event per take: the landings, the clicks and the single hits are cut to their first event only
SINGLE = {n for n in S if n.startswith("l_")} | {"n_pop", "n_tick", "n_tick1", "n_reelstop"}
