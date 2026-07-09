commander_data
========================================

**Prepare data for commands.** Build the argument lists you hand to
``subprocess.run`` as composable, immutable Python instead of hand-typed
strings.

|pypi| |ci| |license| |pyversions|

Before:

.. code-block:: python

   import subprocess

   subprocess.run(["git", "commit", "--all", "--message", "quick commit"])

After:

.. code-block:: python

   import subprocess
   from commander_data import COMMAND

   subprocess.run(COMMAND.git.commit(all=None, message="quick commit"))

Same tokens, no shell, no quoting games: ``COMMAND`` builds the plain list
``["git", "commit", "--all", "--message", "quick commit"]`` and hands it
straight to ``subprocess``.

Installation
----------------------------------------

.. code-block:: console

   $ pip install commander-data

Requires Python 3.11 or newer. The core builder is pure standard library.

The 30-second version
----------------------------------------

``COMMAND`` is an immutable, iterable command builder. Access an attribute to
add a token, call it to add options and positional arguments, and iterate (or
``list(...)``) to get the token list. Every step returns a new builder.

.. code-block:: python

   from commander_data import COMMAND

   list(COMMAND)                                       # -> []
   list(COMMAND.git)                                   # -> ["git"]
   list(COMMAND.git.init("."))                         # -> ["git", "init", "."]
   list(COMMAND.git.commit(all=None))                  # -> ["git", "commit", "--all"]
   list(COMMAND.git.commit(message="checkpoint"))      # -> ["git", "commit", "--message", "checkpoint"]
   list(COMMAND.pip.install(r=["r1.txt", "r2.txt"]))   # -> ["pip", "install", "-r", "r1.txt", "-r", "r2.txt"]
   list(COMMAND.copier(data=dict(a="b", c="d")))       # -> ["copier", "--data", "a=b", "--data", "c=d"]
   list(COMMAND.python(m=None).venv("my-env"))         # -> ["python", "-m", "venv", "my-env"]
   list(COMMAND.some_script)                           # -> ["some-script"]

How the call syntax works
----------------------------------------

- **Attribute access appends one token**, turning ``_`` into ``-``:
  ``COMMAND.some_script`` builds ``["some-script"]``.
- **Calling appends options first, then positional arguments last**:
  ``COMMAND.git.init(".")`` builds ``["git", "init", "."]``.
- **Keyword names become option flags** — a multi-character ``key`` becomes
  ``--key`` (with ``_`` turned into ``-``); a single-character ``k`` becomes
  the short option ``-k``.
- **The keyword's value decides the shape**, dispatched on its type:

.. list-table::
   :header-rows: 1
   :widths: 22 40 38

   * - Value
     - Rule
     - Example
   * - scalar ``v``
     - option name, then ``str(v)`` (two tokens)
     - ``message="checkpoint"`` → ``"--message", "checkpoint"``
   * - ``None``
     - option name alone (a bare flag)
     - ``all=None`` → ``"--all"``
   * - ``list``
     - the option repeated once per item
     - ``r=["r1.txt", "r2.txt"]`` → ``"-r", "r1.txt", "-r", "r2.txt"``
   * - ``dict``
     - the option repeated per pair, each value as ``k=v``
     - ``data={"a": "b", "c": "d"}`` → ``"--data", "a=b", "--data", "c=d"``

Builders compose in any order, and each step returns a fresh builder you can
keep chaining or stash in a variable.

Batteries included
----------------------------------------

``commander_data.common`` ships ready-made builders (pure standard library):

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - Builder
     - Expands to
   * - ``GIT``
     - ``COMMAND.git``
   * - ``DOCKER``
     - ``COMMAND.docker``
   * - ``CONDA``
     - ``COMMAND.conda``
   * - ``LOCAL_PYTHON``
     - the currently-running interpreter (``sys.executable``)
   * - ``PATH_PYTHON``
     - ``python`` resolved from ``PATH``
   * - ``BASE_PYTHON``
     - the base-prefix interpreter (``sys.base_exec_prefix + "/bin/python3"``)
   * - ``env_python(env)``
     - the interpreter inside a virtualenv directory: ``<env>/bin/python``

Each Python helper also exposes ``.module`` (``<python> -m``) and ``.pip``
(``<python> -m pip``), and otherwise behaves like any ``COMMAND`` builder.

.. code-block:: python

   from commander_data.common import GIT, PATH_PYTHON, env_python

   # Reusing a prefix never mutates it:
   list(GIT)                                # -> ["git"]
   list(GIT.commit(message="wip"))          # -> ["git", "commit", "--message", "wip"]
   list(GIT)                                # -> ["git"]  (GIT itself is unchanged)

   list(PATH_PYTHON)                        # -> ["python"]
   list(PATH_PYTHON("script.py"))           # -> ["python", "script.py"]
   list(PATH_PYTHON.some_script)            # -> ["python", "some-script"]

   list(PATH_PYTHON.pip.install(r="requirements.txt"))
   # -> ["python", "-m", "pip", "install", "-r", "requirements.txt"]

   list(env_python("/home/me/venvs/my-env").pip.install(r="requirements.txt"))
   # -> ["/home/me/venvs/my-env/bin/python", "-m", "pip", "install", "-r", "requirements.txt"]

Running commands
----------------------------------------

``commander_data.run.Runner`` is a small, frozen wrapper (built with ``attrs``)
that runs the commands you build. Construct it with
``Runner(orig_run=subprocess.run, *, no_dry_run=False)``.

