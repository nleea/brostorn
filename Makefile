.PHONY: bootstrap migrate upgrade run-api run-indexer run-mcp test lint
export PYTHONPATH := $(PWD)/packages:$(PWD)

bootstrap:
	cp -n .env.example .env || true
	pip install -e .[dev]

migrate:
	alembic revision --autogenerate -m "init"

upgrade:
	alembic upgrade head

run-api:
	poetry run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8008 --reload

run-indexer:
	poetry run python -m apps.indexer.main

run-mcp:
	poetry run python -m apps.mcp_server.main

test:
	pytest -q

lint:
	ruff check .
