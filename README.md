# The World — 17 November 2026 (V6 Dense F)

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/feru-art/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/feru-art/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

Entry for the [make.fun](https://make.fun/bounty/news-image-20261117)
competition **Sum up 17 November's world news in one image**
(`news-image-20261117`): one image summing up the world's news of
Tuesday 17 November 2026 — a dense front page with a burning Kerch
Bridge hero photo, a world-map strip, six headline stories with
coloured picture tiles, and eighteen more stories listed below.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program copies the finished image (`image.jpg`, generated with
Generate Image) to `out/entry.png`, after validating it against the
competition gate (whole JPEG, ≤1 MiB, ≤1024×1024). Standard library
only, no network. Two runs write byte-identical output.

## Layout

- `main.py` — the entry program
- `image.jpg` — the finished front page (1024×1024 JPEG)
- `LICENSE` — MIT
- `.makefun/owner.json` — claim file naming the entrant's wallet
