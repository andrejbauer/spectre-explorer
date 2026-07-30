"""Writing a tiling as SVG.

Three encodings of the same picture:

`use`
    Each distinct tile outline is defined once, and each tile is one `<use>` element
    carrying a transform.  About a seventh of the size of the reference app's export
    and the right default.
`flat`
    A `<polygon>` or `<path>` per tile, with its coordinates written out.  Larger,
    but every tool understands it.
`nested`
    One group per node of the substitution graph, referring to the groups one round
    below.  The file then grows with the number of rounds rather than the number of
    tiles, so even generation 8 is a few kilobytes.  Renderers still expand it, so
    this shrinks the file and not the drawing time.

Coordinates are written in tile units, with the size of the picture carried by the
root `viewBox`, so the precision needed does not change with the depth of the patch.
"""

from __future__ import annotations

from typing import Callable, IO, Iterable

from dataclasses import dataclass

from .colours import Colour, ColourMap, colour_of, to_css
from .geometry import IDENTITY, Transform, apply, point_to_float
from .tiling import (
    Node,
    Placement,
    Rectangle,
    Supertile,
    Tile,
    base_tiles,
    bounds,
    placements,
    tile_count,
)

#: The linear part of a transform is one of a couple of dozen exact values, so it
#: costs almost nothing to write it accurately whatever the coordinate precision is.
LINEAR_DIGITS = 6

Chooser = Callable[[Placement], Colour]


@dataclass(frozen=True)
class Painting:
    """How tiles are coloured, and which coloured outlines a document must define."""

    colour: Chooser
    definitions: Callable[[Iterable[str]], list[tuple[str, Colour]]]


def by_label(colour_map: ColourMap) -> Painting:
    """Colour every tile by its own label."""
    return Painting(
        colour=lambda placement: colour_of(colour_map, placement.label),
        definitions=lambda labels: [
            (label, colour_of(colour_map, label)) for label in labels
        ],
    )


def by_ancestor(colour_map: ColourMap, levels: int) -> Painting:
    """Colour every tile by the label of the supertile the given number of rounds
    above it, which shows the fractal structure of the substitution."""

    def colour(placement: Placement) -> Colour:
        depth = min(levels, len(placement.ancestry) - 1)
        return colour_of(colour_map, placement.ancestry[-1 - depth])

    palette = sorted(set(colour_map.values()))
    return Painting(
        colour=colour,
        definitions=lambda labels: [
            (label, shade) for label in labels for shade in palette
        ],
    )


def number(value: float, digits: int) -> str:
    """A coordinate written as briefly as the requested precision allows."""
    text = f"{value:.{digits}f}"
    trimmed = text.rstrip("0").rstrip(".") if "." in text else text
    return "0" if trimmed in ("", "-", "-0") else trimmed


def _outline_data(tile: Tile, digits: int) -> tuple[str, str]:
    """The element name and geometry attribute drawing one tile at the origin."""
    if tile.curve is None:
        points = " ".join(
            f"{number(x, digits)},{number(y, digits)}"
            for x, y in map(point_to_float, tile.outline)
        )
        return "polygon", f'points="{points}"'
    else:
        vertices = [point_to_float(point) for point in tile.curve]
        start = f"M {number(vertices[0][0], digits)} {number(vertices[0][1], digits)}"
        curves = " ".join(
            "C "
            + " ".join(
                f"{number(x, digits)} {number(y, digits)}"
                for x, y in vertices[index : index + 3]
            )
            for index in range(1, len(vertices), 3)
        )
        return "path", f'd="{start} {curves} Z"'


def _matrix(transform: Transform, digits: int) -> str:
    a, b, c, d, e, f = (float(entry) for entry in transform)
    return (
        "matrix("
        + ",".join(
            (
                number(a, LINEAR_DIGITS),
                number(d, LINEAR_DIGITS),
                number(b, LINEAR_DIGITS),
                number(e, LINEAR_DIGITS),
                number(c, digits),
                number(f, digits),
            )
        )
        + ")"
    )


def _view(rectangle: Rectangle, margin: float) -> tuple[float, float, float, float]:
    left, bottom, right, top = rectangle
    return (
        left - margin,
        -(top + margin),
        (right - left) + 2 * margin,
        (top - bottom) + 2 * margin,
    )


def _header(
    view: tuple[float, float, float, float], pixel_width: int, title: str, digits: int
) -> Iterable[str]:
    x, y, width, height = view
    yield '<?xml version="1.0" encoding="UTF-8"?>\n'
    yield (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{number(x, digits)} {number(y, digits)} '
        f'{number(width, digits)} {number(height, digits)}" '
        f'width="{pixel_width}" height="{round(pixel_width * height / width)}">\n'
    )
    yield f"<title>{title}</title>\n"


