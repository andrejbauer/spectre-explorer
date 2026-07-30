# The tilings

Seven of them, in two families. Give the name to any command as its first argument.

## The Spectre family

Five tilings share one substitution: nine labelled tiles, `Gamma`, `Delta`, `Theta`,
`Lambda`, `Xi`, `Pi`, `Sigma`, `Phi` and `Psi`, each of which becomes eight of the
nine at the next generation. `Gamma` is the odd one, the *mystic*: it is two tiles
rather than one, and one of its eight slots stays empty, so it grows a little more
slowly than the rest.

| name | shape |
|---|---|
| `tile11` | Tile(1,1), the Spectre with straight edges. This is the one to use. |
| `spectre` | the Spectre proper, with cubic curves for edges |
| `hexagons` | hexagons in place of Spectres, which shows the substitution by itself |
| `turtles-in-hats` | hats, with a turtle inside each mystic |
| `hats-in-turtles` | turtles, with a hat inside each mystic |

Pick which of the nine to draw with `--category`; the default is `Gamma`.

Tile counts for `tile11`, counting the mystic as two:

| generation | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|
| `Gamma` | 2 | 8 | 62 | 488 | 3,842 | 30,248 | 238,142 | 1,874,888 | 14,760,962 |
| `Delta` and the rest | 1 | 9 | 71 | 559 | 4,401 | 34,649 | 272,791 | 2,147,679 | 16,908,641 |

Each generation multiplies the count by 4 + √15 = 7.8730 in the limit.

## The hat family

`hat` and `turtle` are the H7/H8 substitution, which is a different tiling from
`turtles-in-hats` above even though the shapes are the same. There are two labels
rather than nine. `H8` is a single tile; `H7` is a reflected pair. Pick with
`--category`; the default is `H8`.

| generation | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| `H8` | 1 | 8 | 55 | 377 | 2,584 | 17,711 | 121,393 |
| `H7` | 2 | 7 | 47 | 322 | 2,207 | 15,127 | 103,682 |

Those are Fibonacci numbers and Lucas numbers, every fourth one, and the growth
factor is the fourth power of the golden ratio, 6.8541.

`hat` and `turtle` are two points on a continuum: the tile has two edge lengths, and
the hat has them as 1 and √3 while the turtle has √3 and 1. Everything else about
the two is the same.

## Coordinates

Tile edges have length 1, so the whole picture is in units of one tile edge. A patch
of generation *n* is about 2.8 times wider than one of generation *n* − 1 for the
Spectre, and about 2.6 times for the hat. Ask for the exact extent with

```
spectre bounds tile11 -g 6
```

which prints left, bottom, right and top.

The y axis points up, as in mathematics. SVG's points down, and the writer flips it
once at the root rather than in every coordinate.

## Where the shapes come from

Every vertex of every tile, and every transform that places one, lies in the field of
rational numbers with √3 adjoined, and every angle in the construction is a whole
multiple of 30 degrees. The package builds the substitution in that field exactly and
converts to floating point once, at the point where it starts walking through tiles.
So the shapes are not approximations of the intended ones; they are the intended
ones.
