#!/usr/bin/env bash
set -euo pipefail

if ! command -v codex >/dev/null 2>&1; then
  echo "Error: codex CLI not found in PATH"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MEMORY_ROOT="${1:-${MEMORY_ROOT_PATH:-$ROOT_DIR}}"
ACTIVE_PROJECT="${2:-${MEMORY_ACTIVE_PROJECT:-}}"

DB_URL="${DATABASE_URL:-postgresql+asyncpg://memory:memory@localhost:5434/memory_db}"
SYNC_DB_URL="${SYNC_DATABASE_URL:-postgresql+psycopg://memory:memory@localhost:5434/memory_db}"
MCP_NAME="${MCP_SERVER_NAME:-memory-system}"

resolve_python_bin() {
  if ! command -v poetry >/dev/null 2>&1; then
    return 1
  fi

  local python_bin
  python_bin="$(cd "$ROOT_DIR" && poetry env info --executable 2>/dev/null || true)"
  if [[ -n "$python_bin" && -x "$python_bin" ]]; then
    printf '%s\n' "$python_bin"
    return 0
  fi

  python_bin="$(cd "$ROOT_DIR" && poetry run python -c 'import sys; print(sys.executable)' 2>/dev/null | tail -n 1 || true)"
  if [[ -n "$python_bin" && -x "$python_bin" ]]; then
    printf '%s\n' "$python_bin"
    return 0
  fi

  return 1
}

PYTHON_BIN="$(resolve_python_bin || true)"
if [[ -z "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python"
fi

echo "Registering Codex MCP server '$MCP_NAME'"
echo "Memory root: $MEMORY_ROOT"
if [[ -n "$ACTIVE_PROJECT" ]]; then
  echo "Active project: $ACTIVE_PROJECT"
fi
echo "Python: $PYTHON_BIN"

# Idempotent refresh
codex mcp remove "$MCP_NAME" >/dev/null 2>&1 || true

codex mcp add "$MCP_NAME" \
  --env DATABASE_URL="$DB_URL" \
  --env SYNC_DATABASE_URL="$SYNC_DB_URL" \
  --env MEMORY_ROOT_PATH="$MEMORY_ROOT" \
  --env MEMORY_ACTIVE_PROJECT="$ACTIVE_PROJECT" \
  --env MCP_SERVER_NAME=memory-mcp \
  -- /bin/zsh -lc "cd '$ROOT_DIR' && '$PYTHON_BIN' -m apps.mcp_server.main"

echo "Done. Verify with: codex mcp list"
echo "Run indexer with: cd '$ROOT_DIR' && poetry run python -m apps.indexer.main"
