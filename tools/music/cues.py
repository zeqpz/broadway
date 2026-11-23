"""The game's five music cues: where each plays, what Lyria is asked for, and how build.py cuts it.

Broadway on Nashville (2026-11-22): Lower Broadway at night, honky-tonks and neon. Every cue is INSTRUMENTAL
honky-tonk / modern country: a twangy Telecaster, pedal steel, upright or electric bass, brushed or shuffle drums,
fiddle, banjo and a honky-tonk piano. G major for the base game, the menu and the TOTAL WIN; D major (its dominant)
for the free spins' intro and the free spins, which share a tempo so the bonus drops in on the intro's beat. Lyria takes
the tempo but not the key: keep takes for their key (tools/music/keys.py). No vocals anywhere, and no tune is a real
song's.

  bars       the loop's length in bars (4/4)
  head       None: the cue is only the loop. A number: the take's opening plays once and the loop
             starts that many seconds in (snapped to the take's beat), cut from wherever after
             loop_from fits best; the opening keeps ringing under it for `tail` seconds (default 2)
  start      seconds cut off the take's front before anything else (head and loop_from count from there)
  loop_from  seconds into the take before which no loop may start (past its intro)
  game_lufs  how loud the cue should sit in the game (the music bar at 100); sets its MUSIC level
"""

NO_VOX = ("Strictly instrumental: no vocals, no singing, no humming, no yodeling, no shouts, no whoops, no chants, "
          "no spoken words. ")
BAND = ("a tight Nashville honky-tonk band: a twangy Telecaster electric guitar, a crying pedal steel guitar, a fiddle, "
        "a banjo, a rolling honky-tonk upright piano, a walking upright bass and a shuffle drum kit")

CUES = {
    "base": {
        "where": "the base game",
        "bpm": 112, "bars": 32, "head": None, "loop_from": 0, "game_lufs": -24.5,
        "prompt": (
            "Instrumental only. Key: G major. Tempo: 112 BPM. " + NO_VOX +
            "An upbeat, feel-good mid-tempo honky-tonk shuffle for a cartoon slot game set on a neon-lit city street of "
            "country music halls at night, 112 BPM, G major, 4/4 with a swinging shuffle feel: " + BAND + ". A "
            "brushed shuffle beat and a walking bass under a catchy twangy Telecaster riff; the pedal steel and the "
            "fiddle answer it, the honky-tonk piano rolls fills between phrases. Fun, warm and toe-tapping but never "
            "busy or fatiguing, so it can play for a long time; the groove steady throughout. Structure: [Short intro] "
            "-> [Main groove] -> [Main groove, fiddle and pedal steel trading the riff] -> [Main groove, piano fills]. "
            "No breakdown, no big ending, no fade-out."),
    },
    "menu": {
        "where": "the bonus buy menu",
        "bpm": 88, "bars": 16, "head": None, "loop_from": 0, "game_lufs": -27,
        "prompt": (
            "Instrumental only. Key: G major. Tempo: 88 BPM. " + NO_VOX +
            "A relaxed, laid-back country groove, like a late-night jam on a porch after the show: 88 BPM, G major, "
            "4/4. Soft brushed drums on 2 and 4, a mellow upright bass, gentle clean Telecaster licks, slow lazy pedal "
            "steel swells and quiet honky-tonk piano chords. Calm and low energy at a rock-steady tempo, the same easy "
            "groove from start to finish: no build-ups, no rubato, no solo, no big ending, no fade-out."),
    },
    "intro": {
        "where": "the YOU WON n FREE SPINS screen (waits for a click)",
        "bpm": 150, "bars": 8, "start": .2, "head": 4.95, "tail": .6, "loop_from": 8, "game_lufs": -23.5,
        "prompt": (
            "Instrumental only. Key: D major. Tempo: 150 BPM. " + NO_VOX +
            "A short, punchy country-rock build announcing a bonus round on a big stage: 150 BPM, D major, 4/4. It "
            "opens instantly with a hard hit - a crash cymbal, a big twangy electric guitar chord and a pedal steel "
            "swell - then a quick rising build of snare and fiddle into an excited, driving country vamp that holds "
            "steady and keeps repeating: a pounding train beat on the snare, a bouncing bass, choppy Telecaster "
            "chords, banjo rolls and fiddle stabs. Structure: [Big hit] -> [Quick build] -> [Steady driving vamp, "
            "repeating]. No big drop, no ending, no fade-out."),
    },
    "bonus": {
        "where": "the free spins",
        "bpm": 150, "bars": 32, "head": None, "loop_from": 0, "game_lufs": -22,
        "prompt": (
            "Instrumental only. Key: D major. Tempo: 150 BPM. " + NO_VOX +
            "A fast, high-energy country-rock and bluegrass burner for a slot game's free spins: 150 BPM, D major, 4/4: "
            + BAND + " at full tilt. A driving train beat on the snare, a fast thumping bass, blazing chicken-picking "
            "Telecaster licks, a racing banjo roll, a hot fiddle hook and pounding honky-tonk piano. Energetic and fun "
            "from the first bar: [Main section] -> [Main section, fiddle and Telecaster trading hot licks] -> [Main "
            "section, banjo and piano breaks] -> [Main section]. No intro, no breakdown, no ending, no fade-out."),
    },
    "total": {
        "where": "the bonus's TOTAL WIN screen (waits for a click)",
        "bpm": 124, "bars": 8, "start": .25, "head": 4.1, "tail": 1.2, "loop_from": 9, "game_lufs": -22.5,
        "prompt": (
            "Instrumental only. Key: G major. Tempo: 124 BPM. " + NO_VOX +
            "A triumphant, big country finish celebrating a huge win on a big stage: 124 BPM, G major, 4/4. It opens "
            "with a big celebratory hit - a drum roll, a crash cymbal and the whole band ringing out one bright major "
            "chord with a soaring pedal steel and a twangy guitar flourish on top - then a joyful, stomping victory "
            "groove: " + BAND + ", playing a big happy hook over G - C - D - G. Uplifting, proud and fun. Structure: "
            "[Celebration hit] -> [Joyful stomping groove, steady and repeating]. No breakdown, no ending, no fade-out."),
    },
}
