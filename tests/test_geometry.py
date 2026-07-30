"""Affine transforms of the plane."""

import pytest

from spectre_explorer.algebra import cosine_sine
from spectre_explorer.geometry import (
    IDENTITY,
    apply,
    compose,
    inverse,
    match_segments,
    point_to_float,
    rotation,
    translation,
    translation_from_to,
)

TURN = rotation(*cosine_sine(60))
SHIFT = translation(3, -2)


def test_the_identity_leaves_points_alone():
    assert apply(IDENTITY, (5, 7)) == (5, 7)


def test_composition_applies_the_inner_transform_first():
    point = (1, 0)
    assert point_to_float(apply(compose(SHIFT, TURN), point)) == pytest.approx(
        point_to_float(apply(SHIFT, apply(TURN, point)))
    )


def test_inverse_undoes_a_transform():
    combined = compose(SHIFT, TURN)
    there_and_back = compose(inverse(combined), combined)
    assert point_to_float(apply(there_and_back, (4, 9))) == pytest.approx((4.0, 9.0))


def test_twelve_sixty_degree_turns_come_back_round():
    total = IDENTITY
    for _ in range(6):
        total = compose(TURN, total)
    assert point_to_float(apply(total, (2, 5))) == pytest.approx((2.0, 5.0))


def test_translation_carries_one_point_to_another():
    assert apply(translation_from_to((1, 2), (4, 6)), (1, 2)) == (4, 6)


def test_matching_segments_carries_both_ends():
    transform = match_segments((0, 0), (1, 0), (2, 3), (2, 5))
    assert point_to_float(apply(transform, (0, 0))) == pytest.approx((2.0, 3.0))
    assert point_to_float(apply(transform, (1, 0))) == pytest.approx((2.0, 5.0))
