# What is checked

A port of a geometry program can be wrong in a way that no eye catches: one turn
angle out of seven, or one tile reflected, reproduces the tile counts exactly and
produces a different tiling. So the counts are the least of what is checked here.

Run the suite with

```
pip install -e ".[dev]"
pytest
```

## Against the reference implementations

`tests/test_reference.py` compares generated patches against files exported from
Kaplan's own applications, coordinate by coordinate.

The comparison recovers the mapping rather than assuming it, because an export
carries whatever zoom and pan the app happened to be at when the button was pressed.
Two corresponding points fix a similarity; after that every tile has to line up.
Tiles are paired by position, not by the order they appear in the file, and outlines
are compared cyclically, since neither the order of the tiles nor the starting vertex
of an outline means anything.

The Spectre at generations 2 and 4 agrees to 1 × 10⁻¹⁴ of a tile edge, which is
floating-point noise. The hat and the H7 pair at generation 3 agree to the same. The
turtle is checked to *disagree* with the hat, which guards against the two shapes of
the continuum being confused.

These tests need the sample files, which are not in the repository because they are
not ours to redistribute. Put them in the directory above the repository, or point
the environment variable `SPECTRE_SAMPLES` at wherever they are, and the tests run;
otherwise they skip. They are

| file | where from |
|---|---|
| `spectre-gamma-round-2-tiles-62.svg` | the Save SVG button of <https://cs.uwaterloo.ca/~csk/spectre/app.html> |
| `spectre-gamma-round-4-tiles-3842.svg` | the same |
| `HAT-H7-GEN-3.svg`, `HAT-H8-GEN-3.svg` | <https://www2.abm.si/ein-stein/> |

There is deliberately no comparison of rendered images. Rasterizing throws away the
structure, needs a tolerance for antialiasing, and when it fails it says only that
two pictures differ. Comparing coordinates says which tile is wrong.

## That it is a tiling at all

`tests/test_covering.py` uses shapely on small patches to check that tiles do not
overlap, that the area covered equals the sum of the tile areas, and that no real gap
appears inside a patch. `tests/test_tilings.py` checks that the patch is one piece
edge to edge, that every tile is placed by an isometry so that no tile is ever
stretched, and that the Spectre's fourteen edges all have length 1.

Two caveats about the shapely results. A patch can be pinched at a single vertex,
which makes its union a multipolygon rather than a polygon, and that is geometry
rather than a fault. The union also picks up slivers of the size of a rounding error,
so what is asserted is that no hole is larger than 10⁻⁹, not that there are none.

## Counts

The full tables in [tilings.md](tilings.md), for both families and both categories,
including generation 7 of the Spectre at 1,874,888 tiles.

## Memory

`test_memory_does_not_grow_with_the_tile_count` builds generation 8, over fourteen
million tiles, and counts the objects in the graph. There are fewer than a hundred.

## The output

`tests/test_svg.py` reads back the SVG the package writes, expands the `<use>`
elements against the definitions, applies the root transform, and compares the result
against the patch it came from. This catches the column order of the SVG matrix,
which is transposed relative to the internal one. It also checks that rounding stays
inside the precision asked for, that the same outline is written for a shallow patch
and a deep one, and that the attribute is `stroke-width`. The reference exporters
write `stroke-weight`, which is a p5 function name and not an SVG attribute, so every
tile in their output silently falls back to a one-pixel outline.

## Grammars

`tests/test_grammar.py` checks the placement rules on a case simple enough to work
out by hand, checks that malformed grammars are refused rather than half-built, and
checks that the mega-object grammar in `examples/` counts 1, 4, 25, 136 and 1, 7, 37
and 2, 10, 60, 332. Those are Boris Horvat's own published figures. The counting is
verified; the geometry in that file is not, and is a first fit.
