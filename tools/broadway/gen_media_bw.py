"""Broadway on Nashville: the engine.io lobby art. NO text, letters or logos on any of it (owner rule; Engine draws the
title itself in the Media Editor).
  covers  media/cover_16x9.png (3840 x 2160) and media/cover_3x4.png (3072 x 4096): Rosie rocking out on Lower Broadway
          at night, a few of the game's symbols round her (the image model, refs = her figure, the street, two symbols),
          enlarged x4 (Real-ESRGAN)
  tiles   Engine's Media Editor wants SEPARATE layers (review of Power Outage, 2026-11-19):
          media/tiles/bg_16x9.png (3840 x 2160), bg_3x4.png (2400 x 3200) - the street with no people, BRIGHT (the editor
          warns under ~40 % perceived brightness) - and fg_rosie.png: Rosie herself, transparent, cut from her rig's parts
          (no image model: exactly the character in the game)
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
COVER = ("A slot game's lobby cover illustration: ROSIE - the cowgirl in the first attached picture, exactly her (blue "
         "cowboy hat with a white star, auburn curls, royal-blue fringed western shirt, short red skirt, red cowboy boots "
         "with a white star on a blue medallion, her red electric guitar with rose decals) - rocking out mid-strum, big "
         "confident smile, one boot kicked up, standing in the middle of LOWER BROADWAY in Nashville at night (the second "
         "attached picture: brick honky-tonks covered in glowing neon signs, marquee bulbs, party lights strung over the "
         "street). Gold records spin through the air around her with music notes and gold stars, and the bachelorette "
         "and the old fiddler from the other attached pictures cheer her on from the sidewalk, smaller. Bright, vibrant, "
         "joyful, poster-like composition with Rosie big in the centre. ")
STREET = ("A lobby-tile BACKGROUND (environment only - NO people, NO characters, NO faces) for a slot game: the attached "
          "Lower Broadway street of honky-tonks, redrawn BRIGHT and VIBRANT like a candy-coloured cartoon poster at a "
          "glowing purple-and-pink dusk: a bright violet-to-peach sky with the first stars, every neon sign blazing in "
          "hot pink, electric blue, gold and green, warm amber windows, strings of party lights, bright brick colours, a "
          "glossy street reflecting the neon. High-key and saturated: every area clearly lit and colourful, NO large "
          "dark areas, NO heavy vignette. Keep the middle calm (a character will stand there). ")
JOBS = {   # job: (prompt, aspect, refs)
    "cover16": (COVER + NOTEXT + "\n" + STYLE, "16:9", ["rosie2/rosie_v2.png", "bg_v1.png", "H2_v1.png", "H3_v1.png"]),
    "cover34": (COVER + NOTEXT + "\n" + STYLE, "3:4", ["rosie2/rosie_v2.png", "bg_mobile_v1.png", "H2_v1.png", "H3_v1.png"]),
    "bg16": (STREET + NOTEXT + "\n" + STYLE, "16:9", ["bg_v1.png"]),
    "bg34": (STREET + NOTEXT + "\n" + STYLE, "3:4", ["bg_mobile_v1.png"]),
}
BOOTS_NOTE = (" She is slim, in her tight fitted blue western shirt and tight red mini skirt; her boots are red with a white "
              "star on a round blue medallion.")


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


def fg_rosie():
    """Rosie at rest from her rig's parts (the same assembly the game shows), trimmed, 2048 px tall."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import rosie_parts as R
    fig = R.figure()
    bb = fig.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    fig = fig.crop(bb)
    k = 2048 / fig.height
    return fig.convert("RGBa").resize((round(fig.width * k), 2048), Image.LANCZOS).convert("RGBA")


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
    old = os.path.join(MEDIA, "tiles", "fg_president.png")
    if os.path.exists(old):
        os.remove(old)                                     # Power Outage's foreground
    fg_rosie().save(os.path.join(MEDIA, "tiles", "fg_rosie.png"))
    print("wrote tiles/fg_rosie.png")


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
