"""The tilings this package can build, and how to grow one.

Each system starts from a handful of labelled tiles and has a substitution that
replaces every label by a supertile of the same nine, or the same two.  Growing a
patch means applying the substitution a number of times and then picking one label
to draw.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from . import hat, spectre
from .tiling import Node, approximate


@dataclass(frozen=True)
class System:
    """One tiling: how to start it, how to grow it, and what it can be rooted at."""

    description: str
    start: Callable[[], dict[str, Node]]
    substitute: Callable[[dict[str, Node]], dict[str, Node]]
    categories: tuple[str, ...]
    default_category: str
    default_colours: str


SYSTEMS: dict[str, System] = {
    "tile11": System(
        "Tile(1,1), the straight-edged spectre",
        lambda: spectre.spectre_system(curved=False),
        spectre.substitute,
        spectre.LABELS,
        "Gamma",
        "mystics",
    ),
    "spectre": System(
        "the Spectre proper, with curved edges",
        lambda: spectre.spectre_system(curved=True),
        spectre.substitute,
        spectre.LABELS,
        "Gamma",
        "mystics",
    ),
    "hexagons": System(
        "hexagons in place of spectres, showing the substitution alone",
        spectre.hexagon_system,
        spectre.substitute,
        spectre.LABELS,
        "Gamma",
        "pride",
    ),
    "turtles-in-hats": System(
        "hats, with a turtle inside each mystic, on the spectre substitution",
        lambda: spectre.hat_turtle_system(hat_dominant=True),
        spectre.substitute,
        spectre.LABELS,
        "Gamma",
        "pride",
    ),
    "hats-in-turtles": System(
        "turtles, with a hat inside each mystic, on the spectre substitution",
        lambda: spectre.hat_turtle_system(hat_dominant=False),
        spectre.substitute,
        spectre.LABELS,
        "Gamma",
        "pride",
    ),
    "hat": System(
        "the hat on the H7/H8 substitution",
        lambda: hat.hat_system("hat"),
        hat.substitute,
        hat.LABELS,
        "H8",
        "grey",
    ),
    "turtle": System(
        "the turtle on the H7/H8 substitution",
        lambda: hat.hat_system("turtle"),
        hat.substitute,
        hat.LABELS,
        "H8",
        "grey",
    ),
}


def grow(name: str, generation: int) -> dict[str, Node]:
    """Apply a named system's substitution the given number of times."""
    system = SYSTEMS[name]
    tiles = system.start()
    for _ in range(generation):
        tiles = system.substitute(tiles)
    return tiles


def patch(
    name: str, category: str | None, generation: int, *, exact: bool = False
) -> Node:
    """One grown patch, ready to draw.

    Coordinates come back as floats unless `exact` is asked for, since walking a
    patch tile by tile is where the arithmetic happens and exact arithmetic there is
    thousands of times slower.
    """
    system = SYSTEMS[name]
    chosen = system.default_category if category is None else category
    root = grow(name, generation)[chosen]
    return root if exact else approximate(root)
