# Measuring a tiling

Pictures are one way out of a patch; numbers are the other. Nothing here requires
reading anything out of an image.

## Counts

```
spectre count tile11 --through 8
spectre count hat --through 6
```

Prints comma-separated rows, one per generation, one column per category. Redirect it
into a file and it is a spreadsheet.

## One row per tile

```
spectre data tile11 -g 5 --out tiles.csv
spectre data tile11 -g 8 --window -40 -40 40 40 --out piece.csv
```

The columns are

| column | meaning |
|---|---|
| `label` | which of the nine, or which of `single`, `unflipped`, `flipped` |
| `ancestry` | the labels from the whole patch down to the tile, separated by slashes |
| `a` … `f` | the tile's placement: `(x, y)` goes to `(ax + by + c, dx + ey + f)` |
| `center_x`, `center_y` | the average of the tile's corners |

`ancestry` is the useful one for structure: two tiles are in the same supertile *k*
generations up exactly when their ancestries agree up to *k* from the end.

## Neighbours and star triplets

From Python. `spectre_explorer.adjacency` turns a patch into a graph: tiles are
vertices, and two tiles are joined when they share a whole edge.

```python
from spectre_explorer.adjacency import expand, star_triplets
from spectre_explorer import tiling_patch

patch = expand(tiling_patch("tile11", "Gamma", 4))
print(len(patch), "tiles")
print(len(patch.neighbors[0]), "neighbors of the first tile")
print(len(patch.components()), "connected pieces")

for corner, three in star_triplets(patch):
    ...
```

`star_triplets` finds the points where three tiles meet and the arrangement turns
into itself under a third of a turn. Three tiles meeting at a point is the ordinary
case in these tilings and means nothing on its own; the three-fold symmetry is what
picks out the star triplets that the mega-objects are built from.

Read those counts carefully near the edge of a patch. A triplet needs its whole
neighbourhood, so a finite patch reports fewer per tile than the infinite tiling
does, and the shortfall fades slowly:

| generation | tiles | triplets | tiles per triplet |
|---|---|---|---|
| 3 | 488 | 15 | 32.5 |
| 4 | 3,842 | 259 | 14.8 |
| 5 | 30,248 | 2,420 | 12.5 |
| 6 | 238,142 | 20,943 | 11.4 |

Boris Horvat gives the density of star triplets in the infinite tiling as one per
5 + √15 = 8.873 tiles. The figures above are consistent with heading there and are
nowhere near arriving, which is what boundary effects of this size look like. Do not
read a number off a single generation.

## Vertices

`Patch.corners()` gives a dictionary from each vertex of the patch to the tiles that
meet there, which is the starting point for anything about local configurations.
