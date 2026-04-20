[![header](https://capsule-render.vercel.app/api?type=venom&color=0:1a1a2e,100:533483&height=220&section=header&text=fontpair&fontSize=60&fontAlignY=42&desc=Local%20Font%20Pairing%20Recommender&descSize=18&descAlignY=62&fontColor=ffffff&descColor=e94560)](https://github.com/izag8216/fontpair)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/izag8216/fontpair/actions)

**fontpair** is a CLI tool that scans your locally installed fonts, categorizes them by typographic classification, and recommends visually harmonious pairings -- no internet required.

English | [日本語](README.ja.md)

---

## Features

- **Local font scanning** -- discovers OTF/TTF/TTC fonts across macOS, Linux, Windows
- **Auto-categorization** -- classifies fonts as serif, sans-serif, monospace, display, or handwriting
- **Metric analysis** -- computes x-height ratio, weight, contrast, and average glyph width
- **Smart pairing** -- recommends heading + body + code font combinations using typographic principles
- **6 style presets** -- modern, classic, playful, editorial, technical, minimal
- **Scored results** -- each pairing rated on visual harmony, readability, contrast balance, and x-height compatibility
- **Multi-format export** -- CSS custom properties, JSON, or YAML output

## Installation

```bash
# From PyPI (when published)
pip install fontpair

# From source
git clone https://github.com/izag8216/fontpair.git
cd fontpair
pip install -e .
```

## Quick Start

```bash
# Step 1: Scan your locally installed fonts
fontpair scan

# Step 2: Get pairing recommendations
fontpair recommend --style modern

# Step 3: Export your favorite pairing as CSS
fontpair export --pairing 1 --format css --output fonts.css
```

## Usage

### Scan Fonts

```bash
fontpair scan                    # Scan all system fonts
fontpair scan --refresh          # Force re-scan (ignore cache)
fontpair scan --dir ./my-fonts   # Scan a specific directory
```

### Get Pairing Recommendations

```bash
fontpair recommend                          # Default: modern style, top 5
fontpair recommend --style classic           # Classic serif+sans pairing
fontpair recommend --style technical -n 3    # Technical style, top 3
fontpair recommend --filter Inter "Roboto"   # Only use specific families
fontpair recommend --no-mono                 # Skip monospace recommendation
```

**Available styles:** `modern`, `classic`, `playful`, `editorial`, `technical`, `minimal`

### Font Info

```bash
fontpair info "Inter"    # Show detailed info (fuzzy match)
```

### Export

```bash
fontpair export --pairing 1 --format css      # CSS to stdout
fontpair export --pairing 1 --format json -o pairing.json
fontpair export --pairing 2 --format yaml -o pairing.yaml
fontpair export --pairing 1 --local           # Include @font-face declarations
```

## How Pairing Works

fontpair evaluates four dimensions for each potential pairing:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Visual Harmony | 30% | Category complementarity (serif+sans = best) |
| Readability | 25% | Body x-height ratio + weight hierarchy |
| Contrast Balance | 25% | Weight differentiation between heading and body |
| X-height Compatibility | 20% | Similar optical size between paired fonts |

## Requirements

- Python 3.10+
- Works offline -- no internet or API keys needed

## License

MIT License -- see [LICENSE](LICENSE) for details.
