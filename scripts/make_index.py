#!/usr/bin/env python3
"""
Generate docs/index.html from images in docs/plots/.
All comments in English for documentation purposes only.
"""

import os
from pathlib import Path
from datetime import datetime
from html import escape

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
PLOTS_DIR = DOCS / "plots"   # images are copied here on publish

def collect_series():
    # Return list of (basename, png_path_rel, svg_path_rel)
    out = []
    if not PLOTS_DIR.exists():
        return out
    pngs = {p.stem: p for p in PLOTS_DIR.glob("*.png")}
    svgs = {p.stem: p for p in PLOTS_DIR.glob("*.svg")}
    names = sorted(set(pngs.keys()) | set(svgs.keys()))
    for name in names:
        png_rel = f"plots/{name}.png" if (PLOTS_DIR / f"{name}.png").exists() else ""
        svg_rel = f"plots/{name}.svg" if (PLOTS_DIR / f"{name}.svg").exists() else ""
        out.append((name, png_rel, svg_rel))
    return out

def card_html(name, png_rel, svg_rel):
    title = escape(name.replace("_benchmark", "").replace("_", " "))
    img = escape(png_rel or svg_rel or "")
    link = escape(svg_rel or png_rel or "")
    if not img:
        return ""
    return f"""
      <a class="card" href="{link}" target="_blank" rel="noopener">
        <img src="{img}" alt="{escape(name)}">
        <div class="card-title">{title}</div>
      </a>
    """

def build_index(cards):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    cards_html = "\n".join(cards)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Tenge Showcase — Benchmarks</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    /* Minimal, clean, responsive gallery */
    body {{ margin: 0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; background:#0b1220; color:#e8eefc; }}
    header {{ padding: 24px 16px; border-bottom:1px solid #1b2a4a; background: #0f1830; position: sticky; top: 0; z-index: 10; }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 16px; }}
    h1 {{ margin: 0 0 8px; font-size: 28px; letter-spacing: .3px; }}
    p.lead {{ margin: 0; opacity:.8; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; margin-top: 18px; }}
    .card {{ display: block; background: #0e1730; border:1px solid #23355b; border-radius: 12px; text-decoration: none; color: inherit; overflow: hidden; transition: transform .08s ease, border-color .2s ease; }}
    .card:hover {{ transform: translateY(-2px); border-color:#3c5fa1; }}
    .card img {{ width:100%; height:180px; object-fit: cover; display:block; background:#091126; }}
    .card-title {{ padding: 12px 14px; font-weight: 600; font-size: 14px; }}
    footer {{ text-align:center; opacity:.6; padding: 24px 0 40px; }}
    .links a {{ color:#9ec2ff; }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <h1>Tenge Showcase — Benchmarks</h1>
      <p class="lead">Auto-generated index of plots. Updated: {escape(now)}</p>
      <div class="links" style="margin-top:8px">
        <a href="./crud_demo.html">CRUD demo</a>
        &nbsp;•&nbsp;
        <a href="https://github.com/DauletBai/tenge">Tenge repo</a>
        &nbsp;•&nbsp;
        <a href="https://github.com/DauletBai/tenge-showcase">Showcase repo</a>
      </div>
    </div>
  </header>

  <main class="wrap">
    <div class="grid">
{cards_html}
    </div>
  </main>

  <footer>
    <div class="wrap">© Tenge Project — Benchmarks gallery</div>
  </footer>
</body>
</html>
"""

def main():
    series = collect_series()
    cards = [card_html(n, p, s) for (n, p, s) in series if (p or s)]
    html = build_index(cards)
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    print(f"[make_index] wrote {DOCS/'index.html'} with {len(cards)} cards")

if __name__ == "__main__":
    main()