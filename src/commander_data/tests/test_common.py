"""Tests for the ready-made command lines."""

import unittest
from typing import Iterable

from hamcrest import assert_that, equal_to

from .. import common


class TestPython(unittest.TestCase):
    """Tests for the Python command bundles."""

    def test_python_commands(self) -> None:
        """The path Python bundle builds the expected command lines."""
        cases: list[tuple[Iterable[str], str]] = [
            (
                common.PATH_PYTHON.pip.install(r="requirements.txt"),
                "python -m pip install -r requirements.txt",
            ),
            (common.PATH_PYTHON, "python"),
            (common.PATH_PYTHON("script.py"), "python script.py"),
            (common.PATH_PYTHON.some_script, "python some-script"),
        ]
        for command, expected in cases:
            with self.subTest(expected=expected):
                assert_that(list(command), equal_to(expected.split()))

    def test_env_python(self) -> None:
        """A virtual-env Python uses the env's interpreter."""
        cmd = "/home/me/venvs/my-env/bin/python -m pip install -r requirements.txt"
        command = common.env_python("/home/me/venvs/my-env").pip.install(
            r="requirements.txt"
        )
        assert_that(list(command), equal_to(cmd.split()))
