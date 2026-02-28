#!/usr/bin/env python
# coding: utf-8
#
# Interactive command line crawler to akinator.com

import sys

import readchar
from akinator.client import Akinator
from akinator.exceptions import CantGoBackAnyFurther, InvalidChoiceError, InvalidLanguageError

USAGE = "use: akinator [language (en|es|pt|...)]"

HELP = """\
Akinator CLI — guess a character by answering yes/no questions.

Usage:
  akinator [language]

Arguments:
  language  Two-letter language code (default: en)

Answers during the game:
  y   Yes
  n   No
  ?   Don't know
  +   Probably
  -   Probably not
  b   Go back

Examples:
  akinator
  akinator es\
"""

ANSWER_ALIASES = {
    "?": "idk",
    "+": "probably",
    "-": "probably not",
}


def interactive(language="en"):
    print("Think about a real or fictional character. I will try to guess who it is.\n")
    print("Answer: [y] Yes  [n] No  [?] Don't know  [+] Probably  [-] Probably not  [b] Back\n")

    aki = Akinator()

    try:
        aki.start_game(language=language)
    except InvalidLanguageError:
        print("Invalid language '%s'. Falling back to English." % language)
        aki.start_game(language="en")
    except Exception as e:
        print("Error starting game: %s" % e)
        return

    while not aki.finished:
        if aki.win:
            print("\nI think it's: %s — %s" % (aki.name_proposition, aki.description_proposition))
            print("Am I right? [y]es / [n]o: ", end="", flush=True)
            raw = readchar.readchar()
            if raw == readchar.key.CTRL_C:
                print()
                return
            print(raw)
            if raw in ("y", "yes"):
                aki.choose()
            else:
                aki.exclude()
            continue

        print("%d. %s " % (aki.step + 1, aki.question), end="", flush=True)
        raw = readchar.readchar()
        if raw == readchar.key.CTRL_C:
            print()
            return
        print(raw)

        if raw == "b":
            try:
                aki.back()
            except CantGoBackAnyFurther:
                print("Can't go back any further.")
            continue

        answer_str = ANSWER_ALIASES.get(raw, raw)
        try:
            aki.answer(answer_str)
        except InvalidChoiceError:
            print("Invalid answer. Use: y, n, ?, +, -, b")
        except Exception as e:
            print("Error: %s" % e)
            return

    print("\n%s" % aki.question)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(HELP)
        sys.exit(0)

    argv = [a for a in sys.argv[1:] if a != "--debug"]
    lang = argv[0] if argv else "en"

    interactive(lang)
