"""The base game's background: INSIDE a Nashville honky-tonk (owner, 2026-11-23: "make the background inside a nashville
bar ... not static, small visual animations / details, no people"; then "more appealing, more detailed and less
bland").

Same method as gen_bg_v2.py (a layout guide drawn in code, painted over by the image model, then one detail pass), so
the picture stays designed rather than chaotic. Version 2 of the room (art/broadway-src/bg4; the first, plainer one
is kept in bg3): the wall is three different surfaces instead of one brown plank wall - a deep-teal stage wall with gold
stars behind red curtains on the left (Rosie stands in front of the stage), exposed brick with the gold records and
hanging guitars in the middle (the board covers it), an ornate back-bar with teal back-lit bottle shelves on the right -
and the picture is LIT: coloured glows round every neon sign, pools of light and neon reflections on a dark polished
floor, shadow in the corners. NO people anywhere.
The things that MOVE are left out of the painting on purpose - frontend/bgscene.js draws them live over it: the
ceiling fans, the stage lights' beams, dust, glints on the bottles, steam off the coffee pot - and the neon signs and
bulbs flicker and chase from the "off" twin (bg_layers_bw.py).
  layout            art/broadway-src/bg4/layout_bar.png
  gen [n]           n takes painted over the guide               -> bg4/bar_<k>.png
  detail <k> [n]    the detail pass on take k                    -> bg4/bar_d<j>.png
  pick <file>       choose the painting                          -> bg4/bar_pick.png
  unlit / mobile    the lights-off twin / the 2:3 phone redraw   -> bg4/bar_unlit.png, bar_mobile.png
  install           copy the three into the pipeline's names (bg_v1, bg_unlit_v1, bg_mobile_v1) - then run
                    tools/broadway/bg_layers_bw.py
usage: python tools/broadway/gen_bg_bar.py layout|gen|detail|pick|unlit|mobile|install [...]"""
import math, os, shutil, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg

ROOT = orimg.ROOT
SRC = os.path.join(ROOT, "art", "broadway-src")
D = os.path.join(SRC, "bg4")
MODEL = "openai/gpt-image-2.6-sunburst"
W, H = 1536, 864
INK = (15, 15, 15)
STYLE = ("STYLE: a lush, professional interior background painting from a modern adult-animation TV series: clean, confident "
         "black line art of even weight and flat colour shapes, PLUS painted lighting - a soft coloured glow round every neon "
         "sign and bulb, pools of warm light on the walls and floor, neon colours reflected in the dark polished floor, deeper "
         "shadow in the corners and up under the ceiling, a gentle vignette. A warm, inviting, night-time bar mood with strong "
         "saturated colour accents (hot pink, electric blue, amber, red, teal) against deep browns and teal. RICH in "
         "deliberate set-dressing detail, but ORGANISED like a designed film set: every object sits in a clear place on a "
         "wall, shelf, counter or floor, shapes are crisp and readable, nothing floats, nothing is garbled, no random "
         "clutter. No glossy plastic 3D look, no photo-realism, no painterly smear. Consistent straight-on perspective.")
NOT = ("Do NOT draw: any people, figures, faces or silhouettes (the bar is EMPTY); any ceiling fan; any hanging pendant "
       "lamp; any wall clock; any light BEAMS from the stage lights (those are added later as animated pieces - draw the "
       "lamps themselves but not their beams). No brand names, no logos, no writing on bottles, posters or signs: the ONLY "
       "words in the whole picture are the three neon signs LIVE MUSIC, HONKY TONK and BAR.")


def star(d, cx, cy, r, fill, squash=1.0):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * .42
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * squash))
    d.polygon(pts, fill=fill, outline=INK)


