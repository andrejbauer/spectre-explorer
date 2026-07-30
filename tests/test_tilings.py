"""Tile counts, congruence and the shape of the substitution graph."""

import pytest

from spectre_explorer.geometry import apply, point_to_float
from spectre_explorer.systems import SYSTEMS, grow, patch
from spectre_explorer.tiling import Supertile, base_tiles, placements, tile_count

SPECTRE_COUNTS = {
    "Gamma": (2, 8, 62, 488, 3842, 30248, 238142, 1874888),
    "Delta": (1, 9, 71, 559, 4401, 34649, 272791, 2147679),
}

HAT_COUNTS = {
    "H8": (1, 8, 55, 377, 2584, 17711, 121393),
    "H7": (2, 7, 47, 322, 2207, 15127, 103682),
}


@pytest.mark.parametrize("category,expected", SPECTRE_COUNTS.items())
def test_spectre_tile_counts(category, expected):
    tiles = SYSTEMS["tile11"].start()
    for generation, count in enumerate(expected):
        assert tile_count(tiles[category]) == count, f"generation {generation}"
        tiles = SYSTEMS["tile11"].substitute(tiles)


@pytest.mark.parametrize("category,expected", HAT_COUNTS.items())
def test_hat_tile_counts(category, expected):
    tiles = SYSTEMS["hat"].start()
    for generation, count in enumerate(expected):
        assert tile_count(tiles[category]) == count, f"generation {generation}"
        tiles = SYSTEMS["hat"].substitute(tiles)


def test_the_hexagon_system_counts_one_tile_where_the_spectre_counts_a_mystic():
    """Gamma is a single hexagon rather than a pair of spectres, and its empty slot
    stays empty, so the counts run 1, 7, 55, 433 rather than 2, 8, 62, 488."""
    tiles = SYSTEMS["hexagons"].start()
    for count in (1, 7, 55, 433, 3409):
        assert tile_count(tiles["Gamma"]) == count
        tiles = SYSTEMS["hexagons"].substitute(tiles)


@pytest.mark.parametrize("name", sorted(SYSTEMS))
def test_walking_a_patch_yields_exactly_its_tiles(name):
    root = patch(name, None, 3)
    assert sum(1 for _ in placements(root)) == tile_count(root)


@pytest.mark.parametrize("name", sorted(SYSTEMS))
def test_every_tile_is_placed_by_an_isometry(name):
    """A tile may be turned and flipped but never stretched, so the linear part of
    every placement is orthogonal with determinant of size one."""
    root = patch(name, None, 3)
    for placement in placements(root):
        a, b, c, d, e, f = (float(entry) for entry in placement.transform)
        assert a * a + d * d == pytest.approx(1.0)
        assert b * b + e * e == pytest.approx(1.0)
        assert a * b + d * e == pytest.approx(0.0, abs=1e-12)
        assert abs(a * e - b * d) == pytest.approx(1.0)


def test_the_spectre_has_fourteen_unit_edges():
    tile = base_tiles(patch("tile11", None, 0))["Gamma1"]
    corners = [point_to_float(vertex) for vertex in tile.outline]
    assert len(corners) == 14
    for index, (x, y) in enumerate(corners):
        nx, ny = corners[(index + 1) % 14]
        assert ((nx - x) ** 2 + (ny - y) ** 2) ** 0.5 == pytest.approx(1.0)


def test_the_graph_is_shared_rather_than_copied():
    """Two supertiles of the same round must hold the very same child objects, which
    is what keeps memory flat as generations grow."""
    tiles = grow("tile11", 3)
    delta = {id(child) for child, _ in tiles["Delta"].children}
    psi = {id(child) for child, _ in tiles["Psi"].children}
    assert delta & psi


def test_memory_does_not_grow_with_the_tile_count():
    tiles = grow("tile11", 8)
    counted: set[int] = set()

    def visit(node):
        if id(node) not in counted:
            counted.add(id(node))
            if isinstance(node, Supertile):
                for child, _ in node.children:
                    visit(child)

    visit(tiles["Gamma"])
    assert tile_count(tiles["Gamma"]) > 10_000_000
    assert len(counted) < 100
