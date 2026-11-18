"""The game's five music cues: where each plays, what Lyria is asked for, and how build.py cuts it.

Power Outage (2026-11-18): a dark-comedy blackout inside the president's office. Every cue is an instrumental
cartoon dark-comedy score - the sneaky, tiptoeing music of an animated sitcom when everything is going wrong:
pizzicato strings, a bassoon and an oompah tuba, a clarinet, a glockenspiel and celesta, a muted trumpet, brushed snare
and timpani, with a low electrical hum and the odd buzzing synth zap. D minor for the base game, the menu and the
TOTAL WIN (D major), A minor (its dominant) for the free spins' intro and the free spins. Lyria takes the tempo but not
the key: keep takes for their key (chroma readout).

  bars       the loop's length in bars (4/4)
  head       None: the cue is only the loop. A number: the take's opening plays once and the loop
             starts that many seconds in (snapped to the take's beat), cut from wherever after
             loop_from fits best; the opening keeps ringing under it for `tail` seconds (default 2)
  start      seconds cut off the take's front before anything else (head and loop_from count from there)
  loop_from  seconds into the take before which no loop may start (past its intro)
  game_lufs  how loud the cue should sit in the game (the music bar at 100); sets its MUSIC level
"""

NO_VOX = ("Strictly instrumental: no vocals, no singing, no humming, no shouts, no chants, no spoken words. ")
BAND = ("a small cartoon dark-comedy orchestra: plucked pizzicato strings, a sneaky bassoon, an oompah tuba on the bass "
        "line, a clarinet, a glockenspiel and celesta, a muted trumpet, brushed snare and soft timpani, with a low "
        "electrical mains hum and an occasional short buzzing synth zap")

CUES = {
    "base": {
        "where": "the base game",
        "bpm": 104, "bars": 32, "head": None, "loop_from": 0, "game_lufs": -24.5,
        "prompt": (
            "Instrumental only. Key: D minor. Tempo: 104 BPM. " + NO_VOX +
            "A sneaky, tiptoeing dark-comedy groove for a cartoon slot game set in a blackout, 104 BPM, D minor, 4/4: "
            + BAND + ". Mischievous and a little sinister but silly, like cartoon characters creeping around a dark "
            "mansion with a candle; the pizzicato strings and bassoon play a catchy creeping riff over the tuba, the "
            "glockenspiel answers. Background music that can play for a long time: never busy or fatiguing, the "
            "groove steady throughout. Structure: [Short intro] -> [Main groove] -> [Main groove, clarinet and muted "
            "trumpet trading the riff] -> [Main groove]. No breakdown, no big ending, no fade-out."),
    },
    "menu": {
        "where": "the bonus buy menu",
        "bpm": 92, "bars": 16, "head": None, "loop_from": 0, "game_lufs": -27,
        "prompt": (
            "Instrumental only. Key: D minor. Tempo: 92 BPM. " + NO_VOX +
            "A slow, suspicious, hushed little vamp while deciding something in the dark: " + BAND + ", playing very "
            "softly. 92 BPM, D minor, 4/4. A soft tuba on every beat, quiet pizzicato strings, a sly clarinet melody, "
            "celesta twinkles, a brushed snare on 2 and 4. Calm and low energy at a rock-steady tempo, the same "
            "relaxed groove from start to finish: no build-ups, no rubato, no solo, no big ending, no fade-out."),
    },
    "intro": {
        "where": "the YOU WON n FREE SPINS screen (waits for a click)",
        "bpm": 132, "bars": 8, "head": 5.5, "tail": .6, "loop_from": 9, "game_lufs": -23.5,
        "prompt": (
            "Instrumental only. Key: A minor. Tempo: 132 BPM. " + NO_VOX +
            "A dramatic cartoon announcement for a bonus round when the power suddenly comes back on: 132 BPM, A minor, "
            "4/4. It opens instantly with a big hit - a timpani boom, a cymbal crash, a buzzing electric surge and the "
            "whole orchestra blasting a rising chord - then settles into an excited, pumping cartoon chase vamp that "
            "holds steady and keeps repeating: driving snare and timpani, a bouncing tuba, punchy pizzicato strings "
            "and muted-trumpet stabs, glockenspiel runs. Structure: [Big hit] -> [Steady pumping vamp, repeating]. "
            "No big drop, no ending, no fade-out."),
    },
    "bonus": {
        "where": "the free spins",
        "bpm": 132, "bars": 32, "head": None, "loop_from": 0, "game_lufs": -22,
        "prompt": (
            "Instrumental only. Key: A minor. Tempo: 132 BPM. " + NO_VOX +
            "A fast, frantic, funny cartoon chase for a slot game's free spins while sparks fly in a blackout: 132 BPM, "
            "A minor, 4/4: " + BAND + " at full tilt. Hard-driving snare and timpani, a pumping tuba line, the "
            "clarinet and muted trumpet playing a catchy hook in unison, racing pizzicato strings, buzzing electric "
            "zaps on the off-beats. Energetic and fun from the first bar: [Main section] -> [Main section, clarinet "
            "and trumpet trading licks] -> [Main section with variations] -> [Main section]. No intro, no breakdown, "
            "no ending, no fade-out."),
    },
    "total": {
        "where": "the bonus's TOTAL WIN screen (waits for a click)",
        "bpm": 120, "bars": 8, "start": 0, "head": 4.4, "tail": 1.2, "loop_from": 9, "game_lufs": -22.5,
        "prompt": (
            "Instrumental only. Key: D major. Tempo: 120 BPM. " + NO_VOX +
            "A triumphant, goofy cartoon finale celebrating a huge win as all the lights come back on: 120 BPM, "
            "D major, 4/4. It opens with a big celebratory hit - a timpani roll, a cymbal crash and the whole "
            "orchestra holding a bright major chord with a trumpet fanfare on top - then a joyful, bouncing victory "
            "march: " + BAND + ", playing a big happy tune over D - A - G - D. Uplifting, victorious and silly. "
            "Structure: [Celebration hit] -> [Joyful march, steady and repeating]. No breakdown, no ending, no "
            "fade-out."),
    },
}
