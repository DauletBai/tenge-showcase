<p align="center">
  <img src="docs/brand/logo_64.svg" alt="Tenge Logo" width="64"/>
</p>

# Tenge Showcase

🚀 **Tenge Showcase** — visualization and public benchmark results of the experimental programming language **[Tenge](https://github.com/DauletBai/tenge)**.

This repository contains:
- Automated benchmark runner (`scripts/run_bench.sh`)
- Plotting and HTML index generator (`scripts/plot.py`, `scripts/make_index.py`)
- Benchmark results in CSV (`benchmarks/`)
- Plots in PNG/SVG (`plots/`)
- Ready-to-publish GitHub Pages site (`docs/`)

## Usage

### Prerequisites
- Python 3.10+
- Go 1.24+
- Rust (latest stable)
- GNU Make

Install Python deps:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt