"""The :class:`Filter` class and its dependencies.

:copyright: (c) 2024 Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.

"""

import dataclasses
import sys
from collections.abc import Generator, Iterable
from types import MappingProxyType
from typing import Annotated, Any, Union, get_args

# not 3.11 because we need frozen_default
if sys.version_info >= (3, 12):  # pragma: no cover
    from typing import dataclass_transform
else:  # pragma: no cover
    from typing_extensions import dataclass_transform

from .__version__ import *  # noqa: F401,F403

__all__ = ("Filter",)


@dataclass_transform(frozen_default=True)
class _Filter:
    """A slightly modified version of :class:`._Message`
    that is used to handle formatting.

    """

    _context: MappingProxyType[str, str]

    def __init_subclass__(cls) -> None:
        """Handle dataclass initialization and build the serialization
        context.

        """
        cls._context = MappingProxyType(
            {k: cls._get_context(a) for k, a in cls.__annotations__.items()}
        )
        dataclasses.dataclass(frozen=True)(cls)

    @classmethod
    def _get_context(cls, annotation: type) -> str:
        """Get the context information from the given type annotation."""
        return get_args(annotation)[1]

    @classmethod
    def _serializer(cls, value: Any) -> str:
        """Serializer that does the following:

        - Return the value if it is a string

        - Stringify integers

        - Format booleans as strings ("0" or "1")

        - Iterables into a comma-separated list of its items (also
            serialized)

        """
        if isinstance(value, str):
            for o, n in (("\n", "n"), ("\r", "r"), ("\f", "f")):
                value = value.replace(o, f"\\{n}")
            return value

        if isinstance(value, bool):
            return ("0", "1")[value]

        if isinstance(value, int):
            return str(value)

        try:
            return ",".join(cls._serializer(e) for e in value)
        except Exception:
            pass

        raise TypeError(f"Unknown type: {value.__class__.__name__!r}")

    def _serialize(self) -> Generator[tuple[str, Any], None, None]:
        """Generate segments that will later be turned into a dictionary
        in :meth:`.serialize`.

        """
        for k, v in self.__dict__.items():
            if v is None:
                continue

            yield (self._context[k], self._serializer(v))

    def serialize(self) -> dict[str, Any]:
        """Serialize this filter into a header dictionary."""
        return dict(self._serialize())


class Filter(_Filter):
    """A filter dataclass that stores filtering preferences used when
    polling and subscribing.

    :param since: Return cached messages since timestamp, duration or
        message ID.
    :type since: str | int | None
    :param scheduled: Include scheduled/delayed messages in message
        response.
    :type scheduled: bool | None
    :param id: Only return messages that match this exact message ID.
    :type id: str | None
    :param message: Only return messages that match this exact message
        string.
    :type message: str | None
    :param title: Only return messages that match this exact title
        string.
    :type title: str | None
    :param priority: Only return messages that match **any** priority
        given.
    :type priority: int | typing.Iterable[int] | None
    :param tags: Only return messages that match **all** listed tags.
    :type tags: str | typing.Iterable[str] | None

    """

    since: Annotated[Union[str, int, None], "X-Since"] = None
    """See the :paramref:`~Filter.since` parameter."""

    scheduled: Annotated[Union[bool, None], "X-Scheduled"] = None
    """See the :paramref:`~Filter.scheduled` parameter."""

    id: Annotated[Union[str, None], "X-ID"] = None
    """See the :paramref:`~Filter.id` parameter."""

    message: Annotated[Union[str, None], "X-Message"] = None
    """See the :paramref:`~Filter.message` parameter."""

    title: Annotated[Union[str, None], "X-Title"] = None
    """See the :paramref:`~Filter.title` parameter."""

    priority: Annotated[Union[int, Iterable[int], None], "X-Priority"] = None
    """See the :paramref:`~Filter.priority` parameter."""

    tags: Annotated[Union[str, Iterable[str], None], "X-Tags"] = None
    """See the :paramref:`~Filter.tags` parameter."""
