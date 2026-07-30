"""Exact arithmetic in the field obtained by adjoining the square root of three
to the rationals.

Every vertex of every tile in this package, and every transform that places one,
lies in this field, so the whole construction can be carried out without rounding.
Rounding happens once, when a picture is written.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Union

Rational = Union[int, Fraction]
Scalar = Union[int, Fraction, "Root3"]


@dataclass(frozen=True, slots=True, order=False)
class Root3:
    """The number `rational + radical * sqrt(3)`."""

    rational: Fraction
    radical: Fraction

    @staticmethod
    def of(value: Scalar) -> Root3:
        """Read any supported scalar as an element of the field."""
        return (
            value
            if isinstance(value, Root3)
            else Root3(Fraction(value), Fraction(0))
        )

    def __add__(self, other: Scalar) -> Root3:
        that = Root3.of(other)
        return Root3(self.rational + that.rational, self.radical + that.radical)

    def __radd__(self, other: Scalar) -> Root3:
        return self + other

    def __sub__(self, other: Scalar) -> Root3:
        that = Root3.of(other)
        return Root3(self.rational - that.rational, self.radical - that.radical)

    def __rsub__(self, other: Scalar) -> Root3:
        return Root3.of(other) - self

    def __neg__(self) -> Root3:
        return Root3(-self.rational, -self.radical)

    def __mul__(self, other: Scalar) -> Root3:
        that = Root3.of(other)
        return Root3(
            self.rational * that.rational + 3 * self.radical * that.radical,
            self.rational * that.radical + self.radical * that.rational,
        )

    def __rmul__(self, other: Scalar) -> Root3:
        return self * other

    def __truediv__(self, other: Scalar) -> Root3:
        that = Root3.of(other)
        norm = that.rational * that.rational - 3 * that.radical * that.radical
        return self * Root3(that.rational / norm, -that.radical / norm)

    def __rtruediv__(self, other: Scalar) -> Root3:
        return Root3.of(other) / self

    def __float__(self) -> float:
        return float(self.rational) + float(self.radical) * 1.7320508075688772

    def __repr__(self) -> str:
        return f"Root3({self.rational}, {self.radical})"


ZERO = Root3(Fraction(0), Fraction(0))
ONE = Root3(Fraction(1), Fraction(0))
HALF = Root3(Fraction(1, 2), Fraction(0))
ROOT3 = Root3(Fraction(0), Fraction(1))
HALF_ROOT3 = Root3(Fraction(0), Fraction(1, 2))

_TWELFTHS: tuple[tuple[Root3, Root3], ...] = (
    (ONE, ZERO),
    (HALF_ROOT3, HALF),
    (HALF, HALF_ROOT3),
    (ZERO, ONE),
    (-HALF, HALF_ROOT3),
    (-HALF_ROOT3, HALF),
    (-ONE, ZERO),
    (-HALF_ROOT3, -HALF),
    (-HALF, -HALF_ROOT3),
    (ZERO, -ONE),
    (HALF, -HALF_ROOT3),
    (HALF_ROOT3, -HALF),
)


def cosine_sine(degrees: int) -> tuple[Root3, Root3]:
    """Exact cosine and sine of an angle that is a whole multiple of 30 degrees."""
    twelfth, remainder = divmod(degrees % 360, 30)
    if remainder == 0:
        return _TWELFTHS[twelfth]
    else:
        raise ValueError(
            f"{degrees} degrees is not a multiple of 30, so it has no exact "
            "representation in this field"
        )
