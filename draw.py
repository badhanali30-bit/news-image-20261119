#!/usr/bin/env python3
"""Draw the news-image-20261119 entry: a newspaper front page summing up
Thursday 19 November 2026. All eight stories are real events verified
from live news reporting that day. Deterministic: fixed content, no
timestamps, no randomness — running it twice yields byte-identical
entry.png.

Usage: python3 draw.py   (writes entry.png next to this script)
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# --- palette ----------------------------------------------------------------
PAPER = (250, 246, 236)      # newsprint cream
INK = (22, 22, 22)
RED = (176, 32, 32)
NAVY = (24, 42, 76)
BLUE = (52, 110, 176)
SKY = (208, 226, 242)
GREY = (105, 105, 98)
RULE = (22, 22, 22)
CARD = (255, 255, 255)
GOLD = (214, 138, 32)
GREEN = (46, 125, 50)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_B = f"{FONT_DIR}/noto/NotoSerif-Bold.ttf"
SANS_B = f"{FONT_DIR}/noto/NotoSans-Bold.ttf"
SANS_R = f"{FONT_DIR}/noto/NotoSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_width):
    """Greedy word wrap; returns lines that fit max_width."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if d.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, x, y, lines, fnt, fill, leading):
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(d, x0, x1, y, width=2, fill=RULE):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


# --- pictograms (flat vector style, drawn with PIL) -------------------------

def icon_summit(d, x, y, s):
    """Three flags on poles above a round table: the trilateral summit."""
    w, h = s, int(s * 0.66)
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    for i, col in enumerate((RED, GOLD, GREEN)):
        px = x + 28 + i * (w // 3)
        d.line([(px, y + 14), (px, y + h - 52)], fill=INK, width=3)
        d.polygon([(px, y + 14), (px + 62, y + 26), (px, y + 38)], fill=col)
    d.ellipse([x + w // 2 - 78, y + h - 48, x + w // 2 + 78, y + h - 16],
              fill=NAVY)


def icon_scales(d, x, y, s):
    """Balanced scales of justice: the ICJ ruling."""
    d.rectangle([x, y, x + s, y + s], fill=SKY)
    cx = x + s // 2
    d.line([(cx, y + 8), (cx, y + s - 10)], fill=INK, width=3)
    d.line([(x + 10, y + 16), (x + s - 10, y + 16)], fill=INK, width=3)
    d.ellipse([cx - 4, y + 4, cx + 4, y + 12], fill=GOLD)
    for sx in (x + 10, x + s - 10):
        d.line([(sx, y + 16), (sx, y + 30)], fill=INK, width=2)
        d.polygon([(sx - 12, y + 30), (sx + 12, y + 30), (sx, y + 42)],
                  fill=NAVY)
    d.line([(x + 8, y + s - 10), (x + s - 8, y + s - 10)], fill=INK,
           width=4)


def icon_chart(d, x, y, s):
    """Rising bar chart with an arrow: the IPO debut."""
    d.rectangle([x, y, x + s, y + s], fill=SKY)
    base = y + s - 12
    bars = [(x + 8, 14), (x + 22, 24), (x + 36, 34)]
    for bx, bh in bars:
        d.rectangle([bx, base - bh, bx + 10, base], fill=BLUE)
    d.line([(x + 8, base - 14), (x + s - 8, y + 8)], fill=RED, width=3)
    d.polygon([(x + s - 8, y + 8), (x + s - 18, y + 8), (x + s - 8, y + 18)],
              fill=RED)
    d.line([(x + 6, base), (x + s - 6, base)], fill=INK, width=2)


def icon_controller(d, x, y, s):
    """A game controller: the GTA VI launch."""
    d.rectangle([x, y, x + s, y + s], fill=SKY)
    cx, cy = x + s // 2, y + s // 2
    d.rounded_rectangle([cx - 24, cy - 14, cx + 24, cy + 14], radius=10,
                        fill=NAVY)
    d.ellipse([cx - 26, cy + 2, cx - 12, cy + 16], fill=NAVY)
    d.ellipse([cx + 12, cy + 2, cx + 26, cy + 16], fill=NAVY)
    # d-pad
    d.line([(cx - 15, cy - 2), (cx - 15, cy + 6)], fill=(255, 255, 255),
           width=3)
    d.line([(cx - 19, cy + 2), (cx - 11, cy + 2)], fill=(255, 255, 255),
           width=3)
    # buttons
    for bx, by in ((cx + 10, cy - 6), (cx + 17, cy + 1), (cx + 10, cy + 8)):
        d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=GOLD)


def icon_probe(d, x, y, s):
    """A deep-space probe with a dish and a star field: Voyager 1."""
    d.rectangle([x, y, x + s, y + s], fill=NAVY)
    # stars
    for sx, sy in ((8, 10), (44, 6), (20, 20), (50, 26), (12, 38)):
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                  fill=(255, 255, 255))
    cx, cy = x + s // 2, y + s // 2 + 2
    # dish
    d.polygon([(cx - 16, cy - 18), (cx + 16, cy - 18), (cx, cy - 2)],
              fill=(255, 255, 255))
    # body and boom
    d.rectangle([cx - 10, cy - 2, cx + 10, cy + 8], fill=GOLD)
    d.line([(cx + 10, cy + 3), (cx + 24, cy + 3)], fill=(255, 255, 255),
           width=2)
    d.ellipse([cx + 22, cy - 1, cx + 30, cy + 7], fill=RED)