def layout_bar():
    im = Image.new("RGB", (W, H), (60, 36, 26))
    d = ImageDraw.Draw(im)
    # ---- three wall surfaces
    d.rectangle([0, 70, 432, 600], fill=(22, 58, 74))                       # stage wall: deep teal
    for sx, sy in ((90, 260), (170, 420), (300, 300), (360, 470), (60, 480), (250, 520)):
        star(d, sx, sy, 16, (214, 170, 70))                                 # painted gold stars on it
    d.rectangle([432, 70, 1128, 600], fill=(132, 64, 48))                   # exposed brick
    for y in range(86, 480, 22):
        d.line([(432, y), (1128, y)], fill=(104, 48, 38), width=2)
    d.rectangle([1128, 70, W, 600], fill=(104, 64, 38))                     # wood panelling behind the bar
    d.rectangle([432, 486, 1128, 600], fill=(52, 34, 26), outline=INK, width=3)   # dark wainscot under the brick
    d.rectangle([0, 0, W, 70], fill=(34, 22, 18), outline=INK, width=3)     # ceiling with beams
    for x in range(120, W, 280):
        d.rectangle([x - 14, 0, x + 14, 70], fill=(24, 16, 12))
    # ---- floor: dark polished planks, neon reflections, an inlaid star in the dance floor
    d.rectangle([0, 600, W, H], fill=(78, 48, 32), outline=INK, width=3)
    for i in range(-7, 8):
        d.line([(W / 2 + i * 115, 600), (W / 2 + i * 250, H)], fill=(58, 34, 24), width=3)
    for x0, x1, col in ((90, 330, (60, 110, 190)), (430, 520, (190, 60, 130)), (660, 880, (200, 140, 50)), (1430, 1530, (190, 50, 50))):
        d.rectangle([x0, 612, x1, 700], fill=col)                           # where each sign's colour lies on the floor
    star(d, 768, 742, 120, (150, 100, 56), squash=.34)
    # ---- one string of warm bulbs under the ceiling
    for i in range(17):
        x = 30 + i * 92
        y = 86 + 20 * (1 - ((i % 8) / 3.5 - 1) ** 2)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(255, 222, 130), outline=INK)
    # ---- left: the stage
    d.polygon([(0, 70), (58, 70), (48, 600), (0, 600)], fill=(150, 26, 34), outline=INK)       # red curtain, left
    d.polygon([(388, 70), (432, 70), (432, 600), (398, 600)], fill=(150, 26, 34), outline=INK)  # red curtain, right
    d.polygon([(0, 600), (404, 600), (440, 652), (0, 652)], fill=(150, 104, 62), outline=INK)   # the riser's top
    d.rectangle([0, 652, 440, 690], fill=(70, 42, 28), outline=INK, width=3)                    # its front, with footlights
    for x in range(30, 430, 50):
        d.ellipse([x - 8, 660, x + 8, 676], fill=(255, 226, 140), outline=INK)
    d.ellipse([84, 478, 204, 598], fill=(240, 235, 220), outline=INK, width=4)                  # kick drum
    d.ellipse([56, 446, 124, 470], fill=(232, 190, 80), outline=INK, width=3)                   # cymbals
    d.ellipse([178, 436, 246, 460], fill=(232, 190, 80), outline=INK, width=3)
    d.rectangle([258, 470, 344, 598], fill=(34, 34, 40), outline=INK, width=4)                  # amp stack
    d.line([(372, 430), (372, 598)], fill=INK, width=5)                                         # mic stand
    for x, col in ((78, (255, 90, 170)), (372, (70, 170, 255))):                                # two stage lights on the ceiling
        d.polygon([(x - 22, 70), (x + 22, 70), (x + 30, 112), (x - 30, 112)], fill=(30, 30, 36), outline=INK)
        d.ellipse([x - 20, 100, x + 20, 122], fill=col, outline=INK)
    d.rectangle([84, 124, 352, 198], fill=(16, 22, 40), outline=(47, 168, 255), width=6)        # neon words: LIVE MUSIC (blue)
    # ---- middle: the brick wall the board covers
    d.rectangle([448, 176, 516, 430], fill=(30, 22, 34), outline=(255, 63, 164), width=6)       # a pink neon guitar
    d.rectangle([664, 98, 872, 168], fill=(30, 22, 30), outline=(255, 194, 58), width=6)        # neon words: HONKY TONK (amber)
    for cx in (620, 768, 916):                                                                  # three framed gold records
        d.rectangle([cx - 52, 204, cx + 52, 312], fill=(44, 30, 22), outline=INK, width=3)
        d.ellipse([cx - 38, 220, cx + 38, 296], fill=(232, 178, 58), outline=INK, width=2)
    for gx in (560, 990, 1060):                                                                 # guitars hung on the brick
        d.ellipse([gx - 26, 380, gx + 26, 450], fill=(190, 110, 50), outline=INK, width=3)
        d.rectangle([gx - 6, 300, gx + 6, 384], fill=(90, 56, 36), outline=INK)
    d.rectangle([640, 350, 900, 362], fill=(80, 50, 32), outline=INK, width=2)                  # a shelf of hats and boots
    for bx in (670, 730, 800, 860):
        d.rectangle([bx - 18, 318, bx + 18, 350], fill=(150, 96, 56), outline=INK)
    # ---- right: the bar
    d.rectangle([1140, 250, 1424, 486], fill=(70, 42, 28), outline=INK, width=4)                # an ornate wooden back-bar
    d.pieslice([1200, 206, 1364, 300], 180, 360, fill=(70, 42, 28), outline=INK, width=4)       # its arched crown
    for y0 in (350, 414):                                                                       # two back-lit shelves of bottles
        d.rectangle([1156, y0, 1408, y0 + 60], fill=(40, 150, 150), outline=INK, width=3)
        for k in range(10):
            col = [(60, 140, 90), (190, 120, 40), (150, 40, 40), (70, 110, 170), (200, 170, 60)][k % 5]
            d.rectangle([1168 + k * 24, y0 + 12, 1182 + k * 24, y0 + 58], fill=col, outline=INK)
    d.rectangle([1120, 488, 1450, 508], fill=(178, 128, 80), outline=INK, width=3)              # the counter's top
    d.rectangle([1130, 508, 1440, 600], fill=(96, 58, 36), outline=INK, width=3)                # its panelled front
    d.line([(1140, 580), (1430, 580)], fill=(214, 170, 70), width=6)                            # brass foot rail
    d.rectangle([1292, 452, 1322, 488], fill=(200, 200, 210), outline=INK, width=2)             # a coffee pot
    d.rectangle([1180, 446, 1230, 488], fill=(214, 170, 70), outline=INK, width=2)              # brass taps
    for sx in (1186, 1284, 1382):                                                               # three bar stools
        d.ellipse([sx - 32, 612, sx + 32, 634], fill=(150, 30, 36), outline=INK, width=3)
        d.rectangle([sx - 5, 634, sx + 5, 716], fill=(60, 38, 26))
    d.ellipse([1150, 720, 1420, 800], fill=(200, 170, 140), outline=INK, width=3)               # a cowhide rug
    d.rounded_rectangle([1450, 404, 1530, 644], radius=38, fill=(150, 62, 40), outline=INK, width=4)   # a jukebox
    d.arc([1460, 414, 1520, 500], 180, 360, fill=(255, 210, 90), width=8)
    d.rectangle([1464, 520, 1516, 604], fill=(240, 200, 120), outline=INK, width=2)
    d.rectangle([1440, 96, 1530, 290], fill=(30, 22, 30), outline=(255, 59, 59), width=6)       # a red neon cowboy boot
    d.rectangle([1440, 312, 1530, 372], fill=(20, 30, 30), outline=(60, 230, 190), width=6)     # neon word: BAR (teal)
    return im


