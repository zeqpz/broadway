"""Broadway on Nashville: the engine.io lobby art. NO text, letters or logos on any of it (owner rule; Engine draws the
title itself in the Media Editor).
  covers  media/cover_16x9.png (3840 x 2160) and media/cover_3x4.png (3072 x 4096): The Crooner singing on the bar's stage, the
          bachelorette and the fiddler beside him, gold records in the air (the image model, refs = the bar, three symbols),
          enlarged x4 (Real-ESRGAN)
  tiles   Engine's Media Editor wants SEPARATE layers (review of Power Outage, 2026-11-19):
          media/tiles/bg_16x9.png (3840 x 2160), bg_3x4.png (2400 x 3200) - the bar with no people, BRIGHT (the editor
          warns under ~40 % perceived brightness) - and fg_crooner.png: The Crooner symbol, transparent
          (no cowgirl: the owner took her out of the game, 2026-11-24)
usage: python tools/broadway/gen_media_bw.py gen [cover16,cover34,bg16,bg34] | build | check"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageStat
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orimg

ROOT = orimg.ROOT
SRC = os.path.join(ROOT, "art", "broadway-src")
RAW = os.path.join(SRC, "media")
MEDIA = os.path.join(ROOT, "media")
MODEL = "openai/gpt-image-2.6-sunburst"
NOTEXT = ("NO text, NO letters, NO numbers, NO words, NO logo anywhere in the picture - the neon signs in the scene show "
          "only shapes and pictures (a boot, a guitar, a star, a horseshoe, a cowboy hat), never words.")
STYLE = ("Drawn in exactly the attached pictures' clean adult-animation TV style: uniform black line weight, flat matte "
         "colours with one hard shade, few highlights, no glossy shine, calm and well designed, no clutter, no realistic "
         "lighting, no blur, no texture noise.")
COVER = ("A slot game's lobby cover illustration, set INSIDE a Nashville honky-tonk bar at night (the first attached "
         "picture: a small stage with a teal star backdrop and red curtains, a brick wall with glowing neon shapes, a "
         "carved back-bar with teal-lit bottle shelves, a polished floor mirroring the neon). On the stage, big in the "
         "centre, THE CROONER from the second attached picture - exactly him - sings into his vintage microphone under "
         "a pink and a blue stage light, one arm thrown wide; the bachelorette and the old fiddler from the other "
         "attached pictures whoop and play beside him, smaller. Gold records spin through the air with music notes and "
         "gold stars, a red rhinestone cowboy boot and a banjo among them. Bright, vibrant, joyful, poster-like "
         "composition. NO cowgirl, NO guitarist woman. ")
STREET = ("A lobby-tile BACKGROUND (environment only - NO people, NO characters, NO faces) for a slot game: the attached "
          "honky-tonk bar interior, redrawn BRIGHT and VIBRANT like a candy-coloured cartoon poster: the stage with its "
          "teal star backdrop and red curtains, warm brick, every neon shape blazing in hot pink, electric blue, gold "
          "and green, strings of party bulbs, the back-bar's teal-lit bottle shelves, a glossy floor reflecting the "
          "neon. High-key and saturated: every area clearly lit and colourful, NO large dark areas, NO heavy vignette. "
          "Keep the middle calm (a character will stand there). ")
NOTEXT = ("NO text, NO letters, NO numbers, NO words, NO logo anywhere in the picture - every neon sign shows only a "
          "shape or picture (a boot, a guitar, a star, a horseshoe, a cowboy hat), never words.")
JOBS = {   # job: (prompt, aspect, refs)
    "cover16": (COVER + NOTEXT + " " + STYLE, "16:9", ["bg_v1.png", "H1_v2.png", "H2_v2.png", "H3_v2.png"]),
    "cover34": (COVER + NOTEXT + " " + STYLE, "3:4", ["bg_mobile_v1.png", "H1_v2.png", "H2_v2.png", "H3_v2.png"]),
    "bg16": (STREET + NOTEXT + " " + STYLE, "16:9", ["bg_v1.png"]),
    "bg34": (STREET + NOTEXT + " " + STYLE, "3:4", ["bg_mobile_v1.png"]),
}
BOOTS_NOTE = ""


def gen(job):
    p, aspect, refs = JOBS[job]
    if job.startswith("cover"):
        p += BOOTS_NOTE
    try:
        _, c = orimg.generate(os.path.join(RAW, job + ".png"), p, aspect=aspect, transparent=False,
                              refs=[os.path.join(SRC, r) for r in refs], model=MODEL)
        return f"OK {job} {c}"
    except RuntimeError as e:
        return f"FAIL {job} {e}"


def brightness(im):
    g = im.convert("L").resize((256, 256))
    return ImageStat.Stat(g).mean[0] / 255


def fg_crooner():
    """The tile's foreground element: The Crooner (H1), the game's top symbol, transparent, 2048 px tall."""
    im = Image.open(os.path.join(SRC, "H1_v2.png")).convert("RGBA")
    im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
    import upscale4k
    k = 2048 / im.height
    return upscale4k.up4(im, (round(im.width * k), 2048), model="realesrgan-x4plus-anime")


def build():
    import upscale4k
    os.makedirs(os.path.join(MEDIA, "tiles"), exist_ok=True)
    for job, out, size in (("cover16", "cover_16x9.png", (3840, 2160)), ("cover34", "cover_3x4.png", (3072, 4096)),
                           ("bg16", "tiles/bg_16x9.png", (3840, 2160)), ("bg34", "tiles/bg_3x4.png", (2400, 3200))):
        p = os.path.join(RAW, job + ".png")
        if not os.path.exists(p):
            print("missing", job); continue
        im = upscale4k.up4(Image.open(p).convert("RGBA"), size, model="realesrgan-x4plus-anime").convert("RGB")
        im.save(os.path.join(MEDIA, out))
        if job.startswith("cover"):
            im.save(os.path.join(MEDIA, out.replace(".png", ".jpg")), quality=90)
        print("wrote", out, im.size, f"brightness {brightness(im):.0%}")
    for old in ("fg_president.png", "fg_rosie.png"):
        if os.path.exists(os.path.join(MEDIA, "tiles", old)):
            os.remove(os.path.join(MEDIA, "tiles", old))
    fg_crooner().save(os.path.join(MEDIA, "tiles", "fg_crooner.png"))
    print("wrote tiles/fg_crooner.png")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    os.makedirs(RAW, exist_ok=True)
    if cmd == "gen":
        names = sys.argv[2].split(",") if len(sys.argv) > 2 else list(JOBS)
        with ThreadPoolExecutor(4) as ex:
            for r in ex.map(gen, names):
                print(r, flush=True)
    elif cmd == "build":
        build()
    else:
        for f in ("tiles/bg_16x9.png", "tiles/bg_3x4.png"):
            print(f, f"{brightness(Image.open(os.path.join(MEDIA, f))):.0%}")