def write(
    stream: IO[str],
    root: Node,
    *,
    mode: str = "use",
    colour_map: ColourMap,
    painting: Painting | None = None,
    precision: int = 3,
    stroke_width: float = 0.02,
    stroke: str = "black",
    window: Rectangle | None = None,
    pixel_width: int = 1000,
    title: str = "Aperiodic tiling",
) -> int:
    """Write a tiling and return the number of tiles written."""
    painted = by_label(colour_map) if painting is None else painting
    view = _view(window if window is not None else bounds(root), 1.0)
    for piece in _header(view, pixel_width, title, precision):
        stream.write(piece)

    shapes = base_tiles(root)
    opening = (
        f'<g transform="scale(1,-1)" stroke="{stroke}" '
        f'stroke-width="{number(stroke_width, 4)}" stroke-linejoin="round">\n'
    )

    if mode == "flat":
        count = _write_flat(stream, root, shapes, painted, precision, window, opening)
    elif mode == "use":
        count = _write_uses(stream, root, shapes, painted, precision, window, opening)
    elif mode == "nested":
        count = _write_nested(stream, root, shapes, colour_map, precision, opening)
    else:
        raise ValueError(f"unknown SVG mode {mode!r}")

    stream.write("</g>\n</svg>\n")
    return count


def _write_flat(stream, root, shapes, painted, precision, window, opening) -> int:
    stream.write(opening)
    count = 0
    for placement in placements(root, IDENTITY, window):
        tile = shapes[placement.label]
        moved = Tile(
            tile.label,
            tuple(apply(placement.transform, point) for point in tile.outline),
            tile.keys,
            None
            if tile.curve is None
            else tuple(apply(placement.transform, point) for point in tile.curve),
        )
        element, geometry = _outline_data(moved, precision)
        fill = to_css(painted.colour(placement))
        stream.write(f'<{element} {geometry} fill="{fill}"/>\n')
        count += 1
    return count


def _write_uses(stream, root, shapes, painted, precision, window, opening) -> int:
    drawings = {
        label: _outline_data(tile, precision) for label, tile in shapes.items()
    }
    defined: dict[tuple[str, str, Colour], str] = {}
    identifiers: dict[tuple[str, Colour], str] = {}
    for label, colour in painted.definitions(shapes):
        element, geometry = drawings[label]
        identifiers[(label, colour)] = defined.setdefault(
            (element, geometry, colour), f"s{len(defined)}"
        )

    stream.write("<defs>\n")
    for (element, geometry, colour), identifier in defined.items():
        stream.write(
            f'<{element} id="{identifier}" {geometry} fill="{to_css(colour)}"/>\n'
        )
    stream.write("</defs>\n")
    stream.write(opening)
    count = 0
    for placement in placements(root, IDENTITY, window):
        identifier = identifiers[(placement.label, painted.colour(placement))]
        stream.write(
            f'<use href="#{identifier}" '
            f'transform="{_matrix(placement.transform, precision)}"/>\n'
        )
        count += 1
    return count


def _write_nested(stream, root, shapes, colour_map, precision, opening) -> int:
    """Emit one group per node of the substitution graph.

    Tiles are coloured by their own label here, because sharing a group between
    supertiles is exactly what makes colouring by ancestry impossible.
    """
    order: list[Node] = []
    seen: set[int] = set()

    def visit(node: Node) -> None:
        if id(node) not in seen:
            seen.add(id(node))
            match node:
                case Tile():
                    pass
                case Supertile():
                    for child, _ in node.children:
                        visit(child)
            order.append(node)

    visit(root)
    identifiers = {id(node): f"n{index}" for index, node in enumerate(order)}

    stream.write("<defs>\n")
    for node in order:
        match node:
            case Tile():
                element, geometry = _outline_data(node, precision)
                fill = to_css(colour_of(colour_map, node.label))
                stream.write(
                    f'<{element} id="{identifiers[id(node)]}" {geometry} '
                    f'fill="{fill}"/>\n'
                )
            case Supertile():
                stream.write(f'<g id="{identifiers[id(node)]}">')
                for child, transform in node.children:
                    stream.write(
                        f'<use href="#{identifiers[id(child)]}" '
                        f'transform="{_matrix(transform, precision)}"/>'
                    )
                stream.write("</g>\n")
    stream.write("</defs>\n")
    stream.write(opening)
    stream.write(f'<use href="#{identifiers[id(root)]}"/>\n')
    return tile_count(root)