PROMPT = ("A wide landscape background for a slot game, painted over the attached LAYOUT GUIDE: keep every block exactly "
          "where the guide puts it. Scene: the INSIDE of a classic honky-tonk bar on Lower Broadway in Nashville at night, "
          "EMPTY of people, seen straight on toward its back wall, richly dressed and beautifully lit. A dark beamed ceiling "
          "with one string of round warm party bulbs under it; a dark polished wooden floor that reflects the neon colours, "
          "with a big inlaid wooden star in the middle of the dance floor. "
          "LEFT - the stage: a low wooden stage with a row of small glowing footlights along its front edge, heavy red "
          "velvet curtains with gold tie-backs on both sides of it, a deep-teal back wall painted with gold stars, a red "
          "sparkle drum kit, a stack of guitar amplifiers, a microphone on a stand, and two stage lights fixed to the "
          "ceiling (one with a pink lens, one with a blue lens - no beams drawn). "
          "MIDDLE - an exposed red-brick wall over a dark wood wainscot (a slot board covers this part): three framed gold "
          "records in a row, acoustic and electric guitars hung on the brick, a wooden shelf with cowboy hats and boots. "
          "RIGHT - the bar: an ornate carved wooden back-bar with an arched crown and two shelves of coloured bottles back-lit "
          "in glowing teal, a polished counter with brass beer taps, a steel coffee pot and glasses, a carved panelled front "
          "with a brass foot rail, three red leather bar stools, a brown-and-white cowhide rug on the floor in front, and a "
          "classic jukebox with glowing coloured arched tubes at the far right. "
          "FIVE neon signs, exactly where the guide's coloured outlines are: the words LIVE MUSIC in electric-blue neon over "
          "the stage; a hot-pink neon guitar on the brick; the words HONKY TONK in amber neon above the gold records; a big "
          "red neon cowboy boot at the top right; the word BAR in teal neon under the boot. Each neon is a clean bright tube "
          "with a white core on a dark backing board and throws a soft glow of its colour on the wall round it. ")
DETAIL = ("Redraw the attached slot-game background with EXACTLY the same composition - every wall, the stage and its "
          "curtains, the drum kit and amplifiers, the gold records, the guitars, the back-bar and its bottles, the counter, "
          "the stools, the rug, the jukebox, the five neon signs, the bulbs, the ceiling and the floor exactly where they "
          "are - raised to the finish of a feature-quality animation background: crisper line art, richer and more "
          "beautiful lighting (soft neon glows, warm light pools, clear neon reflections in the polished floor, deeper "
          "shadow in the corners), and more fine, deliberate detail everywhere: mortar lines and a few chipped bricks, wood "
          "grain and carved trim on the back-bar, labels-free bottles of different shapes, glasses hanging in a rack, a tip "
          "jar and a bowl of peanuts on the counter, studs on the stool leathers, cables, a set list and a guitar on a stand "
          "on the stage, fringe on the curtains, a lucky horseshoe, a coiled lasso, a longhorn skull above the back-bar, "
          "small framed pictures of guitars and stars (no writing). Keep it organised and readable - no clutter, nothing "
          "floating - and keep the middle third the calmest part. ")
