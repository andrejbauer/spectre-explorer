"""The H7/H8 substitution system for the hat and the turtle.

A port of `h7h8.js` by David Smith, Joseph Samuel Myers, Craig S. Kaplan and Chaim
Goodman-Strauss, which drives https://cs.uwaterloo.ca/~csk/hat/h7h8.html.  This is
not the same tiling as the hats and turtles in `spectre_explorer.spectre`, which run
those shapes through the spectre's nine-label substitution: here there are two
labels, H7 and H8, and tile counts grow by the fourth power of the golden ratio.

The original copies and translates whole subtrees to place them, so its memory grows
with the tile count.  This port keeps the placement in a transform, so it does not.
"""

from __future__ import annotations

from .algebra import ONE, ROOT3, ZERO, Root3, cosine_sine
from .geometry import (
    IDENTITY,
    Point,
    Transform,
    apply,
    compose,
    rotation,
    translation,
    translation_from_to,
    walk,
)
from .tiling import Node, Supertile, Tile

LABELS = ("H7", "H8")

#: Each edge of the tile as a length class, `"a"` or `"b"`, and a direction in whole
#: twelfths of a turn.
EDGES = (
    ("a", 0), ("a", 2), ("b", 11), ("b", 1), ("a", 4), ("a", 2), ("b", 5),
    ("b", 3), ("a", 6), ("a", 8), ("a", 8), ("a", 10), ("b", 7),
)

KEY_VERTICES = (1, 3, 9, 13)

#: `(turn in degrees, key of this tile, key of the previous one, use H7)`, walked in
#: order to place the seven tiles of an H8 supertile.  An H7 supertile is the same
#: without the last of them.
PLACEMENT_RULES = (
    (60, 2, 0, False),
    (120, 2, 0, False),
    (0, 1, 1, True),
    (-120, 2, 2, False),
    (-60, 2, 0, False),
    (0, 2, 0, False),
)

#: Edge lengths giving each of the two shapes the substitution is drawn with.
EDGE_LENGTHS: dict[str, tuple[Root3, Root3]] = {
    "hat": (ONE, ROOT3),
    "turtle": (ROOT3, ONE),
}

REFLECT_ACROSS_HORIZONTAL: Transform = (1, 0, 0, 0, -1, 0)


def outline_of(shape: str = "hat") -> tuple[Point, ...]:
    """The fourteen vertices of the hat or the turtle."""
    length_a, length_b = EDGE_LENGTHS[shape]
    displacements = [
        tuple(
            component * (length_a if length_class == "a" else length_b)
            for component in cosine_sine(30 * direction)
        )
        for length_class, direction in EDGES
    ]
    return tuple(walk(displacements, (ZERO, ZERO)))


def hat_system(shape: str = "hat") -> dict[str, Node]:
    """The two unsubstituted tiles: H8 is one tile, H7 is a reflected pair."""
    outline = outline_of(shape)
    keys = tuple(outline[index] for index in KEY_VERTICES)
    reflected = apply(REFLECT_ACROSS_HORIZONTAL, outline[8])
    pair = Supertile(
        "H7",
        (
            (Tile("unflipped", outline, keys), IDENTITY),
            (
                Tile("flipped", outline, keys),
                compose(
                    translation_from_to(reflected, outline[0]),
                    REFLECT_ACROSS_HORIZONTAL,
                ),
            ),
        ),
        keys,
    )
    return {"H8": Tile("single", outline, keys), "H7": pair}


def substitute(system: dict[str, Node]) -> dict[str, Node]:
    """One round of substitution, yielding the next H7 and H8."""
    single, pair = system["H8"], system["H7"]
    placed: list[tuple[Node, Transform]] = [(single, IDENTITY)]
    keys_of = lambda node, transform: [apply(transform, key) for key in node.keys]
    placed_keys = [keys_of(single, IDENTITY)]

    for angle, own_key, previous_key, use_pair in PLACEMENT_RULES:
        child = pair if use_pair else single
        turn = rotation(*cosine_sine(angle))
        transform = compose(
            translation_from_to(
                apply(turn, child.keys[own_key]), placed_keys[-1][previous_key]
            ),
            turn,
        )
        placed.append((child, transform))
        placed_keys.append(keys_of(child, transform))

    keys = (
        placed_keys[1][3],
        placed_keys[2][0],
        placed_keys[4][3],
        placed_keys[6][0],
    )
    return {
        "H8": Supertile("H8", tuple(placed), keys),
        "H7": Supertile("H7", tuple(placed[:-1]), keys),
    }
