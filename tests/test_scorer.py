"""Tests for fontpair scorer."""

from __future__ import annotations

from pathlib import Path

import pytest

from fontpair.models import FontCategory, FontInfo, FontMetrics
from fontpair.scorer import score_pairing

FIXTURES = Path(__file__).parent / "fixtures" / "test_fonts"


def _info(family: str, cat: FontCategory, weight: int = 400, xh: float = 0.5) -> FontInfo:
    return FontInfo(
        family=family,
        style="Regular",
        weight=weight,
        width=5,
        file_path=Path("/fake/font.ttf"),
        category=cat,
        metrics=FontMetrics(x_height_ratio=xh, weight=weight, avg_width=500.0, contrast=0.1),
    )


def test_serif_sans_high_harmony() -> None:
    heading = _info("Heading", FontCategory.SERIF, 700, 0.48)
    body = _info("Body", FontCategory.SANS_SERIF, 400, 0.50)
    score = score_pairing(heading, body)
    assert score.visual_harmony >= 85
    assert score.total >= 60


def test_same_family_penalty() -> None:
    h = _info("Arial", FontCategory.SANS_SERIF, 700, 0.50)
    b = _info("Arial", FontCategory.SANS_SERIF, 400, 0.50)
    score = score_pairing(h, b)
    assert score.visual_harmony < 70


def test_monospace_body_lower_readability() -> None:
    heading = _info("Heading", FontCategory.SANS_SERIF, 700)
    body = _info("Body", FontCategory.MONOSPACE, 400)
    score = score_pairing(heading, body)
    assert score.readability < 90


def test_good_x_height_compatibility() -> None:
    heading = _info("H", FontCategory.SERIF, 700, 0.48)
    body = _info("B", FontCategory.SANS_SERIF, 400, 0.50)
    score = score_pairing(heading, body)
    assert score.x_height_compat >= 80


def test_poor_x_height_compatibility() -> None:
    heading = _info("H", FontCategory.DISPLAY, 900, 0.30)
    body = _info("B", FontCategory.SANS_SERIF, 300, 0.65)
    score = score_pairing(heading, body)
    assert score.x_height_compat < 50


def test_weight_contrast_balance() -> None:
    heading = _info("H", FontCategory.SERIF, 800, 0.48)
    body = _info("B", FontCategory.SANS_SERIF, 300, 0.50)
    score = score_pairing(heading, body)
    assert score.contrast_balance >= 75
