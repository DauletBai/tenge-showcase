#!/usr/bin/env python3
import argparse, os, datetime, html, glob

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="icon" href="plots/tenge_benchmark.svg">
<style>
  :root {{ --bg:#ffffff; --card:#ffffff; --ink:#e9eef5; --muted:#666666; --accent:#3e9ed6; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Ubuntu,Cantarell,"Helvetica Neue",Arial,sans-serif; background:var(--bg); color:var(--ink); }}
  header {{ padding:28px 18px 6px; text-align:center; }}
  header h1 {{ margin:0; font-size:32px; letter-spacing:.5px; color:var(--muted); }}
  header p.sub {{ margin:6px 0 0; color:var(--muted); }}
  header .meta {{ margin-top:8px; font-size:13px; color:var(--muted); }}
  .links a {{ color:var(--accent); text-decoration:none; margin:0 8px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(420px,1fr)); gap:18px; padding:18px; max-width:1440px; margin:0 auto; }}
  figure {{ background:var(--card); border-radius:14px; padding:12px; box-shadow:0 6px 20px rgba(0,0,0,.25); }}
  figure img {{ width:100%; height:auto; border-radius:10px; display:block; }}
  figure figcaption {{ margin-top:10px; font-size:14px; color:var(--muted); display:flex; justify-content:space-between; align-items:center; }}
  .foot {{ text-align:center; color:var(--muted); padding:18px; font-size:12px; }}
  .badge {{ background:#ffffff; padding:2px 8px; border-radius:999px; font-size:12px; color:#008efc; }}
</style>
</head>
<body>
<header>
  <h1>{title}</h1>
  <p class="sub">{subtitle}</p>
  <div class="meta">
    Generated: <span class="badge">{timestamp}</span>
    <span class="links">
      · <a href="{repo}" target="_blank" rel="noopener">tenge repo</a>
      · <a href="{showcase}" target="_blank" rel="noopener">showcase repo</a>
    </span>
  </div>
</header>
<main class="grid">
{cards}
</main>
<div class="foot">Open-source benchmarks. Lower is better (ns). © {year}</div>
</body>
</html>
"""

CARD = """<figure>
  <a href="plots/{fname_svg}" target="_blank" rel="noopener">
    <img src="plots/{fname_png}" alt="{alt}">
  </a>
  <figcaption>
    <span>{label}</span>
    <a href="plots/{fname_svg}" class="badge" target="_blank" rel="noopener">SVG</a>
  </figcaption>
</figure>"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plots", required=True, help="folder with *.png/*.svg")
    ap.add_argument("--out", required=True, help="output HTML")
    ap.add_argument("--title", default="Tenge Benchmarks")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--repo", default="#")
    ap.add_argument("--showcase", default="#")
    args = ap.parse_args()

    plots = os.path.abspath(args.plots)
    pngs = sorted(glob.glob(os.path.join(plots, "*.png")))
    svgs = {os.path.basename(p).replace(".svg",""): os.path.basename(p) 
            for p in glob.glob(os.path.join(plots, "*.svg"))}

    cards = []
    for p in pngs:
        base = os.path.basename(p)
        stem = base[:-4]
        svg = svgs.get(stem, base.replace(".png",".svg"))
        label = stem.replace("_"," ").replace("benchmark","").strip()
        cards.append(CARD.format(fname_png=base, fname_svg=svg,
                                 label=html.escape(label),
                                 alt=html.escape(stem)))
    html_out = TEMPLATE.format(
        title=html.escape(args.title),
        subtitle=html.escape(args.subtitle),
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        repo=html.escape(args.repo),
        showcase=html.escape(args.showcase),
        cards="\n".join(cards),
        year=datetime.datetime.now().year
    )

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"[make_index] wrote {args.out} with {len(cards)} cards")

if __name__ == "__main__":
    main()