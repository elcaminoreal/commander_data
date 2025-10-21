import argparse
import logging
import logging.handlers
import unittest
from hamcrest import (
    assert_that,
    equal_to,
    has_property,
    calling,
    raises,
    starts_with,
    all_of,
    has_item,
)

from .. import run
from .. import COMMAND


class TestRunner(unittest.TestCase):
    def test_basic_runner(self):
        runner = run.Runner()
        res = runner.safe_run(COMMAND.echo("hello"))
        assert_that(res.stdout.strip(), equal_to("hello"))

    def test_dry_runner(self):
        runner = run.Runner()
        res = runner.run(COMMAND.echo("hello"))
        assert_that(res.stdout.strip(), equal_to(""))

    def test_no_dry_runner(self):
        runner = run.Runner(no_dry_run=True)
        res = runner.run(COMMAND.echo("hello"))
        assert_that(res.stdout.strip(), equal_to("hello"))

    def test_args_runner(self):
        runner = run.Runner.from_args(argparse.Namespace())
        res = runner.safe_run(COMMAND.echo("hello"))
        assert_that(res.stdout.strip(), equal_to("hello"))

    def test_runner_fail(self):
        runner = run.Runner.from_args(argparse.Namespace())
        assert_that(
            calling(runner.safe_run).with_args(COMMAND.false),
            raises(
                Exception,
                matching=has_property(
                    "__notes__",
                    all_of(
                        has_item(starts_with("STDOUT:")),
                        has_item(starts_with("STDERR:")),
                    ),
                ),
            ),
        )


class TestRunnerLogging(unittest.TestCase):
    def setUp(self):
        self.log_records = []
        self.handler = logging.handlers.MemoryHandler(capacity=1000)
        self.handler.setLevel(logging.INFO)
        logger = logging.getLogger("commander_data.run")
        logger.addHandler(self.handler)
        logger.setLevel(logging.INFO)

    def tearDown(self):
        logger = logging.getLogger("commander_data.run")
        logger.removeHandler(self.handler)

    def test_safe_run_logs_execution(self):
        runner = run.Runner()
        runner.safe_run(COMMAND.echo("test"))
        self.handler.flush()
        logs = [record.getMessage() for record in self.handler.buffer]
        assert_that(logs, has_item(starts_with("Running ['echo', 'test']")))

    def test_dry_run_logs_skip(self):
        runner = run.Runner()
        runner.run(COMMAND.echo("test"))
        self.handler.flush()
        logs = [record.getMessage() for record in self.handler.buffer]
        assert_that(logs, has_item(starts_with("Dry run, not running ['echo', 'test']")))

    def test_no_dry_run_logs_execution(self):
        runner = run.Runner(no_dry_run=True)
        runner.run(COMMAND.echo("test"))
        self.handler.flush()
        logs = [record.getMessage() for record in self.handler.buffer]
        assert_that(logs, has_item(starts_with("Running ['echo', 'test']")))
