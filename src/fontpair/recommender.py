"""Pairing recommender -- generate font pairings based on typographic principles."""

from __future__ import annotations

from fontpair.models import (
    FontCategory,
    FontInfo,
    FontPair,
    RecommendOptions,
)
from fontpair.scorer import score_pairing

_STYLE_BODY_PREFERENCE: dict[str, list[FontCategory]] = {
    "modern": [FontCategory.SANS_SERIF, FontCategory.SANS_SERIF],
    "classic": [FontCategory.SERIF, FontCategory.SANS_SERIF],
    "playful": [FontCategory.DISPLAY, FontCategory.SANS_SERIF],
    "editorial": [FontCategory.SERIF, FontCategory.SERIF],
    "technical": [FontCategory.SANS_SERIF, FontCategory.MONOSPACE],
    "minimal": [FontCategory.SANS_SERIF, FontCategory.SANS_SERIF],
}

_STYLE_DESCRIPTIONS: dict[str, str] = {
    "modern": "Clean and contemporary -- bold sans-serif headings with a legible sans-serif body",
    "classic": "Timeless elegance -- serif headings paired with a clean sans-serif body",
    "playful": "Expressive and fun -- display/decorative headings with friendly body text",
    "editorial": "Sophisticated and literary -- serif headings with a refined serif body",
    "technical": "Precise and functional -- sans-serif headings with monospace-influenced body",
    "minimal": "Stripped back and refined -- understated sans-serif throughout",
}


def recommend(
    fonts: list[FontInfo],
    options: RecommendOptions | None = None,
) -> list[FontPair]:
    """Generate scored font pairings from a pool of fonts."""
    opts = options or RecommendOptions()

    heading_prefs, body_prefs = _STYLE_BODY_PREFERENCE.get(
        opts.style, (FontCategory.SANS_SERIF, FontCategory.SANS_SERIF)
    )

    if opts.filter_families:
        fonts = [f for f in fonts if f.family.lower() in [ff.lower() for ff in opts.filter_families]]

    heading_candidates = [f for f in fonts if f.category in ([heading_prefs] if isinstance(heading_prefs, FontCategory) else heading_prefs)]
    body_candidates = [f for f in fonts if f.category in ([body_prefs] if isinstance(body_prefs, FontCategory) else body_prefs)]

    if not heading_candidates:
        heading_candidates = [f for f in fonts if f.weight >= 600]
    if not body_candidates:
        body_candidates = [f for f in fonts if f.weight <= 500]

    if not heading_candidates or not body_candidates:
        return []

    mono_candidates = [f for f in fonts if f.category == FontCategory.MONOSPACE] if opts.include_mono else []

    pairs: list[FontPair] = []
    seen: set[tuple[str, str]] = set()

    for heading in heading_candidates:
        for body in body_candidates:
            key = (heading.family, body.family)
            if key in seen:
                continue
            if heading.file_path == body.file_path and heading.style == body.style:
                continue
            seen.add(key)

            score = score_pairing(heading, body)
            mono = None
            if mono_candidates:
                mono = mono_candidates[0]

            pairs.append(
                FontPair(
                    heading=heading,
                    body=body,
                    mono=mono,
                    score=score,
                    style_description=_STYLE_DESCRIPTIONS.get(opts.style, ""),
                )
            )

    pairs.sort(key=lambda p: p.score.total if p.score else 0, reverse=True)
    return pairs[: opts.count]
