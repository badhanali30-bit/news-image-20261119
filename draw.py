"""Front page for Thursday 19 November 2026.

Renders one 1024x1024 newspaper front page -- eight verified stories from
live reporting on the day -- to entry.png next to this file.

Deterministic by construction: fixed palette, fixed type, fixed geometry,
no clock, no randomness, no network. Running it twice writes identical bytes.
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)      # warm newsprint
CARD = (255, 255, 255)       # story card face
INK = (26, 26, 26)           # body ink
RUBY = (164, 19, 60)         # kicker red
TEAL = (15, 76, 92)          # secondary accent
OCHRE = (233, 196, 106)      # warm highlight
MIDNIGHT = (20, 33, 61)      # date ribbon
SMOKE = (96, 96, 96)         # captions
RULE = (26, 26, 26)          # hairlines
SKY = (214, 232, 240)        # lead art sky
LEAF = (46, 125, 50)         # third banner

SIDE = 1024
EDGE = 26                    # outer margin
GUTTER = 14                  # space between columns/cards

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def typeface(path: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a TTF face, falling back to PIL's built-in face if absent."""
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


# ------------------------------------------------------------------- type
MASTHEAD = typeface(SERIF_BOLD, 58)
TAGLINE = typeface(SANS_BOLD, 14)
RIBBON = typeface(SANS_BOLD, 25)
RIBBON_SMALL = typeface(SANS_BOLD, 13)
LEAD_KICKER = typeface(SANS_BOLD, 15)
LEAD_HEAD = typeface(SERIF_BOLD, 30)
LEAD_DECK = typeface(SANS, 15)
CARD_KICKER = typeface(SANS_BOLD, 12)
CARD_HEAD = typeface(SERIF_BOLD, 19)
CARD_DECK = typeface(SANS, 14)
STAT_BIG = typeface(SERIF_BOLD, 24)
STAT_SMALL = typeface(SANS, 12)
FOOT = typeface(SANS, 13)


# ------------------------------------------------------------------ stories
# Headlines and decks written from live reporting on 19 November 2026.
LEAD = {
    "kicker": "LEAD STORY  ·  SHENZHEN",
    "headline": "Trump, Xi and Putin sit down together for the first time",
    "deck": (
        "Ninety minutes at the APEC summit: nuclear arms, Ukraine and Iran "
        "on the table, and a joint declaration that nuclear war must never "
        "be fought."
    ),
}

RIVER = [
    {
        "tag": "WORLD COURT",
        "headline": "World court: Myanmar committed genocide",
        "deck": (
            "The ICJ rules 9–6 that the 2017 crackdown on the Rohingya was "
            "genocide — the first time it has held a state responsible."
        ),
        "glyph": "scales",
        "accent": TEAL,
    },
    {
        "tag": "MARKETS",
        "headline": "Anthropic joins Nasdaq as ANT at $83",
        "deck": (
            "The Claude maker prices 980 million shares above its range, "
            "raising about $81.3 billion in the biggest IPO on record."
        ),
        "glyph": "chart",
        "accent": RUBY,
    },
    {
        "tag": "CULTURE",
        "headline": "After 13 years, GTA VI is finally here",
        "deck": (
            "Rockstar's return to Vice City rolls out at midnight around the "
            "world and lands a 99 on Metacritic."
        ),
        "glyph": "pad",
        "accent": MIDNIGHT,
    },
    {
        "tag": "SPACE",
        "headline": "Voyager 1, a light-day from home",
        "deck": (
            "NASA confirms the 1977 probe has passed 26 billion km — the "
            "farthest any human-made object has ever flown."
        ),
        "glyph": "dish",
        "accent": TEAL,
    },
    {
        "tag": "BANGLADESH",
        "headline": "Bangladesh burns as shutdown bites",
        "deck": (
            "Two ruling-party members are killed and Muhammad Yunus's "
            "ancestral home in Chattogram is torched as the lockdown begins."
        ),
        "glyph": "flame",
        "accent": RUBY,
    },
    {
        "tag": "RIYADH",
        "headline": "Missile fire scars Riyadh's tallest tower",
        "deck": (
            "Windows blow out across seven floors of the 80-storey PIF "
            "Tower in the kingdom's financial district; no injuries are "
            "reported."
        ),
        "glyph": "tower",
        "accent": MIDNIGHT,
    },
    {
        "tag": "UKRAINE",
        "headline": "Neptune missiles hit Crimean Bridge again",
        "deck": (
            "Ukraine strikes the rail span overnight, two days after a road "
            "section fell into the Kerch Strait; trains are halted."
        ),
        "glyph": "bridge",
        "accent": TEAL,
    },
]

