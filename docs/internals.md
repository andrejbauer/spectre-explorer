# How it works

## The tiling is a graph, not a tree

A substitution replaces each of the nine labels by a supertile holding eight of the
nine. The same node goes into all nine supertiles, so a generation costs nine new
objects however many tiles it stands for. Generation 8 of the Spectre is 14,760,962
tiles held in fewer than a hundred objects.

`tiling.Tile` is a leaf, one polygon. `tiling.Supertile` holds pairs of a node and
the transform placing it. `tiling.placements` walks the graph and yields one
`Placement` per leaf: its label, the transform that puts it where it belongs, and the
labels of every supertile above it. Nothing keeps the expanded list, so memory stays
flat and the writer is the only thing that has to keep up.

The three drawing back ends, the table writer and the adjacency graph all consume
that one walk, and nothing else knows how the tiling is built.

## Exact where it is cheap, floating point where it is hot

Every vertex and every transform lies in the rational numbers with √3 adjoined, and
every angle is a whole multiple of 30 degrees. `algebra.Root3` does that arithmetic
exactly, on pairs of fractions, and `spectre.py` and `hat.py` build with it.

Exactness there is free: the graph is nine nodes per round. Exactness in the walk is
ruinous, because the walk does arithmetic once per tile and fractions there are
thousands of times slower than floats. So `tiling.approximate` converts the whole
graph to floats once, preserving the sharing, and the walk sees floats. Generation 7
takes twelve seconds rather than longer than anyone would wait.

`systems.patch` does the conversion for you. Ask for `exact=True` if you want the
other thing.

## Cropping

Each node knows the rectangle it occupies, worked out once from its children's
rectangles. A supertile whose rectangle misses the window is skipped without being
expanded. Sibling rectangles overlap heavily, so the pruning is loose, but it is the
difference between a window onto generation 8 costing seconds and costing hours.

## What was wrong with the exports this replaces

Four things, all in `Shape.streamSVG` and its neighbours.

**The coordinates carry full floating-point precision.** `${sp.x},${sp.y}` on a
double gives seventeen characters, twenty-eight numbers per tile. In the 2.3 MB
sample of generation 4, 82.8% of the bytes are coordinate digits.

**Nothing is shared.** Every tile is written as an independent polygon even though
all 3,842 of them are congruent copies of one shape. The graph that the program is
built on is flattened away at the last step.

**`stroke-weight` is not an SVG attribute.** It is the name of a p5 function.
Browsers ignore it, so every tile is outlined at the default one pixel rather than
the intended 0.1. Boris Horvat found this independently.

**The coordinate space fights precision.** The exporter bakes the on-screen zoom into
absolute canvas coordinates against a fixed `viewBox`. Each generation multiplies the
tile count by 7.87 and so shrinks the tile on screen by 2.8, so the digits have to
grow just to hold still. Measured across the three samples, one tile edge is 21.73
units at generation 2, 2.78 at generation 4 and 0.36 at generation 6.

There is also a leftover `vertex()` call at the top of the curved exporter, which
belongs to drawing on a canvas and not to writing a file, and which probably breaks
that export outright.

Here, geometry is written in tile units with the zoom in the `viewBox`, the outline
goes into `<defs>` once, `stroke` and `stroke-width` go on the enclosing group, and
`--precision` decides the digits. Generation 4 comes out at 289,285 bytes against
2,344,104.

## The H7/H8 port

`h7h8.js` differs from `spectre.js` in three ways worth knowing. It uses two labels
rather than nine. It carries coordinates exactly, in the same field, which this port
keeps and extends to the Spectre. And it places a child by deep-copying the whole
subtree and translating it in place, so its memory grows with the tile count; this
port stores a transform instead, which is why generation 7 is reachable.

## Layout

| module | what is in it |
|---|---|
| `algebra` | exact arithmetic in the rationals with √3 |
| `geometry` | points and affine transforms, over any scalar type |
| `tiling` | `Tile`, `Supertile`, the walk, bounds, counts |
| `spectre` | the nine-label substitution and its five sets of shapes |
| `hat` | the H7/H8 substitution |
| `systems` | the seven named tilings |
| `colors` | the color maps from the two reference apps |
| `svg`, `raster`, `data` | the three back ends |
| `grammar` | rules written as data |
| `adjacency` | which tiles touch which, and star triplets |
| `cli` | the `spectre` command |
