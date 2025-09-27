#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   scripts/run_bench.sh /path/to/tenge [out_dir]
#
# - 1-й аргумент обязателен: путь к корню проекта tenge (где есть benchmarks/run.sh)
# - 2-й аргумент опционален: куда сложить CSV (по умолчанию: ./benchmarks внутри текущего репо)

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: scripts/run_bench.sh /path/to/tenge [out_dir]" >&2
  exit 2
fi

TEN_DIR="$1"
OUT_DIR="${2:-benchmarks}"

if [[ ! -d "$TEN_DIR/benchmarks" || ! -x "$TEN_DIR/benchmarks/run.sh" ]]; then
  echo "[run_bench] not found: $TEN_DIR/benchmarks/run.sh" >&2
  exit 2
fi

# Прокидываем окружение в оригинальный раннер tenge
echo "[bench] running in $TEN_DIR"
(
  cd "$TEN_DIR"
  REPS="${REPS:-5}" \
  WARMUP="${WARMUP:-2}" \
  INNER_REPS="${INNER_REPS:-0}" \
  PROFILE="${PROFILE:-strict}" \
  ./benchmarks/run.sh
)

# Синхронизируем результаты
mkdir -p "$OUT_DIR"
shopt -s nullglob
copied=0
for f in "$TEN_DIR"/benchmarks/results/*.csv; do
  cp -f "$f" "$OUT_DIR"/
  ((copied++)) || true
done

echo "[sync] CSV in $OUT_DIR: $(ls -1 "$OUT_DIR"/*.csv 2>/dev/null | wc -l)"
if [[ $copied -eq 0 ]]; then
  echo "[run_bench] warning: no CSV found in $TEN_DIR/benchmarks/results"
fi