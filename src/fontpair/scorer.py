"""Pairing scorer -- rate font pairings on typographic principles."""

from __future__ import annotations

from fontpair.models import FontCategory, FontInfo, FontPair, ScoreBreakdown


def _visual_harmony(heading: FontInfo, body: FontInfo) -> float:
    """Score visual harmony (0-100). Higher when categories complement."""
    cat_pair = (heading.category, body.category)

    complementary = {
        (FontCategory.SERIF, FontCategory.SANS_SERIF): 90,
        (FontCategory.SANS_SERIF, FontCategory.SERIF): 90,
        (FontCategory.DISPLAY, FontCategory.SANS_SERIF): 85,
        (FontCategory.DISPLAY, FontCategory.SERIF): 85,
        (FontCategory.SANS_SERIF, FontCategory.SANS_SERIF): 70,
        (FontCategory.SERIF, FontCategory.SERIF): 65,
        (FontCategory.HANDWRITING, FontCategory.SANS_SERIF): 60,
    }

    score = complementary.get(cat_pair, 50)

    if heading.family == body.family:
        score -= 15

    return max(0, min(100, score))


def _readability(heading: FontInfo, body: FontInfo) -> float:
    """Score readability (0-100). Higher when body has good x-height and heading is bolder."""
    score = 70.0

    if body.metrics:
        xh = body.metrics.x_height_ratio
        if 0.45 <= xh <= 0.55:
            score += 15
        elif 0.40 <= xh <= 0.60:
            score += 8

    if heading.weight > body.weight:
        score += 10

    if body.category == FontCategory.SANS_SERIF:
        score += 5

    if body.category == FontCategory.MONOSPACE:
        score -= 10

    return max(0, min(100, score))


def _contrast_balance(heading: FontInfo, body: FontInfo) -> float:
    """Score contrast balance (0-100). Higher with good weight differentiation."""
    weight_diff = abs(heading.weight - body.weight)

    if weight_diff >= 200:
        score = 90
    elif weight_diff >= 100:
        score = 75
    elif weight_diff >= 50:
        score = 55
    else:
        score = 30

    if heading.category != body.category:
        score += 5

    return max(0, min(100, score))


def _x_height_compat(heading: FontInfo, body: FontInfo) -> float:
    """Score x-height compatibility (0-100). Higher when heading x-height <= body x-height."""
    if not heading.metrics or not body.metrics:
        return 60.0

    ratio = heading.metrics.x_height_ratio / body.metrics.x_height_ratio

    if 0.85 <= ratio <= 1.05:
        return 90.0
    if 0.75 <= ratio <= 1.15:
        return 70.0
    if 0.65 <= ratio <= 1.25:
        return 50.0
    return 30.0


def score_pairing(heading: FontInfo, body: FontInfo) -> ScoreBreakdown:
    """Score a heading+body pairing."""
    vh = _visual_harmony(heading, body)
    rd = _readability(heading, body)
    cb = _contrast_balance(heading, body)
    xh = _x_height_compat(heading, body)

    total = vh * 0.30 + rd * 0.25 + cb * 0.25 + xh * 0.20

    return ScoreBreakdown(
        visual_harmony=vh,
        readability=rd,
        contrast_balance=cb,
        x_height_compat=xh,
        total=total,
    )
