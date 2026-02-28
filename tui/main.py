#!/usr/bin/env python
import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tui.app import AkinatorApp

parser = argparse.ArgumentParser(description="Akinator TUI")
parser.add_argument("language", nargs="?", default="en")
parser.add_argument("--debug", action="store_true")
args = parser.parse_args()

AkinatorApp(language=args.language, debug=args.debug).run()
