"""The Spectre substitution system.

A port of `spectre.js` by David Smith, Joseph Samuel Myers, Craig S. Kaplan and
Chaim Goodman-Strauss, which drives https://cs.uwaterloo.ca/~csk/spectre/app.html.
The nine labels, the eight placements per supertile and the substitution rules are
theirs; the coordinates here are exact where the original used floating point.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence

from .algebra import HALF_ROOT3, ZERO, Root3, cosine_sine
from .geometry import (
    IDENTITY,
    REFLECT_ACROSS_VERTICAL,
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

LABELS = (
    "Gamma",
    "Delta",
    "Theta",
    "Lambda",
    "Xi",
    "Pi",
    "Sigma",
    "Phi",
    "Psi",
)

PLAIN_LABELS = LABELS[1:]

#: Edge directions of the spectre, in whole twelfths of a turn.
SPECTRE_EDGES = (0, 10, 1, 3, 0, 2, 5, 7, 4, 6, 6, 8, 11, 9)

#: Edge directions of the hexagon, in whole twelfths of a turn.
HEXAGON_EDGES = (0, 2, 4, 6, 8, 10)

#: Which vertices align tiles with one another.
KEY_VERTICES = (3, 5, 7, 11)
HEXAGON_KEY_VERTICES = (1, 2, 3, 5)

#: `(turn in degrees, key of the previous tile, key of this one)`, walked in order to
#: place the eight tiles of a supertile.
TRANSFORM_RULES = (
    (60, 3, 1),
    (0, 2, 0),
    (60, 3, 1),
    (60, 3, 1),
    (0, 2, 0),
    (60, 3, 1),
    (-120, 3, 3),
)

#: Which label goes in each of the eight slots of each supertile.  `None` leaves the
#: slot empty, which is why Gamma grows more slowly than the rest.
SUPER_RULES: dict[str, tuple[str | None, ...]] = {
    "Gamma": ("Pi", "Delta", None, "Theta", "Sigma", "Xi", "Phi", "Gamma"),
    "Delta": ("Xi", "Delta", "Xi", "Phi", "Sigma", "Pi", "Phi", "Gamma"),
    "Theta": ("Psi", "Delta", "Pi", "Phi", "Sigma", "Pi", "Phi", "Gamma"),
    "Lambda": ("Psi", "Delta", "Xi", "Phi", "Sigma", "Pi", "Phi", "Gamma"),
    "Xi": ("Psi", "Delta", "Pi", "Phi", "Sigma", "Psi", "Phi", "Gamma"),
    "Pi": ("Psi", "Delta", "Xi", "Phi", "Sigma", "Psi", "Phi", "Gamma"),
    "Sigma": ("Xi", "Delta", "Xi", "Phi", "Sigma", "Pi", "Lambda", "Gamma"),
    "Phi": ("Psi", "Delta", "Psi", "Phi", "Sigma", "Pi", "Phi", "Gamma"),
    "Psi": ("Psi", "Delta", "Psi", "Phi", "Sigma", "Psi", "Phi", "Gamma"),
}

_CURVE_NEAR = Fraction(33, 100)
_CURVE_FAR = Fraction(67, 100)
_CURVE_DEPTH = Fraction(3, 5)


def unit_polygon(edges: Sequence[int]) -> tuple[Point, ...]:
    """The vertices of a closed equilateral polygon whose edges have unit length and
    run in the given directions, each a whole twelfth of a turn."""
    return tuple(
        walk([cosine_sine(30 * direction) for direction in edges], (ZERO, ZERO))[:-1]
    )


def curve_through(outline: Sequence[Point]) -> tuple[Point, ...]:
    """Control points bending each straight edge of a polygon into the cubic curve
    that turns Tile(1,1) into the true Spectre.

    The result starts with one point and continues in triples, each a pair of control
    points followed by the vertex they reach.  Successive edges bend the opposite way.
    """
    points = [outline[-1]]
    for index, vertex in enumerate(outline):
        previous = points[-1]
        along = (vertex[0] - previous[0], vertex[1] - previous[1])
        across = (-along[1], along[0])
        depth = _CURVE_DEPTH if index % 2 == 0 else -_CURVE_DEPTH
        points.extend(
            (
                previous[0] + step * along[0] + depth * across[0],
                previous[1] + step * along[1] + depth * across[1],
            )
            for step in (_CURVE_NEAR, _CURVE_FAR)
        )
        points.append(vertex)
    return tuple(points)


def _hexagonal_point(x: int, y: int) -> Point:
    """A point of the triangular lattice the hat and the turtle are drawn on."""
    return (Root3.of(x + Fraction(y, 2)), -HALF_ROOT3 * y)


HAT_LATTICE = (
    (-1, 2), (0, 2), (0, 3), (2, 2), (3, 0), (4, 0), (5, -1),
    (4, -2), (2, -1), (2, -2), (1, -2), (0, -2), (-1, -1), (0, 0),
)

TURTLE_LATTICE = (
    (0, 0), (2, -1), (3, 0), (4, -1), (4, -2), (6, -3), (7, -5),
    (6, -5), (5, -4), (4, -5), (2, -4), (0, -3), (-1, -1), (0, -1),
)


def _keys(outline: Sequence[Point], indices: Sequence[int]) -> tuple[Point, ...]:
    return tuple(outline[index] for index in indices)


def spectre_system(curved: bool = False) -> dict[str, Node]:
    """The nine unsubstituted spectre tiles.  `curved` gives the true Spectre, with
    cubic edges; otherwise the straight-edged Tile(1,1)."""
    outline = unit_polygon(SPECTRE_EDGES)
    keys = _keys(outline, KEY_VERTICES)
    curve = curve_through(outline) if curved else None
    mystic = Supertile(
        "Gamma",
        (
            (Tile("Gamma1", outline, keys, curve), IDENTITY),
            (
                Tile("Gamma2", outline, keys, curve),
                compose(
                    translation(*outline[8]), rotation(*cosine_sine(30))
                ),
            ),
        ),
        keys,
    )
    return {
        **{label: Tile(label, outline, keys, curve) for label in PLAIN_LABELS},
        "Gamma": mystic,
    }


def hexagon_system() -> dict[str, Node]:
    """The nine unsubstituted hexagons, the system Kaplan uses to show the
    substitution's combinatorics without the spectre's outline."""
    outline = unit_polygon(HEXAGON_EDGES)
    keys = _keys(outline, HEXAGON_KEY_VERTICES)
    return {label: Tile(label, outline, keys) for label in LABELS}


def hat_turtle_system(hat_dominant: bool = True) -> dict[str, Node]:
    """The nine unsubstituted tiles with hats and turtles in place of spectres, run
    through the spectre's substitution.

    This is Kaplan's "Turtles in Hats" and "Hats in Turtles", and it is not the
    H7/H8 hat tiling; for that see `spectre_explorer.hat`.
    """
    hat = tuple(_hexagonal_point(x, y) for x, y in HAT_LATTICE)
    turtle = tuple(_hexagonal_point(x, y) for x, y in TURTLE_LATTICE)
    hat_keys = _keys(hat, KEY_VERTICES)
    turtle_keys = _keys(turtle, KEY_VERTICES)

    if hat_dominant:
        outline, keys = hat, hat_keys
        companion = Tile("Gamma2", turtle, turtle_keys)
        placement = translation(*hat[8])
    else:
        outline, keys = turtle, turtle_keys
        companion = Tile("Gamma2", hat, hat_keys)
        placement = compose(translation(*turtle[9]), rotation(*cosine_sine(60)))

    mystic = Supertile(
        "Gamma",
        ((Tile("Gamma1", outline, keys), IDENTITY), (companion, placement)),
        keys,
    )
    return {
        **{label: Tile(label, outline, keys) for label in PLAIN_LABELS},
        "Gamma": mystic,
    }


def supertile_transforms(keys: Sequence[Point]) -> list[Transform]:
    """The eight placements within a supertile, derived by walking `TRANSFORM_RULES`
    from one key point to the next and then reflecting the whole arrangement."""
    transforms = [IDENTITY]
    turned = list(keys)
    turn = IDENTITY
    total = 0
    for angle, source, target in TRANSFORM_RULES:
        total += angle
        if angle != 0:
            turn = rotation(*cosine_sine(total))
            turned = [apply(turn, key) for key in keys]
        shift = translation_from_to(
            turned[target], apply(transforms[-1], keys[source])
        )
        transforms.append(compose(shift, turn))
    return [compose(REFLECT_ACROSS_VERTICAL, transform) for transform in transforms]


def substitute(system: dict[str, Node]) -> dict[str, Node]:
    """One round of substitution: nine supertiles built from the nine given nodes.

    The nodes are shared, not copied, so the result costs a fixed amount of memory
    however many tiles it stands for.
    """
    keys = system["Delta"].keys
    transforms = supertile_transforms(keys)
    super_keys = (
        apply(transforms[6], keys[2]),
        apply(transforms[5], keys[1]),
        apply(transforms[3], keys[2]),
        apply(transforms[0], keys[1]),
    )
    return {
        label: Supertile(
            label,
            tuple(
                (system[child], transforms[slot])
                for slot, child in enumerate(children)
                if child is not None
            ),
            super_keys,
        )
        for label, children in SUPER_RULES.items()
    }
