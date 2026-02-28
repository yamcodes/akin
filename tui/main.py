#!/usr/bin/env python
import argparse

from tui.app import AkinatorApp


def main() -> None:
    parser = argparse.ArgumentParser(description="Akinator TUI")
    parser.add_argument("language", nargs="?", default="en")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    AkinatorApp(language=args.language, debug=args.debug).run()


if __name__ == "__main__":
    main()
