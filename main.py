#!/usr/bin/env python
# coding: utf-8
#
# Interactive command line crawler to akinator.com

import sys

import akinator
from akinator import Answer, Language

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

# Map shorthand inputs to strings accepted by Answer.from_str()
ANSWER_ALIASES = {
    "?": "idk",
    "+": "probably",
    "-": "probably not",
}


def interactive(name, age, gender, language="en"):
    print("Think about a real or fictional character. I will try to guess who it is.\n")
    print("Answer: [y]es, [n]o, [?] don't know, [+] probably, [-] not really, [b]ack\n")

    try:
        lang = Language.from_str(language)
    except akinator.InvalidLanguage:
        print("Invalid language '%s'. Falling back to English." % language)
        lang = Language.English

    aki = akinator.Akinator(language=lang)

    try:
        aki.start_game()
    except Exception as e:
        print("Error starting game: %s" % e)
        return

    while True:
        if aki.progression >= 80:
            guess = aki.win()
            print("\nI think it's: %s" % guess.name)
            print(guess.description)
            break

        raw = input("%s " % aki.question)

        if raw == "b":
            try:
                aki.back()
            except akinator.CantGoBackAnyFurther:
                print("Can't go back any further.")
            continue

        answer_str = ANSWER_ALIASES.get(raw, raw)
        try:
            aki.answer(Answer.from_str(answer_str))
        except akinator.InvalidAnswer:
            print("Invalid answer. Use: y, n, ?, +, -, b")
        except Exception as e:
            print("Error: %s" % e)
            return


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
