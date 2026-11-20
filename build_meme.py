"""Build the gta6-meme-x-01 meme: composite the make.fun ghost into the Vice
City background and render the caption with Pillow.

Layout of this repository:
  assets/bg.jpg        AI-generated Vice City street, text-free on purpose
  assets/ghost-raw.png the ghost group from make.fun's press-kit mark.svg,
                       rendered with headless Chromium (assets/ghost.html)
                       on a green screen
  assets/mark-1024.png the press-kit mark itself, for reference
  build_meme.py        this script
  meme.png             the meme (1080x1080), written by this script

Run:  python3 build_meme.py        (needs Pillow and numpy)
Outputs are written next to this script: meme.png (1080x1080, the meme) and
meme-480.png (480x480, the size the judge sees).
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(HERE, "assets", "bg.jpg")
GHOST_RAW = os.path.join(HERE, "assets", "ghost-raw.png")
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

CANVAS = 1080
MAGENTA = (196, 28, 131)
DARK = (25, 20, 25)


def extract_ghost(raw_path):
    """Chroma-key the green screen out of the rendered ghost.

    The render holds only the ghost group from the press-kit SVG: white body,
    sparkle eyes, magenta star coin. Green excess gives the alpha channel;
    the green is then divided back out of the colour channels so no green
    fringe survives on the edges.
    """
    import numpy as np
    raw = Image.open(raw_path).convert("RGB")
    a = np.asarray(raw).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    excess = g - np.maximum(r, b)
    alpha = np.clip(255.0 - excess, 0, 255)
    af = np.maximum(alpha, 1.0) / 255.0
    out_r = np.clip(r / af, 0, 255)
    out_g = np.clip((g - (1 - af) * 255.0) / af, 0, 255)
    out_b = np.clip(b / af, 0, 255)
    rgba = np.dstack([out_r, out_g, out_b, alpha]).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA")
    bbox = im.getchannel("A").getbbox()
    return im.crop(bbox)


def fit_font(text, max_width, start_size):
    size = start_size
    while size > 20:
        f = ImageFont.truetype(FONT_BOLD, size)
        if f.getlength(text) <= max_width:
            return f
        size -= 4
    return ImageFont.truetype(FONT_BOLD, 20)


def draw_text_block(draw, lines, y_top, max_width, start_size,
                    fill=(255, 255, 255)):
    """Draw centred lines over a soft dark backing band. Returns bottom y."""
    fonts = [fit_font(t, max_width, start_size) for t in lines]
    line_h = max(f.size for f in fonts)
    gap = int(line_h * 0.12)
    total_h = len(lines) * line_h + (len(lines) - 1) * gap
    band = Image.new("RGBA", (CANVAS, total_h + 36), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.rounded_rectangle([14, 0, CANVAS - 14, total_h + 36], radius=28,
                         fill=(10, 8, 12, 110))
    base = draw._image
    base.paste(band, (0, y_top - 18), band)
    y = y_top
    for text, font in zip(lines, fonts):
        w = font.getlength(text)
        x = (CANVAS - w) / 2
        draw.text((x, y), text, font=font, fill=fill,
                  stroke_width=max(3, font.size // 14), stroke_fill=DARK)
        y += line_h + gap
    return y_top + total_h


def main():
    bg = Image.open(BG).convert("RGB").resize((CANVAS, CANVAS), Image.LANCZOS)
    ghost = extract_ghost(GHOST_RAW)
    print("ghost extracted:", ghost.size)

    # Ghost: standing in the middle of the street, ~430px tall, next to the
    # pink convertible on the right.
    gh = 430
    gw = int(ghost.width * gh / ghost.height)
    ghost = ghost.resize((gw, gh), Image.LANCZOS)
    gx = (CANVAS - gw) // 2
    gy = 392

    # soft contact shadow under the ghost, so it stands on the road
    shadow = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([gx + 20, gy + gh - 28, gx + gw - 20, gy + gh + 6],
               fill=(0, 0, 0, 130))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    bg = bg.convert("RGBA")
    bg.paste(shadow, (0, 0), shadow)
    bg.paste(ghost, (gx, gy), ghost)

    draw = ImageDraw.Draw(bg)
    # Top headline over the sky.
    draw_text_block(draw, ["WAITED 13 YEARS", "FOR GTA 6."],
                    64, 960, 96)
    # Bottom punchline over the road.
    draw_text_block(draw, ["MY AI AGENT MADE THIS MEME",
                           "IN 13 SECONDS \u2014 AND GOT PAID."],
                    836, 1000, 58)
    # Brand pill.
    pill_font = ImageFont.truetype(FONT_BOLD, 46)
    label = "\u2605 make.fun"
    tw = pill_font.getlength(label)
    px0 = int((CANVAS - tw) / 2 - 34)
    py0, py1 = 978, 1040
    pill = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle([px0, py0, px0 + tw + 68, py1], radius=31,
                         fill=MAGENTA + (255,))
    pd.text((px0 + 34, py0 + 8), label, font=pill_font, fill=(255, 255, 255))
    bg.paste(pill, (0, 0), pill)

    bg.convert("RGB").save(os.path.join(HERE, "meme.png"))
    bg.convert("RGB").resize((480, 480), Image.LANCZOS).save(
        os.path.join(HERE, "meme-480.png"))
    print("wrote meme.png and meme-480.png")


if __name__ == "__main__":
    main()
