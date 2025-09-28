#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
from datetime import datetime
from html import escape

def discover_plots(plots_dir: Path):
    items = []
    for p in sorted(plots_dir.glob("*.png")):
        stem = p.stem
        svg = plots_dir / f"{stem}.svg"
        items.append({
            "title": stem.replace("_", " "),
            "png": p.name,
            "svg": svg.name if svg.exists() else None,
        })
    return items

def write_index(out_path: Path, plots, has_crud_card: bool):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    cards_html = []

    # Plot cards
    for it in plots:
        title = escape(it["title"])
        png = escape(it["png"])
        svg = it["svg"]
        svg_link = f' · <a href="./{escape(svg)}" download>SVG</a>' if svg else ""
        cards_html.append(f"""
        <div class="card">
          <h3>{title}</h3>
          <div class="muted small">Download: <a href="./{png}" download>PNG</a>{svg_link}</div>
          <img src="./{png}" alt="{title}" style="width:100%;height:auto;border-radius:.5rem;margin-top:.5rem"/>
        </div>
        """.strip())

    # CRUD card
    if has_crud_card:
        cards_html.append("""
        <div class="card">
          <h3>CRUD HTTP demo</h3>
          <p class="muted">C + SQLite HTTP API (todos)</p>
          <a class="button" href="./crud_demo.html">Open demo page</a>
        </div>
        """.strip())

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Tenge Showcase — Benchmarks</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root {{ color-scheme: light dark; }}
    body {{ font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji"; margin: 2rem; line-height: 1.5; }}
    header {{ display:flex; gap:1rem; align-items:center; flex-wrap:wrap; }}
    .pill{{display:inline-block;padding:.2rem .6rem;border:1px solid rgba(127,127,127,.35);border-radius:999px;font-size:.85rem;margin-right:.35rem}}
    .muted{{opacity:.7}}
    .small{{font-size:.85rem}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1rem;margin-top:1rem}}
    .card{{border:1px solid rgba(127,127,127,.25);border-radius:.75rem;padding:1rem}}
    a.button{{display:inline-block;padding:.5rem .9rem;border:1px solid rgba(127,127,127,.35);border-radius:.6rem;text-decoration:none}}
  </style>
</head>
<body>
  <header>
    <h1 style="margin:0">Tenge Showcase</h1>
    <span class="pill">benchmarks</span>
    <span class="pill">visuals</span>
    <span class="pill">demo</span>
  </header>

  <p class="muted">Updated: {escape(now)}</p>

  <div class="grid">
    {"".join(cards_html)}
  </div>

  <hr style="margin:2rem 0"/>

  <p class="muted small">
    GitHub: <a href="https://github.com/DauletBai/tenge" target="_blank" rel="noopener">DauletBai/tenge</a> ·
    Showcase: <a href="https://github.com/DauletBai/tenge-showcase" target="_blank" rel="noopener">tenge-showcase</a>
  </p>
</body>
</html>
"""
    out_path.write_text(html, encoding="utf-8")
    print(f"[make_index] wrote {out_path} with {len(plots) + (1 if has_crud_card else 0)} cards")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=False, default="benchmarks")
    ap.add_argument("--out", required=False, default="docs")
    args = ap.parse_args()

    plots_dir = Path("plots")
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    plots = discover_plots(plots_dir)
    has_crud_card = Path(out_dir / "crud_demo.html").exists() or Path("docs/crud_demo.html").exists()
    write_index(out_dir / "index.html", plots, has_crud_card)

if __name__ == "__main__":
    main()