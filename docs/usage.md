# API Reference

## scanner

### `scan_fonts(additional_dirs=None) -> ScanResult`

Scans all system font directories.

### `scan_directory(directory) -> ScanResult`

Scans a specific directory for fonts.

## analyzer

### `compute_metrics(file_path) -> FontMetrics`

Computes x-height ratio, weight, average width, and contrast for a font file.

### `analyze_font_info(font_path) -> dict`

Returns detailed analysis including glyph count, UPM, x-height, ascender, cap height.

## categorizer

### `categorize(font) -> FontCategory`

Categorizes a single font.

### `categorize_fonts(fonts) -> list[FontInfo]`

Batch categorization, returns new FontInfo objects with categories set.

## recommender

### `recommend(fonts, options=None) -> list[FontPair]`

Generates scored font pairings. Options:

| Field | Type | Default |
|-------|------|---------|
| style | str | "modern" |
| count | int | 5 |
| filter_families | list[str] | [] |
| include_mono | bool | True |

## scorer

### `score_pairing(heading, body) -> ScoreBreakdown`

Scores a heading+body pair on four dimensions (each 0-100):
- visual_harmony (weight: 0.30)
- readability (weight: 0.25)
- contrast_balance (weight: 0.25)
- x_height_compat (weight: 0.20)

## exporter

### `export(pairing, fmt="css", include_local=False) -> str`

Export a FontPair. Formats: `css`, `json`, `yaml`.

## models

### FontInfo

| Field | Type |
|-------|------|
| family | str |
| style | str |
| weight | int |
| width | int |
| file_path | Path |
| category | FontCategory |
| metrics | FontMetrics or None |

### FontPair

| Field | Type |
|-------|------|
| heading | FontInfo |
| body | FontInfo |
| mono | FontInfo or None |
| score | ScoreBreakdown or None |
| style_description | str |
