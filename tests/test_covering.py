"""Tiles cover their patch and do not overlap.

This is the property that makes the thing a tiling at all, and no count or reference
comparison catches its failure.  It needs `shapely`, which is in the `dev` extra.
"""

from __future__ import annotations

import pytest

shapely = pytest.importorskip("shapely")

from shapely.geometry import Polygon
from shapely.ops import unary_union

from spectre_explorer.geometry import apply, point_to_float
from spectre_explorer.systems import SYSTEMS, patch
from spectre_explorer.tiling import base_tiles, placements

STRAIGHT_EDGED = tuple(
    name for name in sorted(SYSTEMS) if name not in ("spectre", "hexagons")
)


def polygons(system: str, generation: int) -> list[Polygon]:
    root = patch(system, None, generation)
    shapes = base_tiles(root)
    return [
        Polygon(
            [
                point_to_float(apply(place.transform, vertex))
                for vertex in shapes[place.label].outline
            ]
        )
        for place in placements(root)
    ]


@pytest.mark.parametrize("system", STRAIGHT_EDGED)
def test_tiles_do_not_overlap(system):
    tiles = polygons(system, 2)
    total = sum(tile.area for tile in tiles)
    covered = unary_union(tiles).area
    assert covered == pytest.approx(total, rel=1e-9)


@pytest.mark.parametrize("system", STRAIGHT_EDGED)
def test_a_patch_has_no_gaps_inside_it(system):
    """The union may be pinched at a vertex, which splits it into pieces as far as
    shapely is concerned, and it picks up slivers of the size of a rounding error.
    What must not happen is a real hole."""
    covered = unary_union(polygons(system, 2))
    parts = list(covered.geoms) if covered.geom_type == "MultiPolygon" else [covered]
    holes = [Polygon(ring).area for part in parts for ring in part.interiors]
    assert max(holes, default=0.0) < 1e-9


@pytest.mark.parametrize("system", STRAIGHT_EDGED)
def test_a_patch_hangs_together_edge_to_edge(system):
    from spectre_explorer.adjacency import expand

    assert len(expand(patch(system, None, 3)).components()) == 1


def test_every_tile_has_the_same_area():
    tiles = polygons("tile11", 3)
    first = tiles[0].area
    for tile in tiles:
        assert tile.area == pytest.approx(first, rel=1e-9)
