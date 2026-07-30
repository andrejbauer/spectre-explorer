# Spectre explorer

Generate, crop, color and measure the aperiodic tilings built from the Spectre, the
hat and the turtle. Write them as SVG that is a seventh the size of what the browser
apps produce, go past the generation those apps stop at, and describe assemblies of
your own in a file and draw them.

The tilings and the substitutions are the work of David Smith, Joseph Samuel Myers,
Craig S. Kaplan and Chaim Goodman-Strauss, [*An aperiodic
monotile*](https://arxiv.org/abs/2305.17743) and [*A chiral aperiodic
monotile*](https://arxiv.org/abs/2305.17743). This is a port of their two browser
applications, checked against them tile by tile.

## Installing

```
pip install git+https://github.com/USER/spectre-explorer
```

or, without git,

```
pip install https://github.com/USER/spectre-explorer/archive/refs/heads/main.zip
```

That gives you a command called `spectre` and an importable package called
`spectre_explorer`. Nothing else is needed to write SVG. For PNG and PDF add the
`png` extra, which brings in matplotlib:

```
pip install "spectre-explorer[png] @ git+https://github.com/USER/spectre-explorer"
```

Python 3.10 or later, on Windows, Linux or macOS.

## What it does

Draw a patch of any of the tilings, at any generation:

```
spectre draw tile11 --generation 7 --out patch.svgz
```

Generation 7 of the Spectre is 1,874,888 tiles. It takes about twelve seconds and
comes out at 15 MB compressed, where the browser app cannot produce it at all.

Look at part of a patch without generating the rest:

```
spectre draw tile11 -g 8 --window -40 -40 40 40 --out crop.png
```

Show the fractal structure by coloring each tile after the supertile it came from:

```
spectre draw tile11 -g 5 --colors pride --color-by ancestor:3 --out fractal.png
```

Count things, generation by generation:

```
spectre count hat --through 6
```

Write one row per tile, for a spreadsheet or a statistics package:

```
spectre data tile11 -g 5 --out tiles.csv
```

Draw one picture per generation, for an animation:

```
spectre frames tile11 --through 6 --pattern frame-%02d.svg
```

Write down rules of your own and draw what they build:

```
spectre grammar new mine.json
spectre grammar count mine.json
spectre grammar draw mine.json --symbol A --generation 4 --out mine.svg
```

Every command explains itself with `--help`.

## From Python

```python
from spectre_explorer import tiling_patch, draw

patch = tiling_patch("tile11", category="Gamma", generation=5)
draw(patch, "patch.svg", colors="mystics")
```

## Documentation

| | |
|---|---|
| [docs/tutorial.md](docs/tutorial.md) | start here: from installing to your first pictures |
| [docs/tilings.md](docs/tilings.md) | the seven tilings, their categories, and their tile counts |
| [docs/pictures.md](docs/pictures.md) | file formats, the three SVG encodings, cropping, coloring, sizes |
| [docs/grammars.md](docs/grammars.md) | writing rules of your own, in JSON or in Python |
| [docs/measuring.md](docs/measuring.md) | counts, the tile table, neighbours, star triplets |
| [docs/verification.md](docs/verification.md) | what is checked, against what, and how to run it |
| [docs/internals.md](docs/internals.md) | how it works, and what was wrong with the exports it replaces |

## Provenance and licence

Ported from `spectre.js` and `h7h8.js` on Craig S. Kaplan's pages, which carry no
licence of their own. Kaplan publishes his other tiling code under a BSD 3-clause
licence, and the images on those pages are CC-BY 4.0. Treat this as derived work and
attribute the four authors.
