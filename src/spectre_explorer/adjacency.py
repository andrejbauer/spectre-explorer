"""Which tiles touch which.

A patch on its own is a list of placements that knows nothing about its own
structure.  Almost every question worth asking about these tilings is a question
about neighbors, so this turns a patch into a graph: tiles are vertices, and two
tiles are joined when they share a whole edge.

Vertices are matched by rounding, which is safe here because tile vertices are
either identical or a good fraction of an edge length apart.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterator

from .geometry import IDENTITY, apply, compose, point_to_float, rotation_about
from .tiling import Node, Placement, Rectangle, base_tiles, placements

Corner = tuple[float, float]

#: Decimal places used when deciding that two vertices are the same point.
PLACES = 6


@dataclass(frozen=True)
class Patch:
    """An expanded patch together with its adjacency graph."""

    placements: tuple[Placement, ...]
    outlines: tuple[tuple[Corner, ...], ...]
    neighbors: tuple[frozenset[int], ...]

    def __len__(self) -> int:
        return len(self.placements)

    def center(self, index: int) -> Corner:
        outline = self.outlines[index]
        return (
            sum(x for x, _ in outline) / len(outline),
            sum(y for _, y in outline) / len(outline),
        )

    def components(self) -> list[list[int]]:
        """The tiles grouped into edge-connected pieces."""
        seen: set[int] = set()
        found = []
        for start in range(len(self.placements)):
            if start not in seen:
                seen.add(start)
                piece = [start]
                stack = [start]
                while stack:
                    current = stack.pop()
                    for other in self.neighbors[current]:
                        if other not in seen:
                            seen.add(other)
                            piece.append(other)
                            stack.append(other)
                found.append(sorted(piece))
        return found

    def corners(self) -> dict[Corner, list[int]]:
        """Which tiles meet at each vertex of the patch."""
        meeting: dict[Corner, list[int]] = defaultdict(list)
        for index, outline in enumerate(self.outlines):
            for corner in outline:
                meeting[_rounded(corner)].append(index)
        return dict(meeting)


def _rounded(corner: Corner, places: int = PLACES) -> Corner:
    return (round(corner[0], places), round(corner[1], places))


def expand(root: Node, window: Rectangle | None = None) -> Patch:
    """Walk a patch and work out which of its tiles share edges."""
    shapes = base_tiles(root)
    found = tuple(placements(root, IDENTITY, window))
    outlines = tuple(
        tuple(
            point_to_float(apply(placement.transform, vertex))
            for vertex in shapes[placement.label].outline
        )
        for placement in found
    )

    meeting: dict[Corner, list[int]] = defaultdict(list)
    for index, outline in enumerate(outlines):
        for corner in outline:
            meeting[_rounded(corner)].append(index)

    together: dict[tuple[int, int], int] = defaultdict(int)
    for occupants in meeting.values():
        for position, one in enumerate(occupants):
            for other in occupants[position + 1 :]:
                together[(min(one, other), max(one, other))] += 1

    joined: list[set[int]] = [set() for _ in outlines]
    for (one, other), corners_shared in together.items():
        if corners_shared >= 2:
            joined[one].add(other)
            joined[other].add(one)

    return Patch(found, outlines, tuple(frozenset(entry) for entry in joined))


def star_triplets(patch: Patch, places: int = 5) -> Iterator[tuple[Corner, tuple[int, ...]]]:
    """Points where three tiles meet and the arrangement turns into itself under a
    third of a turn.

    Three tiles meeting at a point is the ordinary case in these tilings and says
    nothing; the three-fold symmetry is what picks out the star triplets that Boris
    Horvat's mega-objects are built from.

    Read the counts with care near the edge of a patch: a triplet needs its whole
    neighborhood, so a patch reports fewer of them per tile than the infinite tiling
    does, and the shortfall only fades slowly as generations grow.
    """
    third_of_a_turn = (-0.5, 0.8660254037844386)

    def written(transform) -> tuple[float, ...]:
        return tuple(round(float(entry), places) for entry in transform)

    for corner, occupants in patch.corners().items():
        group = tuple(sorted(set(occupants)))
        if len(group) == 3:
            turn = rotation_about(corner, *third_of_a_turn)
            here = {written(patch.placements[index].transform) for index in group}
            turned = {
                written(compose(turn, patch.placements[index].transform))
                for index in group
            }
            if here == turned:
                yield corner, group
