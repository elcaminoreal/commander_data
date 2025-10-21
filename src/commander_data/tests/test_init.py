import unittest
from hamcrest import assert_that, equal_to, contains_string, has_item

from .. import __version__, COMMAND, run_all
from .. import common


class TestInit(unittest.TestCase):
    def test_version(self):
        assert_that(__version__, contains_string("."))


class TestRunAll(unittest.TestCase):
    def test_simple_run_all(self):
        keep = []
        run_all(
            keep.append,
            ["git", "commit"],
        )
        assert_that(keep, equal_to([["git", "commit"]]))

    def test_multiple_commands(self):
        keep = []
        run_all(
            keep.append,
            ["git", "add", "."],
            ["git", "commit", "-m", "test"],
            ["git", "push"],
        )
        assert_that(
            keep,
            equal_to([
                ["git", "add", "."],
                ["git", "commit", "-m", "test"],
                ["git", "push"],
            ]),
        )

    def test_run_all_with_kwargs(self):
        keep = []

        def capture_with_kwargs(cmd, **kwargs):
            keep.append({"cmd": cmd, "kwargs": kwargs})

        run_all(
            capture_with_kwargs,
            ["git", "status"],
            ["git", "log"],
            check=True,
            timeout=30,
        )
        assert_that(
            keep,
            equal_to([
                {"cmd": ["git", "status"], "kwargs": {"check": True, "timeout": 30}},
                {"cmd": ["git", "log"], "kwargs": {"check": True, "timeout": 30}},
            ]),
        )


class TestCommand(unittest.TestCase):
    def test_basic(self):
        assert_that(list(COMMAND), equal_to([]))

    def test_attribute(self):
        assert_that(list(COMMAND.git), equal_to(["git"]))

    def test_call_args(self):
        assert_that(list(COMMAND.git.init(".")), equal_to(["git", "init", "."]))

    def test_call_kwargs(self):
        assert_that(
            list(COMMAND.git.commit(all=None)), equal_to(["git", "commit", "--all"])
        )

    def test_call_kwargs_list(self):
        assert_that(
            list(COMMAND.pip.install(r=["r1.txt", "r2.txt"])),
            equal_to("pip install -r r1.txt -r r2.txt".split()),
        )

    def test_call_kwargs_dict(self):
        assert_that(
            list(COMMAND.copier(data=dict(a="b", c="d"))),
            equal_to(["copier", "--data", "a=b", "--data", "c=d"]),
        )

    def test_call_kwargs_str(self):
        assert_that(
            list(COMMAND.git.commit(message="checkpoint")),
            equal_to(["git", "commit", "--message", "checkpoint"]),
        )

    def test_short_arg(self):
        assert_that(
            list(COMMAND.python(m=None).venv("my-env")),
            equal_to("python -m venv my-env".split()),
        )

    def test_deeply_nested_attributes(self):
        assert_that(
            list(COMMAND.git.remote.add.origin("url")),
            equal_to(["git", "remote", "add", "origin", "url"]),
        )

    def test_mixed_args_and_kwargs(self):
        assert_that(
            list(COMMAND.docker.run("ubuntu", rm=None, it=None, name="test")),
            equal_to(["docker", "run", "--rm", "--it", "--name", "test", "ubuntu"]),
        )

    def test_special_characters_in_args(self):
        assert_that(
            list(COMMAND.git.commit(message="Fix bug #123: handle spaces & quotes")),
            equal_to([
                "git",
                "commit",
                "--message",
                "Fix bug #123: handle spaces & quotes",
            ]),
        )

    def test_empty_dict_value(self):
        assert_that(
            list(COMMAND.copier(data={})),
            equal_to(["copier"]),
        )

    def test_empty_list_value(self):
        assert_that(
            list(COMMAND.pip.install(r=[])),
            equal_to(["pip", "install"]),
        )


class TestCommonConstants(unittest.TestCase):
    def test_git_constant(self):
        assert_that(list(common.GIT.status), equal_to(["git", "status"]))

    def test_docker_constant(self):
        assert_that(list(common.DOCKER.ps), equal_to(["docker", "ps"]))

    def test_conda_constant(self):
        assert_that(list(common.CONDA.env.list), equal_to(["conda", "env", "list"]))

    def test_local_python_constant(self):
        result = list(common.LOCAL_PYTHON.pip.list)
        assert_that(result, has_item("pip"))
        assert_that(result, has_item("list"))

    def test_base_python_constant(self):
        result = list(common.BASE_PYTHON.pip.freeze)
        assert_that(result, has_item("pip"))
        assert_that(result, has_item("freeze"))
