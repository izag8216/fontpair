"""Basic example: scan fonts and get a modern pairing recommendation."""

from pathlib import Path

from fontpair.categorizer import categorize_fonts
from fontpair.exporter import export
from fontpair.models import RecommendOptions
from fontpair.recommender import recommend
from fontpair.scanner import scan_directory, scan_fonts

# Scan all system fonts
result = scan_fonts()
fonts = categorize_fonts(result.fonts)
print(f"Found {len(fonts)} fonts")

# Get top 3 modern pairings
opts = RecommendOptions(style="modern", count=3)
pairs = recommend(fonts, opts)

for i, pair in enumerate(pairs, 1):
    score = pair.score.total if pair.score else 0
    print(f"#{i}: {pair.heading.family} + {pair.body.family} (score: {score:.1f})")

# Export the best pairing as CSS
if pairs:
    css = export(pairs[0], fmt="css")
    print("\n--- CSS Output ---")
    print(css)
