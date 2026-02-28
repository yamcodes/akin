.PHONY: help setup setup-engine setup-tui engine tui docker

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  setup         Install deps for both engine and tui"
	@echo "  setup-engine  Install engine deps"
	@echo "  setup-tui     Install tui deps"
	@echo "  engine        Start the engine HTTP server"
	@echo "  tui           Start the TUI (pass ARGS='en --debug' for options)"
	@echo "  docker        Start the engine via Docker"

setup: setup-engine setup-tui

setup-engine:
	cd engine && uv sync

setup-tui:
	cd tui && uv sync

engine:
	cd engine && uv run python server.py

tui:
	cd tui && uv run python main.py $(ARGS)

docker:
	docker compose up
