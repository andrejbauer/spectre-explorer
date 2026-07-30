# Getting started

This walks from an empty machine to a handful of pictures. It assumes you can open a
terminal and type into it, and nothing else.

## 1. Install it

```
pip install "spectre-explorer[png] @ git+https://github.com/USER/spectre-explorer"
```

Check that it worked:

```
spectre --help
```

If `spectre` is not found, your Python scripts directory is not on your path. Use
`python -m spectre_explorer` in place of `spectre` everywhere below; the two are the
same program.

## 2. Draw something small

```
spectre draw tile11 --generation 3 --out first.svg
```

`tile11` is the straight-edged Spectre, the shape Kaplan's app calls Tile(1,1).
`--generation 3` applies the substitution three times, giving 488 tiles. Open
`first.svg` in a browser or in Inkscape.

Ask for a PNG instead by saying so in the file name:

```
spectre draw tile11 -g 3 --out first.png
```

`-g` is short for `--generation`, and `-o` is short for `--out`.

## 3. Choose the shape and the colors

```
spectre draw spectre -g 3 --colors pride -o curved.png
spectre draw hat     -g 4 -o hats.png
spectre draw turtle  -g 4 -o turtles.png
```

`spectre` is the curved Spectre, with the wiggly edges. `hat` and `turtle` are the
H7/H8 tiling, which is a different substitution from the Spectre's; see
[tilings.md](tilings.md).

The color maps are `pride`, `mystics`, `fig53`, `bright` and `gray`. Each tiling
starts with the one its own app used.

## 4. Go deep

```
spectre draw tile11 -g 6 -o six.svgz
spectre draw tile11 -g 7 -o seven.svgz
```

Generation 6 is 238,142 tiles and takes about a second. Generation 7 is 1,874,888
and takes about twelve. The `.svgz` ending compresses the file; every SVG viewer
reads it.

Generation 8 as a whole picture is not worth making: it is 14,760,962 tiles, and no
viewer will open it comfortably. Take a piece of it instead.

## 5. Take a piece

First ask how big the patch is:

```
spectre bounds tile11 -g 8
```

That prints a rectangle, as left, bottom, right, top. Then ask for a part of it:

```
spectre draw tile11 -g 8 --window -40 -40 40 40 -o piece.png
```

Only the tiles that meet the rectangle are generated, so this is quick even though
the patch it comes from is enormous.

## 6. See the fractal structure

Every tile in a deep patch sits inside a supertile, which sits inside a bigger one.
Coloring a tile after its ancestor several rounds up makes that visible:

```
spectre draw tile11 -g 5 --colors pride --color-by ancestor:3 -o structure.png
```

Try `ancestor:1` through `ancestor:5` and watch the scale of the pattern change.

## 7. Get the numbers out

```
spectre count tile11 --through 8
spectre data tile11 -g 5 -o tiles.csv
```

The first prints a table of tile counts. The second writes one row per tile: its
label, which supertiles it came from, where it sits and how it is turned. Open it in
a spreadsheet. See [measuring.md](measuring.md).

## 8. Make an animation

```
spectre frames tile11 --through 6 --pattern frame-%02d.png
```

That writes `frame-00.png` through `frame-06.png`. Fixing the window keeps the
frames registered with one another:

```
spectre frames tile11 --through 6 --window -60 -60 60 60 --pattern frame-%02d.png
```

## 9. Write rules of your own

```
spectre grammar new mine.json
```

Open `mine.json` in a text editor. The `description` at the top explains every field.
Check what your rules count up to before you draw anything:

```
spectre grammar count mine.json
```

Then draw one:

```
spectre grammar draw mine.json --symbol A --generation 4 -o mine.png
```

Change a number, run it again, look again. That loop is the point of the thing. See
[grammars.md](grammars.md) for the whole format, and
`examples/spectre-mega-objects.json` for a worked case.