STATS = [
    ("90 MIN", "three-way talks in Shenzhen"),
    ("9–6", "ICJ vote finding genocide"),
    ("$81.3BN", "raised in the ANT listing"),
    ("99", "GTA VI on Metacritic"),
]


# ------------------------------------------------------------------ wrapping
def split_lines(text: str, font: ImageFont.FreeTypeFont, width: int,
                pen: ImageDraw.ImageDraw) -> list[str]:
    """Greedy word wrap to the given pixel width."""
    rows: list[str] = []
    current = ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if pen.textlength(trial, font=font) <= width or not current:
            current = trial
        else:
            rows.append(current)
            current = word
    if current:
        rows.append(current)
    return rows


def block_lines(pen: ImageDraw.ImageDraw, text: str,
                font: ImageFont.FreeTypeFont, width: int,
                leading: int) -> tuple[list[str], int]:
    """Wrapped lines plus their total pixel height."""
    lines = split_lines(text, font, width, pen)
    return lines, len(lines) * leading


def put_lines(pen: ImageDraw.ImageDraw, lines: list[str], x: int, y: int,
              font: ImageFont.FreeTypeFont, leading: int,
              fill: tuple[int, int, int] = INK) -> int:
    """Draw wrapped lines top-down; return the y just below the last one."""
    for line in lines:
        pen.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


# ------------------------------------------------------------------ glyphs
def paint_glyph(pen: ImageDraw.ImageDraw, box: tuple[int, int, int, int],
                kind: str, accent: tuple[int, int, int]) -> None:
    """Small geometric pictogram inside a rounded accent tile."""
    x0, y0, x1, y1 = box
    pen.rounded_rectangle(box, radius=9, fill=accent)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    pale = (255, 255, 255)
    gold = OCHRE
    if kind == "scales":
        pen.line([(cx, y0 + 12), (cx, y1 - 12)], fill=pale, width=3)
        pen.line([(x0 + 10, y0 + 16), (x1 - 10, y0 + 16)], fill=pale, width=3)
        pen.polygon([(x0 + 8, y0 + 30), (x0 + 20, y0 + 30), (cx - 8, y0 + 18)],
                    fill=gold)
        pen.polygon([(cx + 8, y0 + 18), (x1 - 20, y0 + 30), (x1 - 8, y0 + 30)],
                    fill=gold)
        pen.line([(x0 + 12, y1 - 10), (x1 - 12, y1 - 10)], fill=pale, width=3)
    elif kind == "chart":
        pen.rectangle([x0 + 12, y1 - 24, x0 + 20, y1 - 12], fill=pale)
        pen.rectangle([x0 + 24, y1 - 32, x0 + 32, y1 - 12], fill=pale)
        pen.rectangle([x0 + 36, y1 - 40, x0 + 44, y1 - 12], fill=pale)
        pen.line([(x0 + 10, y1 - 38), (x0 + 26, y1 - 46), (x0 + 46, y0 + 14)],
                 fill=gold, width=3)
        pen.polygon([(x0 + 46, y0 + 14), (x0 + 38, y0 + 15), (x0 + 45, y0 + 22)],
                    fill=gold)
    elif kind == "pad":
        pen.rounded_rectangle([x0 + 9, y0 + 16, x1 - 9, y1 - 16], radius=10,
                              fill=pale)
        pen.rectangle([x0 + 19, cy - 3, x0 + 27, cy + 3], fill=accent)
        pen.rectangle([x0 + 21, cy - 6, x0 + 25, cy + 6], fill=accent)
        pen.ellipse([x1 - 29, cy - 9, x1 - 21, cy - 1], fill=RUBY)
        pen.ellipse([x1 - 29, cy + 1, x1 - 21, cy + 9], fill=TEAL)
    elif kind == "dish":
        pen.arc([x0 + 10, y0 + 8, x1 - 10, y0 + 40], start=0, end=180,
                fill=pale, width=4)
        pen.line([(cx, y0 + 24), (cx, y1 - 14)], fill=pale, width=3)
        pen.line([(x0 + 16, y1 - 14), (x1 - 16, y1 - 14)], fill=pale, width=3)
        pen.ellipse([cx - 4, y0 + 12, cx + 4, y0 + 20], fill=gold)
    elif kind == "flame":
        pen.polygon(
            [(cx, y0 + 8), (cx + 12, y0 + 24), (cx + 8, y0 + 30),
             (cx + 14, y0 + 38), (cx, y1 - 10), (cx - 14, y1 - 10),
             (cx - 10, y0 + 32), (cx - 12, y0 + 22)],
            fill=gold)
        pen.ellipse([cx - 5, y1 - 24, cx + 5, y1 - 12], fill=RUBY)
    elif kind == "tower":
        pen.rectangle([cx - 7, y0 + 12, cx + 7, y1 - 10], fill=pale)
        pen.rectangle([cx - 11, y0 + 22, cx + 11, y0 + 30], fill=pale)
        for wy in (y0 + 34, y0 + 40, y1 - 20):
            pen.rectangle([cx - 4, wy, cx + 4, wy + 3], fill=accent)
        pen.line([(x0 + 10, y1 - 10), (x1 - 10, y1 - 10)], fill=pale, width=3)
    elif kind == "bridge":
        pen.arc([x0 + 10, y0 + 14, x1 - 10, y1 - 2], start=180, end=360,
                fill=pale, width=3)
        for vx in (x0 + 18, cx, x1 - 18):
            pen.line([(vx, y0 + 26), (vx, y1 - 12)], fill=pale, width=3)
        pen.line([(x0 + 8, y1 - 12), (x1 - 8, y1 - 12)], fill=gold, width=4)


