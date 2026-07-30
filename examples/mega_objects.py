"""The Spectre mega-object grammar, written as a Python dictionary.

The same grammar as `spectre-mega-objects.json`, in the form that is easier to edit
when the numbers want computing rather than typing.  Run it:

    python examples/mega_objects.py

The counting is Boris K. Horvat's and comes out right.  The placement is a first fit
and is what you are meant to change: adjust a `turn` or an `onto`, run it again, and
compare with the figures at
https://www2.abm.si/ein-stein/spectre-fractals-movies-www.htm
"""

from math import cos, radians, sin

from spectre_explorer import draw, grammar

#: A placeholder for one star triplet.  Replace with the real outline when you have
#: it; nothing else in the grammar depends on what it looks like.
HEXAGON = [
    [round(cos(radians(60 * corner)), 6), round(sin(radians(60 * corner)), 6)]
    for corner in range(6)
]

#: Two of them side by side, which is what a palindrome starts as.
PAIR = HEXAGON + [[x - 1.5, y - 0.866025] for x, y in HEXAGON]

ANCHORS = [[0, 0], [1.5, 0.866025], [-1.5, 0.866025], [0, -1.732051]]

SPEC = {
    "name": "Spectre mega-objects",
    "shapes": {
        "star": {"outline": HEXAGON, "anchors": ANCHORS},
        "pair": {"outline": PAIR, "anchors": ANCHORS},
    },
    "rules": {
        # MA(n) <- MA(n-1) & 3*MC(n-1)
        "MA": {
            "base": "star",
            "parts": [
                {"symbol": "MA", "generation": -1},
                {"symbol": "MC", "generation": -1, "turn": 0, "onto": 1, "after": 0},
                {"symbol": "MC", "generation": -1, "turn": 120, "onto": 2, "after": 0},
                {"symbol": "MC", "generation": -1, "turn": 240, "onto": 3, "after": 0},
            ],
            "anchors": [
                {"part": 0, "anchor": 0},
                {"part": 1, "anchor": 1},
                {"part": 2, "anchor": 1},
                {"part": 3, "anchor": 1},
            ],
        },
        # MC(n) <- MC(n-1) & 3*PA(n-1)
        "MC": {
            "base": "star",
            "parts": [
                {"symbol": "MC", "generation": -1},
                {"symbol": "PA", "generation": -1, "turn": 0, "onto": 1, "after": 0},
                {"symbol": "PA", "generation": -1, "turn": 120, "onto": 2, "after": 0},
                {"symbol": "PA", "generation": -1, "turn": 240, "onto": 3, "after": 0},
            ],
            "anchors": [
                {"part": 0, "anchor": 0},
                {"part": 1, "anchor": 1},
                {"part": 2, "anchor": 1},
                {"part": 3, "anchor": 1},
            ],
        },
        # PA(n) <- PA(n-1) & 2*MA(n), with MA at the same generation
        "PA": {
            "seed": [
                {"symbol": "star"},
                {"symbol": "star", "turn": 180, "onto": 1, "after": 0},
            ],
            "parts": [
                {"symbol": "PA", "generation": -1},
                {"symbol": "MA", "generation": 0, "turn": 0, "onto": 1, "after": 0},
                {"symbol": "MA", "generation": 0, "turn": 180, "onto": 2, "after": 0},
            ],
            "anchors": [
                {"part": 0, "anchor": 0},
                {"part": 1, "anchor": 1},
                {"part": 1, "anchor": 2},
            ],
        },
    },
}

WANTED = {"MA": [1, 4, 25, 136], "MC": [1, 7, 37], "PA": [2, 10, 60, 332]}

if __name__ == "__main__":
    rules = grammar.read(SPEC)
    counted = [grammar.counts(rules, generation) for generation in range(5)]
    print(f"{'gen':>4} {'MA':>6} {'MC':>6} {'PA':>6}")
    for generation, row in enumerate(counted):
        print(f"{generation:>4} {row['MA']:>6} {row['MC']:>6} {row['PA']:>6}")
    for symbol, wanted in WANTED.items():
        got = [row[symbol] for row in counted][: len(wanted)]
        print(f"{symbol}: {got} against his figures {wanted}: {'agree' if got == wanted else 'DIFFER'}")

    draw(grammar.build(rules, "MA", 3), "megastar-MA-136.svg")
    print("drew megastar-MA-136.svg")