def icon_flame(d, x, y, s):
    """A flame over a rooftop: the Bangladesh unrest."""
    d.rectangle([x, y, x + s, y + s], fill=SKY)
    cx = x + s // 2
    base = y + s - 8
    # rooftop
    d.rectangle([x + 8, base - 12, x + s - 8, base], fill=NAVY)
    d.polygon([(x + 8, base - 12), (cx, base - 24), (x + s - 8, base - 12)],
              fill=NAVY)
    # flame
    d.polygon([(cx, y + 8), (cx + 12, y + 26), (cx + 6, y + 34),
               (cx - 4, y + 34), (cx - 12, y + 26)], fill=RED)
    d.polygon([(cx, y + 22), (cx + 6, y + 32), (cx - 6, y + 32)],
              fill=GOLD)


def icon_tower(d, x, y, s):
    """A tall skyscraper with a red impact burst: the Riyadh attack."""
    d.rectangle([x, y, x + s, y + s], fill=SKY)
    cx = x + s // 2
    # tower
    d.rectangle([cx - 12, y + 14, cx + 12, y + s - 8], fill=NAVY)
    for wy in range(y + 20, y + s - 12, 8):
        d.line([(cx - 8, wy), (cx + 8, wy)], fill=(255, 255, 255), width=2)
    # impact burst at the top
    bx, by = cx, y + 10
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([(bx, by), (bx + int(10 * math.cos(a)),
                           by + int(10 * math.sin(a)))], fill=RED, width=3)
    d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=RED)


def icon_bridge(d, x, y, s):
    """A bridge with a red blast below its deck: the Crimea strike."""
    d.rectangle([x, y, x + s, y + s], fill=SKY)
    # deck
    d.line([(x + 4, y + 22), (x + s - 4, y + 22)], fill=NAVY, width=4)
    # arch
    d.arc([x + 6, y + 22, x + s - 6, y + s - 6], 180, 360, fill=NAVY,
          width=3)
    # pillars
    for px in (x + 12, x + s - 16):
        d.line([(px, y + 22), (px, y + s - 8)], fill=NAVY, width=3)
    # blast burst under the deck
    bx, by = x + s // 2, y + 34
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([(bx, by), (bx + int(9 * math.cos(a)),
                           by + int(9 * math.sin(a)))], fill=RED, width=3)
    d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=GOLD)


ICONS = {
    "summit": icon_summit,
    "scales": icon_scales,
    "chart": icon_chart,
    "controller": icon_controller,
    "probe": icon_probe,
    "flame": icon_flame,
    "tower": icon_tower,
    "bridge": icon_bridge,
}

# --- stories (all verified events of Thursday 19 November 2026) -----------
LEAD = (
    "LEAD STORY  •  SHENZHEN SUMMIT",
    "Trump, Xi and Putin hold first three-way talks",
    "A first-ever trilateral summit at the APEC meeting in Shenzhen: "
    "nuclear arms, Ukraine and Iran on the agenda — and a joint "
    "\u201cpeace declaration\u201d.",
    "summit",
)

STORIES = [
    ("WORLD COURT", "Myanmar committed genocide, court rules",
     "The ICJ finds Myanmar committed genocide against the Rohingya "
     "— the first time it has held a state responsible for genocide.",
     "scales"),
    ("MARKETS", "Anthropic starts trading on Nasdaq",
     "The Claude maker begins trading as ANT after pricing its IPO "
     "at $83 a share.",
     "chart"),
    ("CULTURE", "GTA VI launches worldwide",
     "Rockstar's Grand Theft Auto VI arrives after a 13-year wait, "
     "to rave reviews.",
     "controller"),
    ("SPACE", "Voyager 1 is one light-day away",
     "NASA confirms the probe is 26 billion km out — the first "
     "human-made object to reach the mark.",
     "probe"),
    ("BANGLADESH", "Shutdown brings violence to Bangladesh",
     "Awami League protests turn violent; Yunus's home is set "
     "ablaze and paramilitary troops are deployed.",
     "flame"),
    ("RIYADH", "Houthi attack damages Riyadh tower",
     "Saudi Arabia's tallest building, home to its sovereign wealth "
     "fund, is hit in a Houthi attack.",
     "tower"),
    ("UKRAINE", "Ukraine hits Crimean Bridge again",
     "Russia says Ukraine struck the bridge linking it to Crimea "
     "for a third time this week.",
     "bridge"),
]