UNLIT = ("Redraw the attached picture EXACTLY - the same room, composition, shapes, outlines and every detail in the same "
         "place - but with EVERY electric light SWITCHED OFF: the neon tubes become dull unlit glass (greyish pastel "
         "versions of their colours, no white core, no glow), the party bulbs and the stage's footlights become pale grey "
         "unlit glass, the two stage lights' lenses go dark, the teal back-light behind the bottles goes dark, the "
         "jukebox's glowing tubes and panel go dark and dull, and every coloured glow, light pool and neon reflection they "
         "threw on the walls and floor is gone, leaving the room evenly and dimly lit. Everything else stays exactly as it "
         "is. No other changes.")
MOBILE = ("Redraw the attached slot game background as a TALL PORTRAIT picture (2:3) for phones: the same empty honky-tonk "
          "bar interior in the same richly lit animation style, colours and details, recomposed for a tall screen: the dark "
          "beamed ceiling and the string of party bulbs at the top; in the upper half the walls with the neon signs (LIVE "
          "MUSIC, the pink guitar, HONKY TONK, the red boot, BAR), the gold records and the hanging guitars; the stage with "
          "its red curtains and drum kit at the lower left, the bar with its back-lit bottles, stools and jukebox at the "
          "lower right; the dark polished floor with its neon reflections and inlaid star at the bottom. Soft pink and blue "
          "beams fall from the two stage lights. No extra signs, no other words, NO people, no ceiling fans, no hanging "
          "lamps, no clock.")
REFS_STYLE = ("\nThe second attached picture is the game's main character, only so the line weight and colours suit her - do "
              "NOT draw her (or anyone) in the scene.")


def call(out, prompt, refs, aspect="16:9"):
    try:
        _, c = orimg.generate(out, prompt, aspect=aspect, transparent=False, refs=refs, model=MODEL)
        return f"OK {os.path.basename(out)} {c}"
    except RuntimeError as e:
        return f"FAIL {os.path.basename(out)} {str(e)[:200]}"


if __name__ == "__main__":
    os.makedirs(D, exist_ok=True)
    cmd = sys.argv[1]
    rosie = os.path.join(SRC, "rosie2", "rosie_v2.png")
    pick = os.path.join(D, "bar_pick.png")
    if cmd == "layout":
        layout_bar().save(os.path.join(D, "layout_bar.png"))
        print("layout written")
    elif cmd == "gen":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        p = PROMPT + NOT + REFS_STYLE + "\n\n" + STYLE
        with ThreadPoolExecutor(4) as ex:
            for r in ex.map(lambda k: call(os.path.join(D, f"bar_{k}.png"), p, [os.path.join(D, "layout_bar.png"), rosie]),
                            range(1, n + 1)):
                print(r, flush=True)
    elif cmd == "detail":
        k = sys.argv[2]
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        p = DETAIL + NOT + "\n\n" + STYLE
        with ThreadPoolExecutor(4) as ex:
            for r in ex.map(lambda j: call(os.path.join(D, f"bar_d{j}.png"), p, [os.path.join(D, f"bar_{k}.png")]),
                            range(1, n + 1)):
                print(r, flush=True)
    elif cmd == "pick":
        shutil.copyfile(os.path.join(D, sys.argv[2]), pick)
        print("pick =", sys.argv[2])
    elif cmd == "unlit":
        print(call(os.path.join(D, "bar_unlit.png"), UNLIT, [pick]))
    elif cmd == "mobile":
        print(call(os.path.join(D, "bar_mobile.png"), MOBILE + "\n\n" + STYLE, [pick], aspect="2:3"))
    elif cmd == "install":
        for src, name in (("bar_pick.png", "bg_v1"), ("bar_unlit.png", "bg_unlit_v1"), ("bar_mobile.png", "bg_mobile_v1")):
            shutil.copyfile(os.path.join(D, src), os.path.join(SRC, name + ".png"))
            k4 = os.path.join(SRC, "4k", name + ".png")           # bg_layers_bw.py's enlarged copy is made again
            if os.path.exists(k4):
                os.remove(k4)
        print("installed: now run tools/broadway/bg_layers_bw.py")
