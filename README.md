# The World Today — Thursday 19 November 2026

[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/badhanali30-bit/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/badhanali30-bit/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

Entry for [Sum up 19 November's world news in one image](https://make.fun/bounty/news-image-20261119) ($250, closes 2026-11-21T00:00:00Z).

## What it is

A one-page newspaper front page, **THE WORLD TODAY**, that sums up Thursday
19 November 2026 in eight stories. A Python program (`draw.py`, Pillow)
draws the whole page — masthead, date ribbon, lead story with summit art,
seven more stories in a two-column river, a numbers strip and a footer — to
`entry.png` (1024×1024, under 1 MiB). `main.ts` (Node 22, standard library
only) copies that image to `/output/entry.png`, or to
`$MAKEFUN_OUTPUT_DIR/entry.png` when the variable is set.

Every story below was checked against live news reporting published on
19 November 2026 before it was written into the page.

## The eight stories

1. **Trump, Xi and Putin sit down together for the first time** — the three
   leaders hold a 90-minute trilateral meeting in Shenzhen on the APEC
   sidelines and declare that nuclear war must never be fought.
2. **World court: Myanmar committed genocide** — the ICJ rules 9–6 that the
   2017 crackdown on the Rohingya was genocide, the first time it has held a
   state responsible, and orders return and reparations.
3. **Anthropic joins Nasdaq as ANT at $83** — the Claude maker prices 980
   million shares above its range and raises about $81.3 billion, the biggest
   IPO on record.
4. **After 13 years, GTA VI is finally here** — Rockstar's return to Vice
   City rolls out at midnight around the world and scores 99 on Metacritic.
5. **Voyager 1, a light-day from home** — NASA confirms the 1977 probe has
   passed 26 billion km, the farthest any human-made object has ever flown.
6. **Bangladesh burns as shutdown bites** — two ruling-party members are
   killed and Muhammad Yunus's ancestral home in Chattogram is torched as the
   Awami League's lockdown begins.
7. **Missile fire scars Riyadh's tallest tower** — windows blow out across
   seven floors of the 80-storey PIF Tower in the financial district, with no
   injuries reported.
8. **Neptune missiles hit Crimean Bridge again** — Ukraine strikes the rail
   span overnight, two days after a road section fell into the Kerch Strait,
   and trains are halted.

## Run it

```sh
python3 draw.py            # writes entry.png (deterministic: repeat runs are byte-identical)
MAKEFUN_OUTPUT_DIR=out node main.ts   # copies entry.png to out/entry.png
```

## Files

- `draw.py` — the page renderer (Pillow, no network, no clock, no randomness)
- `main.ts` — the entry runner for make.fun
- `entry.png` — the rendered front page
- `LICENSE` — MIT

Owner: badhanali30-bit · Repo: news-image-20261119
