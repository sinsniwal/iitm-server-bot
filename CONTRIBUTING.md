# Contributing to the bot

First off, thanks for taking the time to contribute. It makes the bot substantially better.

The following is a set of guidelines for contributing to the repository. These are guidelines, not hard rules.

# This is too much to read! I want to ask a question!

Generally speaking, questions are better suited in our Discord server.

Please try your best not to ask questions in the issue tracker. Most of them don't belong there unless they provide
value to a larger audience.

# Getting started

The core of this project is the `discord.py` library, which deals in concepts that are not exactly beginner
friendly. There is a list of useful prerequisite knowledge [here](https://gist.github.com/scragly/095b5278a354d46e86f02d643fc3d64b)
although it is a bit out of date in some respects.

This library also incorporates (and recommends) strong type hinting. This is because type hints, unlike in core
Python, carry functional meaning in discord.py, and thus it can be a good starting point to get introduced to the
concept.

The static type checker we use to validate this repository is Pyright, which you can install from `npm`, or if you use
Visual Studio Code, the Pylance extension uses it under the hood.

We do not enforce `strict` rules, but we do enforce some additional constraints on top of `basic`.

Python docs on typing: https://docs.python.org/3/library/typing.html

# Setting up

We recommend installing `pyright`, `black`, and `isort` to format and check your code. These tools will also be run
against any pull requests you submit. It is recommended to use a
[virtual environment](https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-and-using-virtual-environments)
to develop in.

