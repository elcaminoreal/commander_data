"""Ready-made command lines for common tools."""

import dataclasses
import pathlib
import os
import sys
from typing import Iterator, cast

from .api import COMMAND, CommandProtocol


@dataclasses.dataclass(frozen=True)
class _Python:  # noqa: SLD502,SLD503
    _run: CommandProtocol
    module: CommandProtocol
    pip: CommandProtocol

    def __getattr__(self, name: str) -> CommandProtocol:
        result: CommandProtocol = getattr(self._run, name)
        return result

    def __call__(self, *args: str, **kwargs: object) -> CommandProtocol:
        result: CommandProtocol = self._run(*args, **kwargs)
        return result

    def __iter__(self) -> Iterator[str]:
        return iter(self._run)

    @classmethod
    def create(cls, python: CommandProtocol) -> "_Python":
        """Build a Python command bundle from a base Python command.

        Args:
            python: The base Python command.

        Returns:
            A bundle with the Python, its ``-m`` form, and pip.
        """
        module = python("-m")
        pip = module("pip")
        return cls(_run=python, module=module, pip=pip)


GIT = COMMAND.git

LOCAL_PYTHON = _Python.create(COMMAND(sys.executable))
PATH_PYTHON = _Python.create(COMMAND.python)
BASE_PYTHON = _Python.create(COMMAND(sys.base_exec_prefix + "/bin/python3"))


def env_python(env: str | pathlib.Path) -> CommandProtocol:
    """Return a virtual-env-specific Python.

    Args:
        env: The directory of the virtual environment.

    Returns:
        A command object with this Python.
    """
    python_bin = os.fspath(pathlib.Path(env) / "bin" / "python")
    return cast(CommandProtocol, _Python.create(COMMAND(python_bin)))  # noqa: SLD203


DOCKER = COMMAND.docker

CONDA = COMMAND.conda
