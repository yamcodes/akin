.PHONY: help setup setup-engine setup-tui engine tui build docker start fix check

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  setup         Install deps for both engine and tui"
	@echo "  setup-engine  Install engine deps"
	@echo "  setup-tui     Install tui deps"
	@echo "  fix           Fix formatting and linting in both services"
	@echo "  check         Check formatting and linting without modifying files"
	@echo "  engine        Start the engine HTTP server (local)"
	@echo "  tui           Start the TUI (pass ARGS='en --debug' for options)"
	@echo "  build         Build Docker images"
	@echo "  docker        Start services via Docker Compose"
	@echo "  start         Start full stack: engine via Docker + TUI (requires curl)"

setup: setup-engine setup-tui

setup-engine:
	cd engine && uv sync

setup-tui:
	cd tui && uv sync

fix:
	cd engine && uv run ruff format . && uv run ruff check --fix .
	cd tui && uv run ruff format . && uv run ruff check --fix .
	pnpm fix

check:
	cd engine && uv run ruff format --check . && uv run ruff check .
	cd tui && uv run ruff format --check . && uv run ruff check .
	pnpm check

engine:
	cd engine && uv run python server.py

tui:
	cd tui && uv run python main.py $(ARGS)

build:
	docker compose build

docker:
	docker compose up

start:
	docker compose up -d
	@echo "Waiting for engine to be ready..."; \
	for i in $$(seq 1 30); do \
		curl -sf http://localhost:8000/ > /dev/null 2>&1 && break; \
		sleep 1; \
	done; \
	curl -sf http://localhost:8000/ > /dev/null 2>&1 || { echo "Engine did not start in time"; exit 1; }
	cd tui && uv run python main.py $(ARGS)
