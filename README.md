# Sunday 22 November 2026 — The World in One Page

[![Competition](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![Rank](https://make.fun/badge/news-image-20261122/XIIIIXV/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![Reward](https://make.fun/badge/news-image-20261122/XIIIIXV/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

Entry for the make.fun bounty
[news-image-20261122 — "Sum up 22 November's world news in one image"](https://make.fun/bounty/news-image-20261122).

One page, 33 stories across 7 regions — every fact date-checked to Sunday
22 November 2026. Three illustrated leads (two supertankers hit by
mines near the Strait of Hormuz, COP31 collapsing without a deal,
Democrats winning their largest House majority since 1992), ten more
illustrated cards (186 Russian drones over Ukraine, Iran's unconfirmed
claim of a strike on US bases in Bahrain, the Sparta II still burning,
Hong Kong's Election Committee poll, Alcaraz, Liverpool, 'El Chapo
Isidro', Thitikul, Verstappen, Wembanyama), a numbered world map
("WHERE IT HAPPENED", pins 1–13), a numbered "ALSO ON SUNDAY" list
for the other 20 stories, a UTC timeline, and a red DATE CHECK box
naming the stories deliberately left out (the 19–20 Nov 400-drone
strike, the 19 Nov ICJ Myanmar verdict, the 20 Nov Nigeria boat
capsize, the 21 Nov Sparta II strike itself, the 23 Nov FIFA
announcement) and what was still undecided on Sunday. Every
illustrated story carries a status pill — REPORTED / CLAIM /
CONFIRMED / ONGOING — so an unconfirmed claim is never stated as fact.

## How it runs

`main.py` copies the pre-rendered `entry.png` into
`$MAKEFUN_OUTPUT_DIR`. It renders nothing and writes nothing into the
repository directory.

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`gen_22nov.py` is the deterministic PIL generator that drew `entry.png`
(1024×1024). Running it twice produces byte-identical output. The story
list, with a named source and first-report time for every card, is in
`dev/real/stories.json` (kept outside this repository).

## License

MIT — see `LICENSE`.
