"""Points and affine transforms of the plane.

A transform is the six-tuple `(a, b, c, d, e, f)` standing for the map
`(x, y) |-> (a x + b y + c, d x + e y + f)`.  Every operation here uses only
addition, subtraction, multiplication and division, so the same code serves both
`float` coordinates and the exact coordinates of `spectre_explorer.algebra`.
"""

from __future__ import annotations

from typing import Any, Iterable, Sequence

Point = tuple[Any, Any]
Transform = tuple[Any, Any, Any, Any, Any, Any]

IDENTITY: Transform = (1, 0, 0, 0, 1, 0)
REFLECT_ACROSS_VERTICAL: Transform = (-1, 0, 0, 0, 1, 0)


def compose(outer: Transform, inner: Transform) -> Transform:
    """The transform that applies `inner` and then `outer`."""
    return (
        outer[0] * inner[0] + outer[1] * inner[3],
        outer[0] * inner[1] + outer[1] * inner[4],
        outer[0] * inner[2] + outer[1] * inner[5] + outer[2],
        outer[3] * inner[0] + outer[4] * inner[3],
        outer[3] * inner[1] + outer[4] * inner[4],
        outer[3] * inner[2] + outer[4] * inner[5] + outer[5],
    )


def inverse(transform: Transform) -> Transform:
    """The inverse of an invertible transform."""
    a, b, c, d, e, f = transform
    determinant = a * e - b * d
    return (
        e / determinant,
        -b / determinant,
        (b * f - c * e) / determinant,
        -d / determinant,
        a / determinant,
        (c * d - a * f) / determinant,
    )


def apply(transform: Transform, point: Point) -> Point:
    """The image of a point."""
    a, b, c, d, e, f = transform
    x, y = point
    return (a * x + b * y + c, d * x + e * y + f)


def translation(dx: Any, dy: Any) -> Transform:
    """Translation by a displacement."""
    return (1, 0, dx, 0, 1, dy)


def rotation(cosine: Any, sine: Any) -> Transform:
    """Rotation about the origin, given the cosine and sine of the angle."""
    return (cosine, -sine, 0, sine, cosine, 0)


def rotation_about(point: Point, cosine: Any, sine: Any) -> Transform:
    """Rotation about a point, given the cosine and sine of the angle."""
    x, y = point
    return compose(
        translation(x, y), compose(rotation(cosine, sine), translation(-x, -y))
    )


def translation_from_to(source: Point, target: Point) -> Transform:
    """Translation carrying one point onto another."""
    return translation(target[0] - source[0], target[1] - source[1])


def match_segment(start: Point, end: Point) -> Transform:
    """The transform carrying the unit interval on the x-axis onto a segment."""
    px, py = start
    qx, qy = end
    return (qx - px, py - qy, px, qy - py, qx - px, py)


def match_segments(
    source_start: Point,
    source_end: Point,
    target_start: Point,
    target_end: Point,
) -> Transform:
    """The transform carrying one segment onto another."""
    return compose(
        match_segment(target_start, target_end),
        inverse(match_segment(source_start, source_end)),
    )


def to_float(transform: Transform) -> Transform:
    """The same transform with every entry converted to a float."""
    return tuple(float(entry) for entry in transform)  # type: ignore[return-value]


def point_to_float(point: Point) -> tuple[float, float]:
    """The same point with both coordinates converted to floats."""
    return (float(point[0]), float(point[1]))


def walk(directions: Iterable[tuple[Any, Any]], start: Point) -> list[Point]:
    """The vertices visited by starting at a point and following displacements."""
    vertices = [start]
    for dx, dy in directions:
        here = vertices[-1]
        vertices.append((here[0] + dx, here[1] + dy))
    return vertices


def bounding_box(points: Sequence[tuple[float, float]]) -> tuple[float, float, float, float]:
    """The smallest axis-aligned rectangle containing the points, as
    `(left, bottom, right, top)`."""
    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    return (min(xs), min(ys), max(xs), max(ys))
