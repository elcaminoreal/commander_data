"""Run command lines, with support for dry runs."""

import argparse
import logging
import subprocess
from typing import Iterable, Protocol, Self, cast

import attrs

LOGGER = logging.getLogger(__name__)


class CalledProcessLike(Protocol):  # pragma: no cover
    """The parts of :code:`subprocess.CompletedProcess` that are used."""

    @property
    def stdout(self) -> str:
        """Return the captured standard output."""

    @property
    def stderr(self) -> str:
        """Return the captured standard error."""


class RunFunction(Protocol):  # pragma: no cover
    """A callable with the relevant parts of :code:`subprocess.run`."""

    def __call__(
        self, cmdargs: Iterable[str], /, **kwargs: object
    ) -> CalledProcessLike:
        """Run the command and return the completed process.

        Args:
            cmdargs: The command line to run.
            **kwargs: Extra arguments for the underlying runner.

        Returns:
            The completed process.
        """


@attrs.frozen
class _FakeCalledProcess:  # noqa: SLD504
    stdout: str = attrs.field(default="", init=False)
    stderr: str = attrs.field(default="", init=False)


def _really_run(
    orig_run: RunFunction, cmdargs: Iterable[str], **kwargs: object
) -> CalledProcessLike:
    cmd = list(cmdargs)
    LOGGER.info("Running %s", cmd)
    real_kwargs: dict[str, object] = dict(check=True, capture_output=True, text=True)
    real_kwargs.update(kwargs)
    try:
        return orig_run(cmd, **real_kwargs)
    except subprocess.CalledProcessError as exc:
        exc.add_note(f"STDERR: {exc.stderr}")
        exc.add_note(f"STDOUT: {exc.stdout}")
        raise


@attrs.frozen
class Runner:  # noqa: SLD504
    """Run command lines, optionally only logging them as a dry run."""

    _orig_run: RunFunction = attrs.field(default=subprocess.run)
    _no_dry_run: bool = attrs.field(default=False, kw_only=True)

    def run(self, cmdargs: Iterable[str], **kwargs: object) -> CalledProcessLike:
        """Run the command, unless this is a dry run.

        Args:
            cmdargs: The command line to run.
            **kwargs: Extra arguments to pass to the underlying run function.

        Returns:
            The completed process, or a fake one on a dry run.
        """
        if self._no_dry_run:
            return self.safe_run(cmdargs, **kwargs)
        LOGGER.info("Dry run, not running %s", list(cmdargs))
        return _FakeCalledProcess()

    def safe_run(self, cmdargs: Iterable[str], **kwargs: object) -> CalledProcessLike:
        """Run the command regardless of the dry run setting.

        Args:
            cmdargs: The command line to run.
            **kwargs: Extra arguments to pass to the underlying run function.

        Returns:
            The completed process.
        """
        return _really_run(self._orig_run, cmdargs, **kwargs)

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> Self:
        """Build a runner from parsed command-line arguments.

        Args:
            args: The parsed arguments, optionally carrying ``orig_run`` and
                ``no_dry_run``.

        Returns:
            A runner configured from the arguments.
        """
        default_run = cast(RunFunction, subprocess.run)  # noqa: SLD203
        orig_run: RunFunction = getattr(args, "orig_run", default_run)
        no_dry_run: bool = getattr(args, "no_dry_run", False)
        return cls(orig_run, no_dry_run=no_dry_run)
