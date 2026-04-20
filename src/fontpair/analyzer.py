"""Font metric analyzer -- compute x-height, weight, contrast, width."""

from __future__ import annotations

from pathlib import Path

from fontTools.ttLib import TTFont

from fontpair.models import FontMetrics


def _get_glyph_width(tt: TTFont, glyph_name: str) -> float | None:
    """Get horizontal advance width for a glyph."""
    try:
        glyph_set = tt.getGlyphSet()
        if glyph_name not in glyph_set:
            return None
        return glyph_set[glyph_name].width
    except Exception:
        return None


def _get_x_height(tt: TTFont) -> float | None:
    """Get x-height from OS/2 table or estimate from glyph."""
    if "OS/2" in tt:
        os2 = tt["OS/2"]
        sx_height = getattr(os2, "sxHeight", 0)
        if sx_height > 0:
            return float(sx_height)

    cmap = tt.getBestCmap()
    if not cmap:
        return None

    x_glyph = cmap.get(ord("x"))
    if not x_glyph:
        return None

    glyph_set = tt.getGlyphSet()
    if x_glyph not in glyph_set:
        return None

    try:
        return float(glyph_set[x_glyph].width)
    except Exception:
        return None


def _get_ascender(tt: TTFont) -> float:
    """Get ascender height."""
    if "OS/2" in tt:
        os2 = tt["OS/2"]
        typo_ascender = os2.sTypoAscender
        if typo_ascender > 0:
            return float(typo_ascender)

    if "hhea" in tt:
        hhea = tt["hhea"]
        if hhea.ascent > 0:
            return float(hhea.ascent)

    return 1000.0


def _get_cap_height(tt: TTFont) -> float | None:
    """Get cap height from OS/2 or estimate."""
    if "OS/2" in tt:
        os2 = tt["OS/2"]
        cap_height = getattr(os2, "sCapHeight", 0)
        if cap_height > 0:
            return float(cap_height)
    return None


def compute_metrics(file_path: Path) -> FontMetrics:
    """Compute full metrics for a font file."""
    tt = TTFont(str(file_path))

    x_height = _get_x_height(tt)
    ascender = _get_ascender(tt)
    x_height_ratio = (x_height / ascender) if (x_height and ascender) else 0.5

    weight = 400
    if "OS/2" in tt:
        weight = tt["OS/2"].usWeightClass

    cmap = tt.getBestCmap()
    glyph_set = tt.getGlyphSet()
    widths = []
    for char_code in range(32, 127):
        if cmap and char_code in cmap:
            glyph_name = cmap[char_code]
            if glyph_name in glyph_set:
                w = glyph_set[glyph_name].width
                if w and w > 0:
                    widths.append(float(w))

    avg_width = sum(widths) / len(widths) if widths else 500.0

    if len(widths) >= 2:
        mean = sum(widths) / len(widths)
        variance = sum((w - mean) ** 2 for w in widths) / len(widths)
        contrast = (variance ** 0.5) / mean if mean > 0 else 0.0
    else:
        contrast = 0.0

    tt.close()
    return FontMetrics(
        x_height_ratio=x_height_ratio,
        weight=weight,
        avg_width=avg_width,
        contrast=contrast,
    )


def analyze_font_info(font_path: Path) -> dict:
    """Return detailed analysis dict for a font file."""
    tt = TTFont(str(font_path))
    result = {
        "glyph_count": len(tt.getGlyphOrder()),
        "units_per_em": tt["head"].unitsPerEm if "head" in tt else 1000,
        "has_os2": "OS/2" in tt,
        "x_height": _get_x_height(tt),
        "ascender": _get_ascender(tt),
        "cap_height": _get_cap_height(tt),
    }
    tt.close()
    return result
