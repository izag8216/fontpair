"""Font categorizer -- classify fonts into typographic categories."""

from __future__ import annotations

from fontTools.ttLib import TTFont

from fontpair.models import FontCategory, FontInfo


def _panose_category(tt: TTFont) -> FontCategory | None:
    """Determine category from OS/2 Panose classification."""
    if "OS/2" not in tt:
        return None
    os2 = tt["OS/2"]
    panose = getattr(os2, "panose", None)
    if panose is None:
        return None

    family_type = getattr(panose, "bFamilyType", 0)

    _PANOSE_MAP = {
        2: FontCategory.SERIF,
        3: FontCategory.SANS_SERIF,
        4: FontCategory.HANDWRITING,
        5: FontCategory.HANDWRITING,
    }

    if family_type in _PANOSE_MAP:
        return _PANOSE_MAP[family_type]

    if family_type == 1:
        proportion = getattr(panose, "bProportion", 0)
        if proportion == 9:  # Monospaced
            return FontCategory.MONOSPACE
        return FontCategory.SANS_SERIF

    return None


def _heuristic_category(tt: TTFont) -> FontCategory:
    """Fallback: classify using post table and glyph analysis."""
    if "post" in tt:
        post = tt["post"]
        is_fixed = getattr(post, "isFixedPitch", 0)
        if is_fixed:
            return FontCategory.MONOSPACE

    cmap = tt.getBestCmap()
    if cmap:
        glyph_set = tt.getGlyphSet()
        widths = set()
        for char_code in range(32, 127):
            if char_code in cmap:
                glyph_name = cmap[char_code]
                if glyph_name in glyph_set:
                    widths.add(glyph_set[glyph_name].width)
        if len(widths) == 1:
            return FontCategory.MONOSPACE

    return FontCategory.SANS_SERIF


def categorize(font: FontInfo) -> FontCategory:
    """Categorize a font based on its file."""
    try:
        tt = TTFont(str(font.file_path))
        cat = _panose_category(tt)
        if cat is None:
            cat = _heuristic_category(tt)
        tt.close()
        return cat
    except Exception:
        return FontCategory.SANS_SERIF


def categorize_fonts(fonts: list[FontInfo]) -> list[FontInfo]:
    """Categorize a list of fonts, returning new FontInfo objects with categories."""
    return [
        FontInfo(
            family=f.family,
            style=f.style,
            weight=f.weight,
            width=f.width,
            file_path=f.file_path,
            category=categorize(f),
            metrics=f.metrics,
        )
        for f in fonts
    ]
