"""Authoritative print-trim catalog shared by metadata, doctor, and covers.

KDP limits were checked against "Set Trim Size, Bleed, and Margins"
(GVBQ3CMEQW3W2VL6) on 2026-08-29.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrimSpec:
    width: float
    height: float
    family: str
    kdp_large: bool
    kdp_hardcover: bool
    recommended_base_size: int
    paperback_max: dict[str, int]


def _max(white: int, cream: int, groundwood: int,
         standard: int, premium: int) -> dict[str, int]:
    return {
        "white": white, "cream": cream, "groundwood": groundwood,
        "standard-color": standard, "premium-color": premium,
    }


TRIM_CATALOG = {
    "5x8": TrimSpec(5.0, 8.0, "compact", False, False, 10,
                    _max(828, 776, 812, 600, 828)),
    "5.5x8.5": TrimSpec(5.5, 8.5, "compact", False, True, 10,
                       _max(828, 776, 812, 600, 828)),
    "6x9": TrimSpec(6.0, 9.0, "trade", False, True, 11,
                    _max(828, 776, 812, 600, 828)),
    "7x10": TrimSpec(7.0, 10.0, "technical", True, True, 11,
                     _max(828, 776, 812, 600, 828)),
    "7.5x9.25": TrimSpec(7.5, 9.25, "technical-wide", True, False, 11,
                        _max(828, 776, 812, 600, 828)),
    "8x10": TrimSpec(8.0, 10.0, "technical-wide", True, False, 11,
                     _max(828, 776, 812, 600, 828)),
    "8.25x11": TrimSpec(8.25, 11.0, "large-textbook", True, True, 12,
                        _max(800, 750, 784, 600, 800)),
    "8.5x11": TrimSpec(8.5, 11.0, "large-textbook", True, False, 12,
                       _max(590, 550, 578, 600, 590)),
}

TRIM_PRESETS = {
    name: (spec.width, spec.height) for name, spec in TRIM_CATALOG.items()
}
KDP_HARDCOVER_MIN_PAGES = 75
KDP_HARDCOVER_MAX_PAGES = 550
