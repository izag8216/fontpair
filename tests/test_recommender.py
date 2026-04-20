"""Tests for fontpair recommender."""

from __future__ import annotations

from pathlib import Path

import pytest

from fontpair.models import FontCategory, FontInfo, FontMetrics, RecommendOptions
from fontpair.recommender import recommend


def _info(family: str, cat: FontCategory, weight: int = 400) -> FontInfo:
    return FontInfo(
        family=family,
        style="Regular" if weight <= 400 else "Bold",
        weight=weight,
        width=5,
        file_path=Path(f"/fake/{family}.ttf"),
        category=cat,
        metrics=FontMetrics(x_height_ratio=0.50, weight=weight, avg_width=500.0, contrast=0.1),
    )


@pytest.fixture
def font_pool() -> list[FontInfo]:
    return [
        _info("Playfair", FontCategory.SERIF, 700),
        _info("Playfair", FontCategory.SERIF, 400),
        _info("Inter", FontCategory.SANS_SERIF, 400),
        _info("Inter", FontCategory.SANS_SERIF, 700),
        _info("FiraCode", FontCategory.MONOSPACE, 400),
        _info("Bebas", FontCategory.DISPLAY, 700),
    ]


def test_recommend_returns_pairs(font_pool: list[FontInfo]) -> None:
    pairs = recommend(font_pool)
    assert len(pairs) >= 1
    assert pairs[0].heading.family != ""
    assert pairs[0].body.family != ""


def test_recommend_respects_count(font_pool: list[FontInfo]) -> None:
    opts = RecommendOptions(count=2)
    pairs = recommend(font_pool, opts)
    assert len(pairs) <= 2


def test_recommend_modern_style(font_pool: list[FontInfo]) -> None:
    opts = RecommendOptions(style="modern")
    pairs = recommend(font_pool, opts)
    assert len(pairs) >= 1


def test_recommend_filter_families(font_pool: list[FontInfo]) -> None:
    opts = RecommendOptions(filter_families=["Inter", "Playfair"])
    pairs = recommend(font_pool, opts)
    for p in pairs:
        assert p.heading.family in ("Inter", "Playfair")
        assert p.body.family in ("Inter", "Playfair")


def test_recommend_sorted_by_score(font_pool: list[FontInfo]) -> None:
    pairs = recommend(font_pool)
    scores = [p.score.total for p in pairs if p.score]
    assert scores == sorted(scores, reverse=True)


def test_recommend_no_mono(font_pool: list[FontInfo]) -> None:
    opts = RecommendOptions(include_mono=False)
    pairs = recommend(font_pool, opts)
    for p in pairs:
        assert p.mono is None


def test_recommend_empty_pool() -> None:
    pairs = recommend([])
    assert len(pairs) == 0


def test_recommend_with_mono(font_pool: list[FontInfo]) -> None:
    opts = RecommendOptions(include_mono=True)
    pairs = recommend(font_pool, opts)
    mono_pairs = [p for p in pairs if p.mono is not None]
    assert len(mono_pairs) >= 1
