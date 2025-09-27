#!/usr/bin/env python3
import argparse
import glob
import os
import re
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ---- Helpers ------------------------------------------------

def find_csvs(results_dir: str):
    # search recursively to be safe
    files = glob.glob(os.path.join(results_dir, "*.csv")) + \
            glob.glob(os.path.join(results_dir, "**", "*.csv"), recursive=True)
    # dedup while preserving order
    seen = set()
    out = []
    for f in files:
        p = os.path.abspath(f)
        if p not in seen and os.path.isfile(p):
            seen.add(p)
            out.append(p)
    return out

TASK_RX = re.compile(r"TASK=([A-Za-z0-9_()\-]+)")
TIME_RX = re.compile(r"TIME_NS=(\d+)")
CSV_RX  = re.compile(r"__CSV__:(.*?):(\d+)")

def load_one(csv_path: str) -> pd.DataFrame:
    """
    Try a few strategies:
    1) Proper CSV with columns like task, impl, avg_ns or time_ns
    2) Lines containing TASK=... TIME_NS=...
    3) Lines like __CSV__:<impl>:<ns>
    """
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        # Maybe it's not a real CSV -> read as raw text
        with open(csv_path, "r", encoding="utf-8", errors="ignore") as fh:
            lines = [ln.strip() for ln in fh if ln.strip()]
        return parse_raw_lines(lines, csv_path)

    cols = {c.lower(): c for c in df.columns}
    # Case 1: tabular
    if "task" in cols and ("avg_ns" in cols or "time_ns" in cols):
        task_col = cols["task"]
        time_col = cols.get("avg_ns", cols.get("time_ns"))
        impl_col = cols.get("impl", None)
        out = pd.DataFrame({
            "task": df[task_col].astype(str).str.strip().str.lower(),
            "time_ns": pd.to_numeric(df[time_col], errors="coerce")
        })
        if impl_col:
            out["impl"] = df[impl_col].astype(str).str.strip()
        else:
            out["impl"] = out["task"]
        out["source"] = Path(csv_path).name
        out = out.dropna(subset=["time_ns"])
        return out.reset_index(drop=True)

    # Fallback to raw parsing if columns unknown
    # Flatten into strings and parse
    lines = []
    for _, row in df.iterrows():
        s = ",".join([str(x) for x in row.values])
        lines.append(s)
    return parse_raw_lines(lines, csv_path)

def parse_raw_lines(lines, csv_path):
    rows = []
    last_task = None
    for ln in lines:
        # __CSV__:impl:ns
        m3 = CSV_RX.search(ln)
        if m3:
            impl = m3.group(1).strip()
            ns = int(m3.group(2))
            rows.append({"task": last_task or impl, "impl": impl, "time_ns": ns})
            continue

        m1 = TASK_RX.search(ln)
        if m1:
            last_task = m1.group(1).strip().lower()

        m2 = TIME_RX.search(ln)
        if m2:
            ns = int(m2.group(1))
            impl = detect_impl_from_line(ln, last_task)
            rows.append({"task": last_task or impl, "impl": impl, "time_ns": ns})

    df = pd.DataFrame(rows)
    if not df.empty:
        df["source"] = Path(csv_path).name
    return df

def detect_impl_from_line(ln: str, task: str | None) -> str:
    # Try to guess impl label from line content
    # Examples in logs: "tenge(radix)", "rust", "c(-)", "go(sym)" etc.
    impl_match = re.search(r"\b(tenge\([^)]+\)|tenge|rust|go|c(?:\([^)]+\)|\(sym\)|\(-\))?)\b", ln, re.IGNORECASE)
    if impl_match:
        return impl_match.group(1)
    if task:
        return task
    return "unknown"

def normalize_task(t: str) -> str:
    t = (t or "").lower()
    # collapse detailed names to groups
    if t.startswith("sort") or "sort" in t:
        return "sort"
    if t.startswith("fib_iter") or "fib_iter" in t:
        return "fib_iter"
    if t.startswith("fib_rec") or "fib_rec" in t:
        return "fib_rec"
    if t.startswith("var_mc") or "var_mc" in t:
        return "var_mc"
    if t.startswith("nbody_sym") or "nbody_sym" in t or "(sym" in t:
        return "nbody_sym"
    if t.startswith("nbody") or "nbody" in t:
        return "nbody"
    return t or "misc"

# ---- Plotting ------------------------------------------------

PALETTE_ORDER = ["tenge(radix)", "tenge(pdq)", "tenge(msort)", "tenge(qsort)",
                 "tenge", "c", "rust", "go", "c(-)", "rust(-)", "go(-)", "tenge(sym)", "c(sym)", "rust(sym)", "go(sym)"]

def plot_group(df: pd.DataFrame, out_dir: str, title: str):
    if df.empty:
        return
    # prefer the common impl labels
    df = df.copy()
    # Use best (fastest) time per impl within the group to keep bars clean
    best = df.groupby("impl", as_index=False)["time_ns"].min()
    # Preserve a consistent order
    best["order"] = best["impl"].apply(lambda x: PALETTE_ORDER.index(x) if x in PALETTE_ORDER else 999)
    best = best.sort_values(["order", "time_ns"])

    plt.figure(figsize=(10, 5))
    plt.bar(best["impl"], best["time_ns"])
    plt.xticks(rotation=30, ha="right")
    plt.ylabel("time (ns) lower is better")
    plt.title(title)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    png_path = os.path.join(out_dir, f"{title.replace(' ', '_')}.png")
    svg_path = os.path.join(out_dir, f"{title.replace(' ', '_')}.svg")
    plt.tight_layout()
    plt.savefig(png_path, dpi=180)
    plt.savefig(svg_path)
    plt.close()
    print(f"[plot] wrote {png_path} and {svg_path}")

# ---- Main ----------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True, help="directory with CSV files")
    ap.add_argument("--out", required=True, help="output directory for plots")
    args = ap.parse_args()

    csvs = find_csvs(args.results)
    if not csvs:
        print(f"[plot] no CSV files found in {args.results}")
        return

    frames = []
    for f in csvs:
        try:
            df = load_one(f)
            if df is not None and not df.empty:
                frames.append(df)
        except Exception as e:
            print(f"[warn] failed to parse {f}: {e}")

    if not frames:
        print("[plot] no usable data after normalization")
        return

    data = pd.concat(frames, ignore_index=True)
    # cleanup
    data["task"] = data["task"].astype(str).str.strip().str.lower()
    data["impl"] = data.get("impl", pd.Series(["unknown"] * len(data))).astype(str).str.strip()
    data["task_group"] = data["task"].map(normalize_task)

    for grp, df_grp in data.groupby("task_group"):
        plot_group(df_grp, args.out, f"{grp}_benchmark")

if __name__ == "__main__":
    main()