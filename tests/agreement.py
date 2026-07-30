"""Deciding whether two collections of polygons describe the same tiling.

An export from one of Kaplan's apps carries whatever zoom and pan the app happened
to be at, so the two collections agree only up to a similarity.  Two corresponding
points fix that similarity; after that every tile has to line up.  Tiles are paired
by position and outlines are compared cyclically, because neither the order of the
tiles nor the starting vertex of an outline is meaningful.
"""

from __future__ import annotations

import re
from typing import Sequence

Polygon = tuple[complex, ...]


def read_polygons(text: str) -> list[Polygon]:
    """Every `<polygon>` in an SVG document, as written."""
    return [
        tuple(
            complex(float(x), float(y))
            for x, y in (pair.split(",") for pair in match.group(1).split())
        )
        for match in re.finditer(r'<polygon points="([^"]+)"', text)
    ]


def expand_uses(text: str) -> list[Polygon]:
    """Every polygon of a document that defines outlines once and places them by
    reference, with the root `scale(1,-1)` applied."""
    shapes = {
        match.group(1): [
            complex(float(x), float(y))
            for x, y in (pair.split(",") for pair in match.group(2).split())
        ]
        for match in re.finditer(r'<polygon id="([^"]+)" points="([^"]+)"', text)
    }
    placed = []
    for identifier, numbers in re.findall(
        r'<use href="#([^"]+)" transform="matrix\(([^)]+)\)"', text
    ):
        a, b, c, d, e, f = (float(value) for value in numbers.split(","))
        placed.append(
            tuple(
                complex(a * z.real + c * z.imag + e, -(b * z.real + d * z.imag + f))
                for z in shapes[identifier]
            )
        )
    return placed


def centroid(polygon: Polygon) -> complex:
    return sum(polygon) / len(polygon)


def _anchors(polygons: Sequence[Polygon]) -> tuple[complex, complex]:
    centers = [centroid(polygon) for polygon in polygons]
    middle = sum(centers) / len(centers)
    return middle, max(centers, key=lambda center: abs(center - middle))


class Nearest:
    """Nearest-point lookup over a fixed set of points, on a uniform grid."""

    def __init__(self, points: Sequence[complex], cell: float) -> None:
        self.cell = cell
        self.buckets: dict[tuple[int, int], list[tuple[complex, int]]] = {}
        for index, point in enumerate(points):
            self.buckets.setdefault(self._key(point), []).append((point, index))

    def _key(self, point: complex) -> tuple[int, int]:
        return (int(point.real // self.cell), int(point.imag // self.cell))

    def of(self, point: complex) -> tuple[complex, int] | None:
        column, row = self._key(point)
        candidates = [
            entry
            for across in (-1, 0, 1)
            for down in (-1, 0, 1)
            for entry in self.buckets.get((column + across, row + down), ())
        ]
        return (
            min(candidates, key=lambda entry: abs(entry[0] - point))
            if candidates
            else None
        )


def outline_deviation(one: Sequence[complex], other: Sequence[complex]) -> float:
    """How far two closed outlines are from each other, allowing the vertex list to
    start anywhere and to run either way round."""
    count = len(one)
    return min(
        max(
            abs(one[index] - ordering[(index + offset) % count])
            for index in range(count)
        )
        for ordering in (list(other), list(reversed(other)))
        for offset in range(count)
    )


def deviation(mine: Sequence[Polygon], theirs: Sequence[Polygon]) -> float | None:
    """The worst distance between corresponding vertices once the two collections are
    brought into register, measured in the units of `theirs`, or `None` if they are
    not the same tiling at all."""
    if len(mine) != len(theirs):
        return None
    source_center, source_far = _anchors(mine)
    target_center, target_far = _anchors(theirs)
    target_centers = [centroid(polygon) for polygon in theirs]
    first = target_centers[0]
    cell = min(abs(other - first) for other in target_centers[1:])
    index = Nearest(target_centers, cell)

    for flip in (lambda z: z, lambda z: z.conjugate()):
        scale = (target_far - target_center) / (flip(source_far) - flip(source_center))
        place = lambda z: target_center + scale * (flip(z) - flip(source_center))
        pairs = []
        for polygon in mine:
            wanted = place(centroid(polygon))
            found = index.of(wanted)
            if found is None or abs(found[0] - wanted) > cell / 2:
                pairs = None
                break
            pairs.append((polygon, theirs[found[1]]))
        if pairs is not None and len({found for _, found in pairs}) == len(theirs):
            return max(
                outline_deviation([place(vertex) for vertex in ours], target)
                for ours, target in pairs
            )
    return None


def scale_between(mine: Sequence[Polygon], theirs: Sequence[Polygon]) -> float:
    """How much larger the second collection is than the first."""
    source_center, source_far = _anchors(mine)
    target_center, target_far = _anchors(theirs)
    return abs(target_far - target_center) / abs(source_far - source_center)
