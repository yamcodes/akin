#!/usr/bin/env python
# coding: utf-8
#
# Interactive command line crawler to akinator.com

import sys

import akinator

USAGE = "use: akinator <name> <age> <gender> [language (en|es|pt)]"

HELP = """\
Akinator CLI — guess a character by answering yes/no questions.

Usage:
  akinator <name> <age> <gender> [language]

Arguments:
  name      Your name
  age       Your age (must be greater than 8)
  gender    M or F
  language  Two-letter language code (default: en)

Answers during the game:
  y   Yes
  n   No
  ?   Don't know
  +   Probably
  -   Not really
  b   Go back

Examples:
  akinator Alice 25 F
  akinator Alice 25 F es\
"""

ANSWER_MAP = {
    "y": "yes",
    "n": "no",
    "?": "idk",
    "+": "probably",
    "-": "probably not",
    "b": "back",
}


def interactive(name, age, gender, language="en"):
    print("Think about a real or fictional character. I will try to guess who it is.\n")
    print("Answer: [y]es, [n]o, [?] don't know, [+] probably, [-] not really, [b]ack\n")

    aki = akinator.Akinator()

    try:
        aki.start_game(language=language)
    except Exception as e:
        print("Error starting game: %s" % e)
        return

    while not aki.finished:
        answer = input("%s " % aki)
        mapped = ANSWER_MAP.get(answer, answer)
        try:
            aki.answer(mapped)
        except akinator.CantGoBackAnyFurther:
            print("Can't go back any further.")
        except Exception as e:
            print("Error: %s" % e)
            return

    print("\nI think it's: %s" % aki.first_guess["name"])
    print(aki.first_guess.get("description", ""))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(HELP)
        sys.exit(0)

    argv = [a for a in sys.argv[1:] if a != "--debug"]

    try:
        name = argv[0]
        age = int(argv[1])
        gender = argv[2].upper()
        try:
            lang = argv[3]
        except IndexError:
            lang = "en"

        assert age > 8, "you must be elder than 8 to play"
        assert gender in ("M", "F"), "you must be either (M)ale or (F)emale"
    except AssertionError as e:
        print("oops!", e)
        sys.exit(0)
    except Exception:
        print(USAGE)
        sys.exit(0)

    interactive(name, age, gender, lang)
