# Pictures

## Choosing a format

The ending of `--out` decides.

| ending | what happens |
|---|---|
| `.svg` | SVG |
| `.svgz`, `.svg.gz` | SVG, compressed. Every viewer reads it, and it is five to ten times smaller. |
| `.png`, `.jpg`, `.tif` | a raster picture, drawn by matplotlib |
| `.pdf` | PDF, drawn by matplotlib |
| nothing | SVG to standard output |

Anything but SVG needs the `png` extra:
`pip install "spectre-explorer[png] @ git+..."`.

## The three SVG encodings

`--mode` picks one. They draw the same picture.

`use`, the default
: The outline of each kind of tile is written once inside `<defs>`, and each tile is
one short `<use>` element carrying its position. This is what makes the files small.

`flat`
: A `<polygon>` per tile with all its coordinates written out. Three or four times
larger. Use it for a tool that mishandles `<use>`.

`nested`
: One group per node of the substitution, each referring to groups from the
generation below, mirroring the way the tiling is actually built. The file then grows
with the number of generations instead of the number of tiles: generation 6 is 27 KB
and generation 8 would be about the same. A renderer still has to expand it, so this
makes the file small and not the drawing fast. Tiles are colored by their own label
in this mode, since sharing a group between supertiles is exactly what makes coloring
by ancestry impossible.

Sizes for generation 4 of `tile11`, 3,842 tiles, against the 2,344,104 bytes the
browser app writes for the same patch:

| mode | bytes | of the original |
|---|---|---|
| `flat` | 998,937 | 42.6% |
| `use` | 289,285 | 12.3% |
| `use`, compressed | 31,830 | 1.4% |
| `nested` | 17,103 | 0.7% |

## Precision

`--precision` sets how many decimal places coordinates get; the default is 3.
Coordinates are in tile units, where an edge is 1, so three places put every vertex
within a thousandth of an edge of where it belongs. It is worth knowing why that is
enough here and is not enough in the exports this replaces: those write coordinates
in screen units at whatever zoom the app was at, and the zoom shrinks by a factor of
2.8 with every generation, so the digits have to grow to keep up. Here the zoom lives
in the `viewBox` and the coordinates do not change at all from one generation to the
next.

`--precision 1` costs about 6% of the file and puts vertices within a tenth of an
edge, which is visible. `--precision 0` is too coarse to be a tiling.

## Lines

`--stroke-width` is in tile units, default 0.02, so it does not change as the patch
deepens. `--stroke` takes any SVG color, and `--stroke none` turns outlines off,
which is what you want when tiles are a pixel across.

The width and the color are set once on the enclosing group, not on every tile.

## Cropping

`--window LEFT BOTTOM RIGHT TOP`, in tile units, keeps only the tiles that meet that
rectangle. Whole supertiles that miss it are skipped without ever being expanded, so
the cost is closer to the size of the window than to the size of the patch. Use
`spectre bounds` to find out where the patch is before choosing a window.

## Colors

`--colors` picks a map: `pride`, `mystics`, `fig53`, `bright` for the Spectre family,
`gray` for the hat. Each tiling starts with the map its own app used.

`--color-by` picks what the color means.

`label`, the default
: each tile takes the color of its own label.

`ancestor:N`
: each tile takes the color of the supertile *N* generations above it. Every tile of
one supertile gets one color, so the substitution's structure is drawn instead of the
individual tiles. `ancestor:0` is the same as `label`; large *N* colors the whole
patch nearly uniformly.

Coloring by ancestry shows the structure of the *substitution*. That is not the same
decomposition as the mega-objects built from star triplets, which cut across
supertile boundaries; for those see [measuring.md](measuring.md).

## Size on screen

`--width` is the picture's width in pixels: the `width` attribute for SVG, and the
actual raster size for PNG. The height follows from the shape of the patch. For SVG
this only decides how large it opens; the geometry is in the `viewBox` either way.

## Animations

```
spectre frames tile11 --through 6 --pattern frame-%02d.png
```

One picture per generation, with `%d` in the pattern replaced by the number. Every
drawing option works here too. Give `--window` to keep the frames registered with one
another, otherwise each is scaled to its own patch and the picture appears to jump.
