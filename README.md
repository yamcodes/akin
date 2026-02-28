# akin

A monorepo for an Akinator CLI experience.

## Structure

| Directory | Description                                        |
|-----------|----------------------------------------------------|
| `poc/`    | Original single-file PoC — 109 lines, plain Python |
| `engine/` | Python wrapper around the akinator library         |
| `tui/`    | Frontend (Textual)                                 |
| `server/` | Spring Boot server, hypermedia, session state      |

## Acknlowedgements

- Thanks [fiorix](https://gist.github.com/fiorix) for original gist: https://gist.github.com/fiorix/3152830
- Thanks [Omkaar](https://github.com/Ombucha) for the [`akinator`](https://github.com/Ombucha/akinator.py) library, which powers the game session and Cloudflare bypass
- Thanks the [`readchar`](https://github.com/magmax/python-readchar) authors for single-keypress input
