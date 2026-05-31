"""Tests for the package's public API."""

import unittest
from typing import Iterable
from hamcrest import assert_that, equal_to, contains_string

from .. import __version__, COMMAND, run_all


class TestInit(unittest.TestCase):
    """Tests for package-level attributes."""

    def test_version(self) -> None:
        """The package exposes a dotted version string."""
        assert_that(__version__, contains_string("."))


class TestRunAll(unittest.TestCase):
    """Tests for :code:`run_all`."""

    def test_simple_run_all(self) -> None:
        """Each command is passed to the runner in order."""
        keep: list[Iterable[str]] = []

        def collect(command: Iterable[str], /, **kwargs: object) -> None:
            keep.append(command)

        run_all(
            collect,
            ["git", "commit"],
        )
        assert_that(keep, equal_to([["git", "commit"]]))


class TestCommand(unittest.TestCase):
    """Tests for building command lines with :code:`COMMAND`."""

    def test_commands(self) -> None:
        """Building commands produces the expected argument lists."""
        for command, expected in _COMMAND_CASES:
            with self.subTest(expected=expected):
                assert_that(list(command), equal_to(expected))


_COMMAND_CASES: list[tuple[Iterable[str], list[str]]] = [
    (COMMAND, []),
    (COMMAND.git, ["git"]),
    (COMMAND.git.init("."), ["git", "init", "."]),
    (COMMAND.git.commit(all=None), ["git", "commit", "--all"]),
    (
        COMMAND.pip.install(r=["r1.txt", "r2.txt"]),
        "pip install -r r1.txt -r r2.txt".split(),
    ),
    (
        COMMAND.copier(data=dict(a="b", c="d")),
        ["copier", "--data", "a=b", "--data", "c=d"],
    ),
    (
        COMMAND.git.commit(message="checkpoint"),
        ["git", "commit", "--message", "checkpoint"],
    ),
    (COMMAND.python(m=None).venv("my-env"), "python -m venv my-env".split()),
]
