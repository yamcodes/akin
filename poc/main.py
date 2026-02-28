#!/usr/bin/env python
# coding: utf-8
#
# Interactive command line crawler to akinator.com

import argparse
import sys

import readchar
from akinator.client import Akinator
from akinator.exceptions import (
    CantGoBackAnyFurther,
    InvalidChoiceError,
    InvalidLanguageError,
)

HELP = """\
Akinator CLI - guess a character by answering yes/no questions.

Usage:
  akinator [language] [--debug]

Arguments:
  language  Two-letter language code (default: en)
  --debug   Show progression and confidence after each answer

Answers during the game:
  y   Yes
  n   No
  ?   Don't know
  +   Probably
  -   Probably not
  b   Go back

Examples:
  akinator
  akinator es
  akinator en --debug\
"""

ANSWER_ALIASES = {
    "?": "idk",
    "+": "probably",
    "-": "probably not",
}


def read_key(prompt):
    print(prompt, end="", flush=True)
    key = readchar.readchar()
    if key == readchar.key.CTRL_C:
        print()
        raise KeyboardInterrupt
    print(key)
    return key


def interactive(language="en", debug=False):
    print("Think about a real or fictional character. I will try to guess who it is.\n")
    print("Answer: [y] Yes  [n] No  [?] Don't know  [+] Probably  [-] Probably not  [b] Back\n")

    aki = Akinator()

    try:
        aki.start_game(language=language)
    except InvalidLanguageError:
        print(f"Invalid language '{language}'. Falling back to English.")
        aki.start_game(language="en")
    except Exception as e:
        sys.exit(f"Error starting game: {e}")

    try:
        while not aki.finished:
            if aki.win:
                print(f"\nI think it's: {aki.name_proposition} - {aki.description_proposition}")
                raw = read_key("Am I right? [y]es / [n]o: ")
                if raw == "y":
                    aki.choose()
                else:
                    try:
                        aki.exclude()
                    except Exception:
                        print("\nI give up! Good game.")
                        return
                continue

            raw = read_key(f"{aki.step + 1}. {aki.question} ")

            if raw == "b":
                try:
                    aki.back()
                except CantGoBackAnyFurther:
                    print("Can't go back any further.")
                continue

            answer_str = ANSWER_ALIASES.get(raw, raw)
            try:
                aki.answer(answer_str)
                if debug:
                    print(f"  [debug] step={aki.step}  progression={aki.progression:.1f}%")
            except InvalidChoiceError:
                print("Invalid answer. Use: y, n, ?, +, -, b")
            except Exception as e:
                sys.exit(f"Error: {e}")
    except KeyboardInterrupt:
        return

    print(f"\n{aki.question}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Akinator CLI - guess a character by answering yes/no questions.")
    parser.add_argument("language", nargs="?", default="en", help="Two-letter language code (default: en)")
    parser.add_argument("--debug", action="store_true", help="Show progression and confidence after each answer")
    args = parser.parse_args()

    interactive(args.language, debug=args.debug)
