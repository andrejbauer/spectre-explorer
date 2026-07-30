"""Colour maps, ported from the reference implementations.

A colour map sends a tile label to a red-green-blue triple.  The Spectre maps use
the nine substitution labels, splitting `Gamma` into the two halves of the mystic;
the Hat map uses the three labels of the H7/H8 system.
"""

from __future__ import annotations

Colour = tuple[int, int, int]
ColourMap = dict[str, Colour]

FIGURE_53: ColourMap = {
    "Gamma": (203, 157, 126),
    "Gamma1": (203, 157, 126),
    "Gamma2": (203, 157, 126),
    "Delta": (163, 150, 133),
    "Theta": (208, 215, 150),
    "Lambda": (184, 205, 178),
    "Xi": (211, 177, 144),
    "Pi": (218, 197, 161),
    "Sigma": (191, 146, 126),
    "Phi": (228, 213, 167),
    "Psi": (224, 223, 156),
}

BRIGHT: ColourMap = {
    "Gamma": (255, 255, 255),
    "Gamma1": (255, 255, 255),
    "Gamma2": (255, 255, 255),
    "Delta": (220, 220, 220),
    "Theta": (255, 191, 191),
    "Lambda": (255, 160, 122),
    "Xi": (255, 242, 0),
    "Pi": (135, 206, 250),
    "Sigma": (245, 245, 220),
    "Phi": (0, 255, 0),
    "Psi": (0, 255, 255),
}

MYSTICS: ColourMap = {
    "Gamma": (196, 201, 169),
    "Gamma1": (196, 201, 169),
    "Gamma2": (156, 160, 116),
    "Delta": (247, 252, 248),
    "Theta": (247, 252, 248),
    "Lambda": (247, 252, 248),
    "Xi": (247, 252, 248),
    "Pi": (247, 252, 248),
    "Sigma": (247, 252, 248),
    "Phi": (247, 252, 248),
    "Psi": (247, 252, 248),
}

PRIDE: ColourMap = {
    "Gamma": (255, 255, 255),
    "Gamma1": (97, 57, 21),
    "Gamma2": (0, 0, 0),
    "Delta": (2, 129, 33),
    "Theta": (0, 76, 255),
    "Lambda": (118, 0, 136),
    "Xi": (229, 0, 0),
    "Pi": (255, 175, 199),
    "Sigma": (115, 215, 238),
    "Phi": (255, 141, 0),
    "Psi": (255, 238, 0),
}

GREY: ColourMap = {
    "single": (255, 255, 255),
    "unflipped": (200, 200, 200),
    "flipped": (150, 150, 150),
}

BY_NAME: dict[str, ColourMap] = {
    "pride": PRIDE,
    "mystics": MYSTICS,
    "fig53": FIGURE_53,
    "bright": BRIGHT,
    "grey": GREY,
}

FALLBACK: Colour = (200, 200, 200)


def colour_of(colour_map: ColourMap, label: str) -> Colour:
    """The colour of a label, or a neutral grey for a label the map does not name."""
    return colour_map.get(label, FALLBACK)


def to_css(colour: Colour) -> str:
    """A colour written the way SVG wants it."""
    return f"rgb({colour[0]},{colour[1]},{colour[2]})"
