#!/usr/bin/env python
import argparse
import os

from app import AkinatorApp


def main() -> None:
    parser = argparse.ArgumentParser(description="Akinator TUI")
    parser.add_argument("language", nargs="?", default="en")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument(
        "--engine-url",
        default=os.environ.get("ENGINE_URL", "http://localhost:8000"),
    )
    args = parser.parse_args()
    AkinatorApp(language=args.language, debug=args.debug, engine_url=args.engine_url).run()


if __name__ == "__main__":
    main()
