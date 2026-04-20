[![header](https://raw.githubusercontent.com/izag8216/fontpair/main/header.svg)](https://github.com/izag8216/fontpair)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/izag8216/fontpair/actions)

**fontpair** は、ローカルにインストールされたフォントをスキャンし、タイポグラフィ分類でカテゴリ化、視覚的に調和するペアリングを推奨するCLIツールです。インターネット不要。

[English](README.md) | 日本語

---

## 特徴

- **ローカルフォントスキャン** -- macOS/Linux/WindowsのOTF/TTF/TTCを自動検出
- **自動カテゴリ分類** -- serif, sans-serif, monospace, display, handwritingに分類
- **メトリクス分析** -- x-height比率、ウェイト、コントラスト、平均グリフ幅を計算
- **スマートペアリング** -- タイポグラフィ原則に基づく heading + body + code フォント推奨
- **6つのスタイルプリセット** -- modern, classic, playful, editorial, technical, minimal
- **スコアリング** -- 視覚的調和・可読性・コントラスト・x-height互換性で評価
- **マルチフォーマット出力** -- CSS / JSON / YAML

## インストール

```bash
pip install fontpair
```

## クイックスタート

```bash
# 1. フォントをスキャン
fontpair scan

# 2. ペアリング推奨を取得
fontpair recommend --style modern

# 3. CSS としてエクスポート
fontpair export --pairing 1 --format css --output fonts.css
```

## 使い方

### スキャン

```bash
fontpair scan                    # システムフォントをスキャン
fontpair scan --refresh          # キャッシュを無視して再スキャン
fontpair scan --dir ./my-fonts   # 特定ディレクトリをスキャン
```

### ペアリング推奨

```bash
fontpair recommend                          # デフォルト: modern, 上位5件
fontpair recommend --style classic           # クラシック serif+sans
fontpair recommend --style technical -n 3    # テクニカル, 上位3件
fontpair recommend --filter Inter "Roboto"   # 特定ファミリに絞る
```

**スタイル一覧:** `modern`, `classic`, `playful`, `editorial`, `technical`, `minimal`

### フォント情報

```bash
fontpair info "Inter"    # 詳細情報表示（曖昧検索対応）
```

### エクスポート

```bash
fontpair export --pairing 1 --format css      # CSS を stdout へ
fontpair export --pairing 1 --format json -o pairing.json
fontpair export --pairing 2 --format yaml -o pairing.yaml
fontpair export --pairing 1 --local           # @font-face 宣言を含む
```

## ペアリングの仕組み

4つの次元で各ペアリングを評価:

| 次元 | 重み | 説明 |
|------|------|------|
| 視覚的調和 | 30% | カテゴリの補完性（serif+sansが最適） |
| 可読性 | 25% | bodyのx-height比率 + ウェイト階層 |
| コントラスト | 25% | heading/body間のウェイト差 |
| x-height互換性 | 20% | ペア間の光学的サイズの類似性 |

## 動作環境

- Python 3.10+
- オフライン動作 -- インターネット・APIキー不要

## ライセンス

MIT License -- [LICENSE](LICENSE) を参照。
