# The World — 17 November 2026 (V6 Dense)

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/feru-art/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/feru-art/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

Entry for the [news-image-20261117 bounty](https://make.fun/bounty/news-image-20261117):
sum up Tuesday 17 November 2026's world news in one image.

V6 Dense is a dense newspaper front page: a dramatic hero photo of the
burning Kerch bridge, a numbered map strip (Kerch, Manila, Hormuz, Rwanda,
New York, Eritrea), six headline cards (Kerch, Trump in Manila, Gulf
carrier, EU–Rwanda hub, Chase outage, WHO Eritrea), and an "18 more
stories" list — 24 stories on one page.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` (Python 3.13, standard library only, no network) validates the
bundled JPEG and copies it byte for byte to `entry.png` in the output
directory. Two runs write identical bytes.

## Files

- `main.py` — the entry program
- `image.jpg` — the front-page image (1024×1024 JPEG, under 1 MiB)
- `LICENSE` — MIT