.. code-block:: python

   from commander_data import COMMAND
   from commander_data.run import Runner

   # Dry run by default: logs "Dry run, not running ..." and does NOT execute.
   Runner().run(COMMAND.echo("hello")).stdout.strip()                 # -> ''

   # Opt in to actually running:
   Runner(no_dry_run=True).run(COMMAND.echo("hello")).stdout.strip()  # -> 'hello'

   # safe_run always executes, whatever the dry-run setting:
   Runner().safe_run(COMMAND.echo("hello")).stdout.strip()            # -> 'hello'

- ``Runner.run(cmdargs, *args, **kwargs)`` is a **dry run by default**: it logs
  ``Dry run, not running <cmd>`` at ``INFO``, does not execute, and returns a
  fake result whose ``.stdout`` and ``.stderr`` are empty strings. Set
  ``no_dry_run=True`` on the ``Runner`` to make it really execute.
- ``Runner.safe_run(cmdargs, *args, **kwargs)`` **always executes**, regardless
  of the dry-run setting.

When a command really runs, the ``Runner`` logs ``Running <cmd>`` at ``INFO``
and defaults its subprocess keyword arguments to ``check=True``,
``capture_output=True``, and ``text=True`` (override any of them by passing
your own). On ``subprocess.CalledProcessError`` it attaches the captured
stdout and stderr to the exception with ``add_note`` and re-raises, so the
output you need to debug a failure is right there in the traceback. Logging
goes to ``logging.getLogger("commander_data.run")``, so nothing is printed
until you configure logging.

``Runner.from_args`` builds a ``Runner`` from an ``argparse.Namespace``,
reading optional ``orig_run`` and ``no_dry_run`` attributes off it — the clean
way to wire a ``--no-dry-run`` flag to your runner, as shown below.

Running several commands
----------------------------------------

``run_all(run, *commands, **kwargs)`` calls ``run(command, **kwargs)`` for
every command:

.. code-block:: python

   import subprocess
   from commander_data import COMMAND, run_all

   run_all(
       subprocess.run,
       COMMAND.git.add("."),
       COMMAND.git.commit(message="release"),
   )

The ``run`` can be anything callable — ``subprocess.run`` to execute the
commands, a ``Runner``'s ``.run`` / ``.safe_run``, or a list's bound
``.append`` to collect them instead of running them.

Putting it together
----------------------------------------

A small provisioning script: create a virtualenv, install requirements into
it, and commit the result. It previews every command by default and only
touches the system when invoked with ``--no-dry-run``.

.. code-block:: python

   import argparse
   import logging

   from commander_data import run_all
   from commander_data.common import GIT, PATH_PYTHON, env_python
   from commander_data.run import Runner

   logging.basicConfig(level=logging.INFO)

   parser = argparse.ArgumentParser()
   parser.add_argument("--no-dry-run", action="store_true")
   args = parser.parse_args()

   runner = Runner.from_args(args)

   env = "my-env"
   run_all(
       runner.run,
       PATH_PYTHON.module.venv(env),                       # python -m venv my-env
       env_python(env).pip.install(r="requirements.txt"),  # my-env/bin/python -m pip install -r requirements.txt
       GIT.add("."),                                       # git add .
       GIT.commit(all=None, message="Set up environment"), # git commit --all --message 'Set up environment'
   )

Run with no arguments, it logs each command as a dry run and changes nothing;
add ``--no-dry-run`` to actually create the environment and make the commit.
Every command is already a plain list of tokens by the time it reaches
``runner.run`` — there is nothing to quote and no shell to defend against.

Why it exists
----------------------------------------

Hand-writing argument lists like ``["git", "commit", "--all", "--message",
msg]`` is noisy and easy to get wrong, and f-strings shoved through a shell
invite quoting and injection bugs. ``commander_data`` lets you write commands
that read like Python method calls while producing a plain list of string
tokens — no shell involved — so it works with any command yet keeps the common
shapes concise. Because every builder is immutable, shared prefixes like
``GIT`` or a configured interpreter are safe to reuse everywhere.

Requirements
----------------------------------------

- Python 3.11+ (it uses ``typing.Self``); tested on CPython 3.11 and 3.12.
- The core builder (``COMMAND``, ``commander_data.api``,
  ``commander_data.common``) needs only the standard library.
- ``commander_data.run`` additionally depends on ``attrs``.

Development
----------------------------------------

Development is driven by `nox <https://nox.thea.codes/>`_. The default
sessions are:

- ``tests`` — ``virtue`` + ``coverage``, enforcing 100% branch coverage on
  Python 3.11 and 3.12
- ``lint`` — ``black --check`` and ``flake8``
- ``mypy`` — type checking
- ``docs`` — Sphinx, built with ``-W`` (warnings are errors)
- ``build`` — builds a wheel

.. code-block:: console

   $ pip install nox
   $ nox

CI runs these sessions on 3.11 and 3.12 via
``.github/workflows/pr-main.yml``; ``release.yml`` publishes to PyPI through
OIDC / trusted publishing on every push to ``trunk``. Versions are
calendar-based, derived from git by ``autocalver``. The documentation (Sphinx
with autodoc: index, quick-start, api-reference) lives under ``doc/``.

License and author
----------------------------------------

MIT-licensed. Written by Moshe Zadka.

- Source and issues: https://github.com/elcaminoreal/commander_data
- PyPI: https://pypi.org/project/commander-data/

.. |pypi| image:: https://img.shields.io/pypi/v/commander-data.svg
   :target: https://pypi.org/project/commander-data/
   :alt: PyPI version

.. |ci| image:: https://github.com/elcaminoreal/commander_data/actions/workflows/pr-main.yml/badge.svg
   :target: https://github.com/elcaminoreal/commander_data/actions/workflows/pr-main.yml
   :alt: CI status

.. |license| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

.. |pyversions| image:: https://img.shields.io/badge/python-3.11%2B-blue.svg
   :target: https://pypi.org/project/commander-data/
   :alt: Python 3.11+
