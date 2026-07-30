"""Exact arithmetic in the rationals adjoined the square root of three."""

from fractions import Fraction
from math import cos, radians, sin

import pytest

from spectre_explorer.algebra import HALF_ROOT3, ONE, ROOT3, ZERO, Root3, cosine_sine


def test_the_square_root_squares_to_three():
    assert ROOT3 * ROOT3 == Root3(Fraction(3), Fraction(0))


def test_division_undoes_multiplication():
    value = Root3(Fraction(3, 2), Fraction(-5, 7))
    other = Root3(Fraction(2), Fraction(1, 3))
    assert value * other / other == value


def test_integers_and_fractions_mix_in():
    assert 2 * ONE + Fraction(1, 2) == Root3(Fraction(5, 2), Fraction(0))
    assert ZERO - 1 == -ONE


def test_the_twelfths_agree_with_trigonometry():
    for degrees in range(-360, 721, 30):
        cosine, sine = cosine_sine(degrees)
        assert float(cosine) == pytest.approx(cos(radians(degrees)), abs=1e-15)
        assert float(sine) == pytest.approx(sin(radians(degrees)), abs=1e-15)


def test_the_twelfths_are_exact():
    assert cosine_sine(30) == (HALF_ROOT3, Root3(Fraction(1, 2), Fraction(0)))
    assert cosine_sine(90) == (ZERO, ONE)
    assert cosine_sine(390) == cosine_sine(30)


def test_angles_off_the_grid_are_refused():
    with pytest.raises(ValueError):
        cosine_sine(45)
