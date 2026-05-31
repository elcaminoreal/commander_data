"""Build command lines for :code:`subprocess.run` and friends."""

import dataclasses
import functools
from typing import Iterator, Iterable, Mapping, Protocol, Self


@functools.singledispatch
def _get_value_parts(value: object, key: str) -> Iterator[str]:
    yield key
    yield str(value)


@_get_value_parts.register(type(None))
def _get_value_parts_none(value: None, key: str) -> Iterator[str]:
    yield key


@_get_value_parts.register(list)
def _get_value_parts_list(value: Iterable[object], key: str) -> Iterator[str]:
    for item in value:
        yield from _get_value_parts(item, key)


@_get_value_parts.register(dict)
def _get_value_parts_dict(value: Mapping[str, str], key: str) -> Iterator[str]:
    for d_key, d_value in value.items():
        yield key
        yield f"{d_key}={d_value}"


def _parse_kwargs(kwargs: Mapping[str, object]) -> Iterator[str]:
    for key, value in kwargs.items():
        if len(key) == 1:
            key = "-" + key
        else:
            key = "--" + key.replace("_", "-")
        yield from _get_value_parts(value, key)


class CommandProtocol(Protocol):  # pragma: no cover
    """An immutable, composable command line."""

    def __iter__(self) -> Iterator[str]:
        """Iterate over the words of the command line.

        Returns:
            An iterator over the command words.
        """

    def __getattr__(self, name: str) -> Self:
        """Return a command with ``name`` appended as a sub-command.

        Args:
            name: The sub-command name.

        Returns:
            A command with the sub-command appended.
        """

    def __call__(self, *args: str, **kwargs: object) -> Self:
        """Return a command with the given arguments appended.

        Args:
            *args: Positional arguments to append.
            **kwargs: Keyword arguments to render as options.

        Returns:
            A command with the arguments appended.
        """


@dataclasses.dataclass
class _Command:  # noqa: SLD501,SLD502,SLD503
    _contents: list[str] = dataclasses.field(default_factory=list)

    def __iter__(self) -> Iterator[str]:
        return iter(self._contents)

    def extend(self, things: Iterable[str]) -> Self:
        """Return a copy of this command with ``things`` appended.

        Args:
            things: The words to append.

        Returns:
            A new command with the words appended.
        """
        return dataclasses.replace(self, _contents=self._contents + list(things))

    def __getattr__(self, name: str) -> Self:
        return self.extend([name.replace("_", "-")])

    def __call__(self, *args: str, **kwargs: object) -> Self:
        return self.extend(_parse_kwargs(kwargs)).extend(args)


COMMAND = _Command()


class RunCallable(Protocol):  # pragma: no cover
    """A callable that runs a command line."""

    def __call__(self, command: Iterable[str], /, **kwargs: object) -> object:
        """Run ``command``, passing along any keyword arguments.

        Args:
            command: The command line to run.
            **kwargs: Extra arguments for the underlying runner.

        Returns:
            Whatever the underlying runner returns.
        """


def run_all(run: RunCallable, *commands: Iterable[str], **kwargs: object) -> None:
    """Run several command lines with the same runner.

    Args:
        run: The callable used to run each command.
        *commands: The command lines to run.
        **kwargs: Extra arguments forwarded to ``run`` for every command.
    """
    for a_command in commands:
        run(a_command, **kwargs)
