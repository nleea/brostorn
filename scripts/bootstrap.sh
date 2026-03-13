#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

cp -n .env.example .env || true
python -m pip install -e .[dev]
alembic upgrade head

echo "Bootstrap completed."
echo "1) Edit .env if needed"
echo "2) Add markdown notes into knowledge/obsidian-vault"
echo "3) Run: make run-api"
