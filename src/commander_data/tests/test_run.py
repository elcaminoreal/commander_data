"""Tests for the command runner."""

import argparse
import unittest
from typing import Sequence
from hamcrest import (
    assert_that,
    equal_to,
)

from .. import run
from .. import COMMAND


class TestRunner(unittest.TestCase):
    """Tests for :code:`run.Runner`."""

    def test_basic_runner(self) -> None:
        """The default runner runs commands and captures output."""
        res = run.Runner().safe_run(COMMAND.echo("hello"))
        assert_that(res.stdout.strip(), equal_to("hello"))  # noqa: SLD801

    def test_no_dry_runner(self) -> None:
        """A non-dry runner runs the command via run()."""
        res = run.Runner(no_dry_run=True).run(COMMAND.echo("hello"))
        assert_that(res.stdout.strip(), equal_to("hello"))  # noqa: SLD801

    def test_args_runner(self) -> None:
        """A runner built from args runs commands."""
        runner = run.Runner.from_args(argparse.Namespace())  # noqa: SLD801
        res = runner.safe_run(COMMAND.echo("hello"))
        assert_that(res.stdout.strip(), equal_to("hello"))  # noqa: SLD801

    def test_dry_runner(self) -> None:
        """A dry run does not produce any output."""
        res = run.Runner().run(COMMAND.echo("hello"))
        assert_that(res.stdout.strip(), equal_to(""))

    def test_runner_fail(self) -> None:
        """A failing command attaches its output as notes."""
        runner = run.Runner.from_args(argparse.Namespace())  # noqa: SLD801
        with self.assertRaises(Exception) as caught:
            runner.safe_run(COMMAND.false)
        notes: Sequence[str] = getattr(caught.exception, "__notes__")
        starts = {note[:7] for note in notes}
        assert_that(starts, equal_to({"STDOUT:", "STDERR:"}))
