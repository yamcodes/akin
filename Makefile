.PHONY: help setup setup-engine setup-tui engine tui build docker start

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  setup         Install deps for both engine and tui"
	@echo "  setup-engine  Install engine deps"
	@echo "  setup-tui     Install tui deps"
	@echo "  engine        Start the engine HTTP server (local)"
	@echo "  tui           Start the TUI (pass ARGS='en --debug' for options)"
	@echo "  build         Build Docker images"
	@echo "  docker        Start services via Docker Compose"
	@echo "  start         Start full stack: engine via Docker + TUI"

setup: setup-engine setup-tui

setup-engine:
	cd engine && uv sync

setup-tui:
	cd tui && uv sync

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
	cd tui && uv run python main.py $(ARGS)
