#!/usr/bin/env python
# coding: utf-8
#
# Interactive command line crawler to akinator.com
# http://musta.sh/2012-07-20/twisting-python-and-freeswitch.html

import re
import sys
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from twisted.internet import defer, reactor
from twisted.web import client


class AkinatorChat:
    def __init__(self, name, age, gender, language="en"):
        self.answer = 0
        self.count = 0
        self.partie = 0
        self.signature = 0

        self.language = language
        self.server = "http://%s.akinator.com" % language

        # http session data
        self.done = False
        self.session = False
        self.name = name
        self.age = age
        self.gender = gender

    def __iter__(self):
        return self

    def parse_html(self, html, init_session=False):
        try:
            soup = BeautifulSoup(html, "html.parser")
            div = soup.find("div", {"class": "question"})

            if init_session:
                script = div.find("script")
                self.partie, self.signature = re.search(
                    r"(\d+),(\d+)", script.text
                ).groups()
                script.extract()

            # no question number means it found the character,
            # or that the Akinator is lost. :)
            try:
                n_question = div.find("span", {"class": "n_question"})
                n_question.extract()
            except:
                try:
                    script = div.find("script")
                    # result[0] = url
                    # result[1] = something
                    # result[2] = name / original name
                    # result[3] = occupation (singer, etc)
                    result = re.findall('("[^"]+)', script.text)
                    character = result[2].strip('"').split("/")[0]
                except:
                    return (0, div.text)
                else:
                    self.done = True
                    script.extract()
                    return (1, "%s %s" % (div.text, character))
            else:
                return (2, div.text)
        except:
            pass

    def put_answer(self, answer):
        # akinator takes 0=yes, 1=no, 2=don't know, 3=probably, 4=not really
        text = ("y", "n", "?", "+", "-")
        if answer in text:
            self.answer = dict([(y, x) for (x, y) in enumerate(text)])[answer]
        elif answer in ("0", "1", "2", "3", "4"):
            self.answer = answer
        else:
            self.answer = 0
            self.done = True

    def __next__(self):
        if self.done:
            raise StopIteration

        if self.session:
            url = "%s/repondre_propose.php?%s" % (
                self.server,
                urlencode(
                    {
                        "engine": 0,
                        "fq": "",
                        "nqp": self.count,
                        "partie": self.partie,
                        "prio": 0,
                        "reponse": self.answer,
                        "signature": self.signature,
                        "step_prop": -1,
                        "trouvitude": 0,
                    }
                ),
            )

            self.count += 1
            return client.getPage(url).addCallback(self.parse_html)
        else:
            # new session
            url = "%s/new_session.php?%s" % (
                self.server,
                urlencode(
                    {
                        "age": self.age,
                        "email": "",
                        "engine": 0,
                        "joueur": self.name,
                        "ms": 0,
                        "partner_id": 0,
                        "prio": 0,
                        "remember": 0,
                        "sexe": self.gender,
                    }
                ),
            )

            self.session = True
            return client.getPage(url).addCallback(lambda s: self.parse_html(s, True))


@defer.inlineCallbacks
def interactive(*args):
    print("Think about a real or fictional character. I will try to guess who it is.\n")
    print("Answer: [y]es, [n]o, [?] don't know, [+] probably, [-] not really\n")

    akinator = AkinatorChat(*args)

    for cmd in akinator:
        r, text = yield cmd

        if r == 2:  # Question
            answer = input("%s " % text)
            akinator.put_answer(answer)
        else:  # Answer or Error
            print(text)
            break


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

Examples:
  akinator Alice 25 F
  akinator Alice 25 F es\
"""

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(HELP)
        sys.exit(0)

    try:
        name = sys.argv[1]
        age = int(sys.argv[2])
        gender = sys.argv[3].upper()
        try:
            lang = sys.argv[4]
        except:
            lang = "en"

        assert age > 8, "you must be elder than 8 to play"
        assert gender in ("M", "F"), "you must be either (M)ale or (F)emale"
    except AssertionError as e:
        print("oops! ", e)
        sys.exit(0)
    except Exception as e:
        print(USAGE)
        sys.exit(0)

    interactive(name, age, gender, lang).addCallback(lambda *v: reactor.stop())
    reactor.run()
