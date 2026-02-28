.PHONY: setup setup-engine setup-tui engine tui docker

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
