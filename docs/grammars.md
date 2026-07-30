# Writing rules of your own

A grammar names some shapes and some rules. A rule says what an object of one
generation is made of: a list of parts, each a copy of some object, turned and then
slid until one of its anchor points sits on an anchor point of a part already placed.
Nothing is ever scaled. Objects grow because they have more parts.

That is enough to write down Kaplan's substitutions and Boris Horvat's mega-object
grammars in the same notation, and what comes out is an ordinary patch, so every
command that draws or measures a tiling works on it unchanged.

Start from a working file:

```
spectre grammar new mine.json
```

## The file

```json
{
  "name": "my grammar",
  "description": "notes to yourself; nothing reads this",

  "shapes": {
    "block": {
      "outline": [[0, 0], [1, 0], [1, 1], [0, 1]],
      "anchors": [[0, 0], [1, 0], [1, 1], [0, 1]]
    }
  },

  "rules": {
    "A": {
      "base": "block",
      "parts": [
        {"symbol": "A", "generation": -1},
        {"symbol": "A", "generation": -1, "onto": 1, "after": 0}
      ],
      "anchors": [
        {"part": 0, "anchor": 0},
        {"part": 1, "anchor": 1},
        {"part": 1, "anchor": 2},
        {"part": 0, "anchor": 3}
      ]
    }
  }
}
```

### shapes

What actually gets drawn. `outline` is a closed polygon, listed once round;
`anchors` are the points used to join things together. Anchors need not lie on the
outline, and there can be as many as you like.

### rules

One entry per symbol.

`base`
: the shape this object is at generation 0.

`seed`
: parts to assemble at generation 0, for an object that does not start as one piece.
Use this or `base`, not both. Boris Horvat's palindrome needs it, because a
palindrome is two star triplets before it is anything else.

`parts`
: what the object is made of at every later generation, in the order they are placed.

`anchors`
: which anchors of which parts become the anchors of the finished object. This is how
the next generation up attaches to it. Written as `{"part": i, "anchor": j}`, where
`i` counts the parts from 0. Leaving it out gives the object the anchors of its first
part.

### parts

| field | meaning | default |
|---|---|---|
| `symbol` | the rule, or the shape, to copy | required |
| `generation` | a step relative to the object being built: `-1` is one generation younger, `0` is the same generation | `-1` |
| `turn` | degrees to turn the copy by, counterclockwise | `0` |
| `reflect` | flip the copy left to right before turning it | `false` |
| `anchor` | which of the copy's own anchors is being placed | `0` |
| `onto` | which anchor of the earlier part it lands on | `0` |
| `after` | which earlier part, counting from 0; the one before it if left out | previous |

The first part in a list is placed at the origin, turned by its own `turn`; its
`anchor` and `onto` are ignored.

A part may name a shape as well as a rule. A part with `"generation": 0` refers to
another object of the same generation, which is fine as long as nothing ends up
depending on itself.

## Checking a grammar

Count before you draw. It is much easier to see that a sequence is wrong than that a
picture is.

```
spectre grammar count mine.json --through 6
```

That prints how many base shapes each symbol stands for at each generation. If you
know what the sequence should be, this tells you at once whether the rules say what
you meant.

Then look:

```
spectre grammar draw mine.json --symbol A --generation 4 -o mine.png
```

All the drawing options work: `--window`, `--color-by ancestor:2`, `--precision`,
`--mode`, and so on. Colors are assigned to symbols automatically.

## From Python

The same grammar as a dictionary, which is often easier to edit than JSON because you
can compute the numbers:

```python
from spectre_explorer import grammar, draw

spec = {
    "shapes": {
        "block": {
            "outline": [[0, 0], [1, 0], [1, 1], [0, 1]],
            "anchors": [[0, 0], [1, 0], [1, 1], [0, 1]],
        }
    },
    "rules": {
        "A": {
            "base": "block",
            "parts": [
                {"symbol": "A", "generation": -1},
                {"symbol": "A", "generation": -1, "onto": 1, "after": 0},
            ],
            "anchors": [{"part": 0, "anchor": 0}, {"part": 1, "anchor": 1}],
        }
    },
}

rules = grammar.read(spec)
print(grammar.counts(rules, 5))
draw(grammar.build(rules, "A", 5), "mine.svg")
```

## The worked example

`examples/spectre-mega-objects.json` is Boris K. Horvat's grammar for the Spectre
mega-objects:

```
MA(n) <- MA(n-1) & 3*MC(n-1)
MC(n) <- MC(n-1) & 3*PA(n-1)
PA(n) <- PA(n-1) & 2*MA(n)
```

Written in this notation it counts 1, 4, 25, 136 star triplets for MA, 1, 7, 37 for
MC and 2, 10, 60, 332 for PA, which are the numbers in the names of the figures on
his own pages. So the counting is settled.

The geometry is not. The turn angles and anchors in that file place three arms at 120
degrees and the palindrome's two arms opposite each other, which is what his pictures
show, but where exactly each arm attaches is a guess. The file is there to be edited:
change a `turn`, change an `onto`, draw it again, and compare with

<https://www2.abm.si/ein-stein/spectre-fractals-movies-www.htm>