# ---------------------------------------------------------------- lead art
def paint_summit_art(pen: ImageDraw.ImageDraw,
                     box: tuple[int, int, int, int]) -> None:
    """Three hanging banners over a round table: the Shenzhen summit."""
    x0, y0, x1, y1 = box
    pen.rectangle(box, fill=SKY, outline=RULE, width=2)
    # hanging rail
    pen.line([(x0 + 8, y0 + 14), (x1 - 8, y0 + 14)], fill=RULE, width=3)
    banners = [RUBY, MIDNIGHT, LEAF]
    span = (x1 - x0 - 40) // 3
    for i, colour in enumerate(banners):
        bx0 = x0 + 20 + i * span
        bx1 = bx0 + span - 16
        pen.rectangle([bx0, y0 + 14, bx1, y0 + 92], fill=colour)
        pen.polygon([(bx0, y0 + 92), (bx1, y0 + 92),
                     ((bx0 + bx1) // 2, y0 + 108)], fill=colour)
        pen.ellipse([((bx0 + bx1) // 2) - 5, y0 + 34,
                     ((bx0 + bx1) // 2) + 5, y0 + 44], fill=OCHRE)
    # round table
    pen.ellipse([x0 + 40, y1 - 42, x1 - 40, y1 - 14], fill=MIDNIGHT)
    for cx in (x0 + 70, (x0 + x1) // 2, x1 - 70):
        pen.ellipse([cx - 6, y1 - 52, cx + 6, y1 - 40], fill=INK)


# ------------------------------------------------------------------ layout
class Sheet:
    """A vertical flow: each section draws itself and advances the cursor."""

    def __init__(self) -> None:
        self.canvas = Image.new("RGB", (SIDE, SIDE), PAPER)
        self.pen = ImageDraw.Draw(self.canvas)
        self.y = EDGE

    def rule(self, weight: int = 2) -> None:
        self.pen.line([(EDGE, self.y), (SIDE - EDGE, self.y)], fill=RULE,
                      width=weight)
        self.y += weight + 6

    def masthead(self) -> None:
        label = "THE WORLD TODAY"
        w = self.pen.textlength(label, font=MASTHEAD)
        self.pen.text(((SIDE - w) / 2, self.y), label, font=MASTHEAD, fill=INK)
        self.y += 68
        sub = "ONE DAY  ·  ONE PAGE  ·  THE NEWS IN BRIEF"
        w = self.pen.textlength(sub, font=TAGLINE)
        self.pen.text(((SIDE - w) / 2, self.y), sub, font=TAGLINE, fill=SMOKE)
        self.y += 22
        self.rule(3)

    def ribbon(self) -> None:
        top = self.y
        self.pen.rectangle([EDGE, top, SIDE - EDGE, top + 38], fill=MIDNIGHT)
        day = "THURSDAY 19 NOVEMBER 2026"
        self.pen.text((EDGE + 18, top + 6), day, font=RIBBON, fill=(255, 255, 255))
        side = "8 STORIES · 1 PAGE"
        w = self.pen.textlength(side, font=RIBBON_SMALL)
        self.pen.text((SIDE - EDGE - 18 - w, top + 12), side,
                      font=RIBBON_SMALL, fill=OCHRE)
        self.y = top + 38 + 10

    def lead(self) -> None:
        top = self.y
        left_w = 560
        art_box = (EDGE + left_w + GUTTER, top, SIDE - EDGE, top + 168)
        paint_summit_art(self.pen, art_box)
        x = EDGE + 8
        self.pen.text((x, top), LEAD["kicker"], font=LEAD_KICKER, fill=RUBY)
        y = top + 26
        head_lines, _ = block_lines(self.pen, LEAD["headline"], LEAD_HEAD,
                                    left_w - 8, 36)
        y = put_lines(self.pen, head_lines, x, y, LEAD_HEAD, 36)
        y += 6
        deck_lines, _ = block_lines(self.pen, LEAD["deck"], LEAD_DECK,
                                    left_w - 8, 20)
        y = put_lines(self.pen, deck_lines, x, y, LEAD_DECK, 20, fill=(51, 51, 51))
        self.y = max(top + 168, y) + 10

    def card_height(self, story: dict, width: int) -> int:
        inner = width - 76
        _, head_h = block_lines(self.pen, story["headline"], CARD_HEAD, inner, 22)
        _, deck_h = block_lines(self.pen, story["deck"], CARD_DECK, inner, 18)
        # Deck must clear both the headline and the 52px glyph tile.
        deck_top = max(27 + head_h + 4, 70)
        return deck_top + deck_h + 8

    def card(self, story: dict, box: tuple[int, int, int, int]) -> None:
        x0, y0, x1, y1 = box
        self.pen.rectangle(box, fill=CARD, outline=RULE, width=1)
        gx0, gy0 = x0 + 10, y0 + 10
        paint_glyph(self.pen, (gx0, gy0, gx0 + 52, gy0 + 52),
                    story["glyph"], story["accent"])
        tx = gx0 + 62
        self.pen.text((tx, y0 + 10), story["tag"], font=CARD_KICKER,
                      fill=RUBY)
        inner = (x1 - 10) - tx
        head_lines, _ = block_lines(self.pen, story["headline"], CARD_HEAD,
                                    inner, 22)
        y = put_lines(self.pen, head_lines, tx, y0 + 27, CARD_HEAD, 22)
        deck_top = max(y + 4, y0 + 70)
        deck_lines, _ = block_lines(self.pen, story["deck"], CARD_DECK,
                                    x1 - x0 - 20, 18)
        put_lines(self.pen, deck_lines, x0 + 10, deck_top, CARD_DECK, 18,
                  fill=(51, 51, 51))

    def river(self) -> None:
        col_w = (SIDE - 2 * EDGE - GUTTER) // 2
        idx = 0
        while idx < len(RIVER):
            pair = RIVER[idx:idx + 2]
            height = max(self.card_height(s, col_w) for s in pair)
            for j, story in enumerate(pair):
                x0 = EDGE + j * (col_w + GUTTER)
                self.card(story, (x0, self.y, x0 + col_w, self.y + height))
            self.y += height + 12
            idx += 2

    def stats(self) -> None:
        top = self.y
        self.pen.rectangle([EDGE, top, SIDE - EDGE, top + 70], fill=CARD,
                           outline=RULE, width=1)
        self.pen.text((EDGE + 14, top + 7), "THE DAY IN NUMBERS",
                      font=CARD_KICKER, fill=RUBY)
        cell_w = (SIDE - 2 * EDGE) // 4
        for i, (big, small) in enumerate(STATS):
            cx = EDGE + i * cell_w + 14
            self.pen.text((cx, top + 22), big, font=STAT_BIG, fill=MIDNIGHT)
            self.pen.text((cx, top + 48), small, font=STAT_SMALL, fill=SMOKE)
        self.y = top + 70 + 8

    def footer(self) -> None:
        note = ("All eight stories checked against live reporting "
                "on 19 November 2026.")
        w = self.pen.textlength(note, font=FOOT)
        self.pen.text(((SIDE - w) / 2, self.y), note, font=FOOT, fill=SMOKE)
        self.y += 18
        self.pen.line([(EDGE, self.y), (SIDE - EDGE, self.y)], fill=RULE,
                      width=1)

    def frame(self) -> None:
        self.pen.rectangle([10, 10, SIDE - 11, SIDE - 11], outline=RULE,
                           width=2)
        self.pen.rectangle([16, 16, SIDE - 17, SIDE - 17], outline=RULE,
                           width=1)


def build() -> Path:
    sheet = Sheet()
    sheet.masthead()
    sheet.ribbon()
    sheet.lead()
    sheet.river()
    sheet.stats()
    sheet.footer()
    sheet.frame()
    out = Path(__file__).resolve().parent / "entry.png"
    sheet.canvas.save(out, format="PNG", optimize=True)
    return out


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    target = build()
    size = target.stat().st_size
    print(f"wrote {target} ({size} bytes, sha256 {digest(target)})")
    if size > 1_048_576:
        print("ERROR: entry.png exceeds 1 MiB", file=sys.stderr)
        sys.exit(1)
    if Image.open(target).size != (SIDE, SIDE):
        print("ERROR: entry.png is not 1024x1024", file=sys.stderr)
        sys.exit(1)