NUMBERS = [("3", "leaders at the\nfirst summit"),
           ("9–6", "ICJ vote\nfinding genocide"),
           ("$83", "Anthropic IPO\nprice per share"),
           ("26bn km", "Voyager 1\nfrom Earth")]


# --- page -------------------------------------------------------------------
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 44
    CW = W - 2 * MX

    # outer double frame
    d.rectangle([16, 16, W - 17, H - 17], outline=RULE, width=3)
    d.rectangle([22, 22, W - 23, H - 23], outline=RULE, width=1)

    # masthead
    f_mast = font(SERIF_B, 74)
    title = "THE WORLD TODAY"
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 32), title, font=f_mast, fill=INK)
    f_tag = font(SANS_B, 17)
    tag = "ONE DAY  •  ONE PAGE  •  THE WORLD IN BRIEF"
    tw = d.textlength(tag, font=f_tag)
    d.text(((W - tw) / 2, 118), tag, font=f_tag, fill=GREY)
    rule(d, MX, W - MX, 148, width=3)

    # date band
    d.rectangle([MX, 160, W - MX, 208], fill=NAVY)
    f_date = font(SANS_B, 36)
    date = "THURSDAY 19 NOVEMBER 2026"
    tw = d.textlength(date, font=f_date)
    d.text(((W - tw) / 2, 169), date, font=f_date, fill=(255, 255, 255))

    # ---- lead story ------------------------------------------------------
    ly0, ly1 = 222, 462
    d.rectangle([MX, ly0, W - MX, ly1], fill=CARD, outline=RULE, width=2)
    f_kick = font(SANS_B, 19)
    d.text((MX + 22, ly0 + 14), LEAD[0], font=f_kick, fill=RED)
    f_lead = font(SANS_B, 36)
    lines = wrap(d, LEAD[1], f_lead, 556)
    y = draw_lines(d, MX + 22, ly0 + 46, lines, f_lead, INK, 44)
    f_sum = font(SANS_R, 22)
    lines = wrap(d, LEAD[2], f_sum, 556)
    draw_lines(d, MX + 22, y + 12, lines, f_sum, INK, 28)
    px, py, ps = W - MX - 22 - 300, ly0 + 16, 300
    ICONS[LEAD[3]](d, px, py, ps)
    d.rectangle([px, py, px + ps, py + int(ps * 0.66)], outline=RULE,
                width=2)

    # ---- story grid: 2 columns x 4 rows ----------------------------------
    gx, gy = MX, 474
    cell_w, cell_h = (CW - 16) // 2, 118
    f_k = font(SANS_B, 15)
    f_h = font(SANS_B, 21)
    f_s = font(SANS_R, 16)

    cells = list(STORIES) + [None]  # last cell = numbers box
    for idx, story in enumerate(cells):
        col, row = idx % 2, idx // 2
        x0 = gx + col * (cell_w + 16)
        y0 = gy + row * (cell_h + 8)
        d.rectangle([x0, y0, x0 + cell_w, y0 + cell_h], fill=CARD,
                    outline=RULE, width=1)
        if story is None:
            d.text((x0 + 16, y0 + 10), "THE DAY IN NUMBERS", font=f_k,
                   fill=RED)
            nx = x0 + 16
            f_n = font(SANS_B, 24)
            f_nl = font(SANS_R, 13)
            for num, lab in NUMBERS:
                d.text((nx, y0 + 34), num, font=f_n, fill=NAVY)
                ly = y0 + 66
                for lab_line in lab.split("\n"):
                    d.text((nx, ly), lab_line, font=f_nl, fill=GREY)
                    ly += 16
                nx += 110
            continue
        kicker, headline, summary, icon = story
        d.text((x0 + 78, y0 + 8), kicker, font=f_k, fill=RED)
        lines = wrap(d, headline, f_h, cell_w - 94)
        hy = draw_lines(d, x0 + 78, y0 + 26, lines[:2], f_h, INK, 24)
        lines = wrap(d, summary, f_s, cell_w - 32)
        draw_lines(d, x0 + 16, max(y0 + 72, hy + 4), lines[:2], f_s,
                   INK, 18)
        ICONS[icon](d, x0 + 10, y0 + 8, 58)

    # footer
    f_f = font(SANS_R, 15)
    foot = "All stories verified from live news reporting on 19 November 2026"
    tw = d.textlength(foot, font=f_f)
    d.text(((W - tw) / 2, 984), foot, font=f_f, fill=GREY)

    img.save(OUT, optimize=True)
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    main()
