#!/usr/bin/env bash
set -euo pipefail
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8080}"
BASE="http://${HOST}:${PORT}"
echo "[crud-smoke] GET /todos (should be JSON list)"
curl -fsS "${BASE}/todos" | jq .
echo "[crud-smoke] POST /todos (create)"
NEW=$(curl -fsS -X POST "${BASE}/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"Write blog post","priority":2}')
echo "$NEW" | jq .
ID=$(echo "$NEW" | jq -r '.id // .ID // .Id // empty')
if [[ -z "${ID}" || "${ID}" == "null" ]]; then
  echo "[crud-smoke] ERROR: cannot parse ID from response"
  exit 1
fi
echo "[crud-smoke] created ID=${ID}"
echo "[crud-smoke] GET /todos/${ID}"
curl -fsS "${BASE}/todos/${ID}" | jq .
echo "[crud-smoke] PATCH /todos/${ID} (done=true)"
curl -fsS -X PATCH "${BASE}/todos/${ID}" \
  -H "Content-Type: application/json" \
  -d '{"done":true}' | jq .
echo "[crud-smoke] DELETE /todos/${ID}"
curl -fsS -X DELETE "${BASE}/todos/${ID}" | jq .
echo "[crud-smoke] GET /todos (final)"
curl -fsS "${BASE}/todos" | jq .
echo "[crud-smoke] OK"
