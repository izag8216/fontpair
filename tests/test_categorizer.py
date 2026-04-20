"""Tests for fontpair categorizer."""

from __future__ import annotations

from pathlib import Path

import pytest

from fontpair.categorizer import categorize, categorize_fonts
from fontpair.models import FontCategory, FontInfo

FIXTURES = Path(__file__).parent / "fixtures" / "test_fonts"

MONO_FONT = FIXTURES / "RobotoMono.ttf"
SLAB_FONT = FIXTURES / "GeorgiaBold.ttf"
SANS_FONT = FIXTURES / "Raleway.ttf"


def _make_info(path: Path, family: str = "", style: str = "Regular") -> FontInfo:
    return FontInfo(
        family=family or path.stem,
        style=style,
        weight=400,
        width=5,
        file_path=path,
    )


def test_categorize_monospace() -> None:
    info = _make_info(MONO_FONT, "Roboto Mono")
    cat = categorize(info)
    assert cat == FontCategory.MONOSPACE


def test_categorize_sans_serif() -> None:
    info = _make_info(SANS_FONT, "Raleway")
    cat = categorize(info)
    assert cat == FontCategory.SANS_SERIF


def test_categorize_serif() -> None:
    info = _make_info(SLAB_FONT, "Georgia")
    cat = categorize(info)
    assert cat == FontCategory.SERIF


def test_categorize_fonts_batch() -> None:
    fonts = [
        _make_info(MONO_FONT, "Roboto Mono"),
        _make_info(SANS_FONT, "Raleway"),
        _make_info(SLAB_FONT, "Georgia"),
    ]
    categorized = categorize_fonts(fonts)
    assert len(categorized) == 3
    categories = {f.category for f in categorized}
    assert FontCategory.MONOSPACE in categories


def test_categorize_nonexistent_file() -> None:
    info = FontInfo(
        family="Missing",
        style="Regular",
        weight=400,
        width=5,
        file_path=Path("/nonexistent/font.ttf"),
    )
    cat = categorize(info)
    assert cat == FontCategory.SANS_SERIF  # fallback
