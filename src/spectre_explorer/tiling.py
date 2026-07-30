"""The shared structure of a substitution tiling.

A tiling is a directed acyclic graph.  A `Tile` is a leaf, a single polygon.  A
`Supertile` places other nodes by affine transforms, and the same node may appear in
many supertiles, so one round of substitution costs a fixed amount of memory however
many tiles it adds.  Walking the graph with `placements` expands it lazily.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Iterator, NamedTuple, Union

from .geometry import (
    IDENTITY,
    Point,
    Transform,
    apply,
    compose,
    point_to_float,
    to_float,
)

Rectangle = tuple[float, float, float, float]


@dataclass(frozen=True, eq=False)
class Tile:
    """A single polygon, the leaf of a substitution."""

    label: str
    outline: tuple[Point, ...]
    keys: tuple[Point, ...]
    curve: tuple[Point, ...] | None = None


@dataclass(frozen=True, eq=False)
class Supertile:
    """A labelled collection of nodes, each placed by a transform."""

    label: str
    children: tuple[tuple["Node", Transform], ...]
    keys: tuple[Point, ...] = field(default=())


Node = Union[Tile, Supertile]


class Placement(NamedTuple):
    """One leaf tile of an expanded tiling.

    `ancestry` runs from the outermost supertile to the tile itself, so
    `ancestry[-1]` is the tile's own label and `ancestry[0]` names the whole patch.
    """

    label: str
    transform: Transform
    ancestry: tuple[str, ...]


@lru_cache(maxsize=None)
def tile_count(node: Node) -> int:
    """How many leaf tiles the node expands into."""
    match node:
        case Tile():
            return 1
        case Supertile():
            return sum(tile_count(child) for child, _ in node.children)


@lru_cache(maxsize=None)
def bounds(node: Node) -> Rectangle:
    """The smallest axis-aligned rectangle holding the node, in its own coordinates,
    as `(left, bottom, right, top)`.

    For a supertile this is the box around the boxes of its children, which can be
    larger than the true box but never smaller, so it is safe for cropping.
    """
    match node:
        case Tile():
            corners = [point_to_float(vertex) for vertex in node.outline]
        case Supertile():
            corners = [
                corner
                for child, transform in node.children
                for corner in _corners(bounds(child), transform)
            ]
    return (
        min(x for x, _ in corners),
        min(y for _, y in corners),
        max(x for x, _ in corners),
        max(y for _, y in corners),
    )


def _corners(rectangle: Rectangle, transform: Transform) -> list[tuple[float, float]]:
    left, bottom, right, top = rectangle
    return [
        point_to_float(apply(transform, corner))
        for corner in ((left, bottom), (right, bottom), (right, top), (left, top))
    ]


def _meets(one: Rectangle, other: Rectangle) -> bool:
    return (
        one[0] <= other[2]
        and other[0] <= one[2]
        and one[1] <= other[3]
        and other[1] <= one[3]
    )


def placements(
    node: Node,
    transform: Transform = IDENTITY,
    window: Rectangle | None = None,
    ancestry: tuple[str, ...] = (),
) -> Iterator[Placement]:
    """Yield a `Placement` for every leaf tile, in the order the substitution builds
    them.

    When `window` is given, tiles outside it are skipped, and any supertile whose box
    misses the window is skipped whole, so cropping a deep patch costs about what
    generating the visible part costs.
    """
    visible = window is None or _meets(
        window, _box(_corners(bounds(node), transform))
    )
    if visible:
        match node:
            case Tile():
                yield Placement(node.label, transform, ancestry + (node.label,))
            case Supertile():
                for child, placement in node.children:
                    yield from placements(
                        child,
                        compose(transform, placement),
                        window,
                        ancestry + (node.label,),
                    )


def _box(corners: list[tuple[float, float]]) -> Rectangle:
    return (
        min(x for x, _ in corners),
        min(y for _, y in corners),
        max(x for x, _ in corners),
        max(y for _, y in corners),
    )


def base_tiles(node: Node) -> dict[str, Tile]:
    """Every distinct leaf tile reachable from the node, keyed by label.

    Tiles that share a label share an outline, so this is what a drawing back end
    needs to define once and then reference."""
    match node:
        case Tile():
            return {node.label: node}
        case Supertile():
            return {
                label: tile
                for child, _ in node.children
                for label, tile in base_tiles(child).items()
            }


def approximate(root: Node) -> Node:
    """The same tiling with every coordinate and transform converted to a float.

    The substitution is built with exact arithmetic, which costs nothing because a
    graph holds only a handful of nodes per round.  Walking it does the arithmetic
    once per tile, where exactness would cost everything, so convert first.  Sharing
    is preserved, so this is as cheap as the graph is small.
    """
    converted: dict[int, Node] = {}

    def convert(node: Node) -> Node:
        if id(node) not in converted:
            match node:
                case Tile():
                    converted[id(node)] = Tile(
                        node.label,
                        tuple(point_to_float(point) for point in node.outline),
                        tuple(point_to_float(point) for point in node.keys),
                        None
                        if node.curve is None
                        else tuple(point_to_float(point) for point in node.curve),
                    )
                case Supertile():
                    converted[id(node)] = Supertile(
                        node.label,
                        tuple(
                            (convert(child), to_float(transform))
                            for child, transform in node.children
                        ),
                        tuple(point_to_float(point) for point in node.keys),
                    )
        return converted[id(node)]

    return convert(root)


def expand(system: dict[str, Node], rounds: int, substitute) -> dict[str, Node]:
    """Apply a substitution the given number of times."""
    for _ in range(rounds):
        system = substitute(system)
    return system
