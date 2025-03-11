"""Action definitions.

:copyright: (c) 2024 Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.

"""

import dataclasses
import sys
from collections.abc import Generator, Mapping
from types import MappingProxyType
from typing import Annotated, Any, Union, final, get_args, get_origin

if sys.version_info >= (3, 10):  # pragma: no cover
    from typing import TypeAlias
else:  # pragma: no cover
    from typing_extensions import TypeAlias
# not 3.11 because we need frozen_default
if sys.version_info >= (3, 12):  # pragma: no cover
    from typing import dataclass_transform
else:  # pragma: no cover
    from typing_extensions import dataclass_transform

from .__version__ import *  # noqa: F401,F403
from ._internals import WrappingDataclass
from .enums import HTTPMethod

__all__ = (
    "ViewAction",
    "BroadcastAction",
    "HTTPAction",
    "ReceivedViewAction",
    "ReceivedBroadcastAction",
    "ReceivedHTTPAction",
    "ReceivedAction",
)


@dataclass_transform(frozen_default=True)
class _Action:
    """Action base class that is used to handle formatting."""

    _action: str
    _context: MappingProxyType[str, bool]

    def __init_subclass__(cls, action: str) -> None:
        """Handle subclass arguments, initialize dataclass, and build
        the serialization context.

        :param action: The name of the action.
        :type action: str

        """
        cls._action = action
        cls._context = MappingProxyType(
            {k: cls._get_context(a) for k, a in cls.__annotations__.items()}
        )
        dataclasses.dataclass(frozen=True)(cls)

    @final
    @classmethod
    def _get_context(cls, annotation: type) -> bool:
        """Get the context information from the given type annotation.

        :param annotation: The annotation to get the context from.
        :type annotation: type
        :return: Whether or not this annotation should be considered an
            assignment. That is, whether it should be formatted as
            ``k.x=y`` as opposed to ``x=y``.
        :rtype: bool

        """
        origin = get_origin(annotation)

        if origin is not Annotated:
            return True

        # typing.Annotated must have at least two arguments, so we know
        # that index 1 will not be out of range
        return get_args(annotation)[1]

    @final
    @classmethod
    def _default_serializer(cls, key: Union[str, None], value: Any) -> str:
        """Serializer used to serialize values.

        Does the following:

            - Escapes backslashes (``\\``) and double quotes (``"``) in
                strings

            - Encloses strings in double quotes if needed

            - Formats booleans as strings

            - Formats mappings as ``<key>.k=v,...``
                (e.g. ``extras.x=y``)

        :param key: A key that must be provided if the value is a
            mapping.
        :type key: str | None
        :param value: The value to serialize.
        :type value: typing.Any

        :return: The serialized value.
        :rtype: str

        """
        if isinstance(value, str):
            for k in ("\\", '"'):
                value = value.replace(k, f"\\{k}")
            if set(value).intersection({",", ";", "=", "'", '"', "\\"}):
                return f'"{value}"'
            return value

        if isinstance(value, bool):
            return ("false", "true")[value]

        if key and isinstance(value, Mapping):
            return ",".join(
                f"{key}.{k}={cls._default_serializer(None, v)}"
                for k, v in value.items()
            )

        raise TypeError(f"Unknown type: {value.__class__.__name__!r}")

    @final
    def _serialize(self) -> Generator[str, None, None]:
        """Generate segments that will later be joined in
        :meth:`.serialize`.

        """
        yield self._action

        for k, v in self.__dict__.items():
            if v is None:
                continue

            assign = self._context[k]
            value = self._default_serializer(k, v)

            if not assign:
                yield value
                continue

            yield f"{k}={value}"

    @final
    def serialize(self) -> str:
        """Serialize this action into a single header value.

        :returns: The serialized header value.
        :rtype: str

        """
        return ",".join(self._serialize())


class ViewAction(_Action, action="view"):
    """A serializable view action.

    :param label: The action label.
    :type label: str
    :param url: The URL to open when the action is activated.
    :type url: str
    :param clear: Whether or not to clear the notification after the
        action is activated.
    :type clear: bool | None, optional

    """

    label: Annotated[str, False]
    """See the :paramref:`~ViewAction.label` parameter."""

    url: Annotated[str, False]
    """See the :paramref:`~ViewAction.url` parameter."""

    clear: Union[bool, None] = None
    """See the :paramref:`~ViewAction.clear` parameter."""


class BroadcastAction(_Action, action="broadcast"):
    """A serializable broadcast action.

    :param label: The action label.
    :type label: str
    :param intent: The Android intent name.
    :type intent: str | None, optional
    :param extras: The Android intent extras.
    :type extras: typing.Mapping[str, str] | None, optional
    :param clear: Whether or not to clear the notification after the
        action is activated.
    :type clear: bool | None, optional

    """

    label: Annotated[str, False]
    """See the :paramref:`~BroadcastAction.label` parameter."""

    intent: Union[str, None] = None
    """See the :paramref:`~BroadcastAction.intent` parameter."""

    extras: Annotated[Union[Mapping[str, str], None], False] = None
    """See the :paramref:`~BroadcastAction.extras` parameter."""

    clear: Union[bool, None] = None
    """See the :paramref:`~BroadcastAction.clear` parameter."""


class HTTPAction(_Action, action="http"):
    """A serializable HTTP action.

    :param label: The action label.
    :type label: str
    :param url: The URL to send the HTTP request to.
    :type url: str
    :param method: The HTTP method.
    :type method: str | None, optional
    :param headers: The HTTP headers.
    :type headers: typing.Mapping[str, str] | None, optional
    :param body: The HTTP body.
    :type body: str | None, optional
    :param clear: Whether or not to clear the notification after the
        action is activated.
    :type clear: bool | None, optional

    """

    label: Annotated[str, False]
    """See the :paramref:`~HTTPAction.label` parameter."""

    url: Annotated[str, False]
    """See the :paramref:`~HTTPAction.url` parameter."""

    method: Union[str, None] = None
    """See the :paramref:`~HTTPAction.method` parameter."""

    headers: Annotated[Union[Mapping[str, str], None], False] = None
    """See the :paramref:`~HTTPAction.headers` parameter."""

    body: Union[str, None] = None
    """See the :paramref:`~HTTPAction.body` parameter."""

    clear: Union[bool, None] = None
    """See the :paramref:`~HTTPAction.clear` parameter."""


class ReceivedViewAction(WrappingDataclass):
    """A received view action. Similar to :class:`ViewAction`, but
    cannot be serialized.

    :param id: The action ID.
    :type id: str
    :param label: The action label.
    :type label: str
    :param url: The URL to open when the action is activated.
    :type url: str
    :param clear: Whether or not to clear the notification after the
        action is activated.
    :type clear: bool

    """

    id: str
    """See the :paramref:`~ReceivedViewAction.id` parameter."""

    label: str
    """See the :paramref:`~ReceivedViewAction.label` parameter."""

    url: str
    """See the :paramref:`~ReceivedViewAction.url` parameter."""

    clear: bool
    """See the :paramref:`~ReceivedViewAction.clear` parameter."""


class ReceivedBroadcastAction(WrappingDataclass):
    """A received broadcast action. Similar to :class:`BroadcastAction`,
    but cannot be serialized.

    :param id: The action ID.
    :type id: str
    :param label: The action label.
    :type label: str
    :param clear: Whether or not to clear the notification after the
        action is activated.
    :type clear: bool
    :param intent: The Android intent name.
    :type intent: str | None, optional
    :param extras: The Android intent extras.
    :type extras: dict[str, str] | None, optional

    """

    id: str
    """See the :paramref:`~ReceivedBroadcastAction.id` parameter."""

    label: str
    """See the :paramref:`~ReceivedBroadcastAction.label` parameter."""

    clear: bool
    """See the :paramref:`~ReceivedBroadcastAction.clear` parameter."""

    intent: Union[str, None] = None
    """See the :paramref:`~ReceivedBroadcastAction.intent` parameter."""

    extras: Union[dict[str, str], None] = None
    """See the :paramref:`~ReceivedBroadcastAction.extras` parameter."""


class ReceivedHTTPAction(WrappingDataclass):
    """A received HTTP action. Similar to :class:`HTTPAction`,
    but cannot be serialized.

    :param id: The action ID.
    :type id: str
    :param label: The action label.
    :type label: str
    :param url: The URL to send the HTTP request to.
    :type url: str
    :param clear: Whether or not to clear the notification after the
        action is activated.
    :type clear: bool
    :param method: The HTTP method.
    :type method: HTTPMethod | None, optional
    :param headers: The HTTP headers.
    :type headers: dict[str, str] | None, optional
    :param body: The HTTP body.
    :type body: str | None, optional

    """

    id: str
    """See the :paramref:`~ReceivedHTTPAction.id` parameter."""

    label: str
    """See the :paramref:`~ReceivedHTTPAction.label` parameter."""

    url: str
    """See the :paramref:`~ReceivedHTTPAction.url` parameter."""

    clear: bool
    """See the :paramref:`~ReceivedHTTPAction.clear` parameter."""

    method: Annotated[Union[HTTPMethod, None], HTTPMethod] = None
    """See the :paramref:`~ReceivedHTTPAction.method` parameter."""

    headers: Union[dict[str, str], None] = None
    """See the :paramref:`~ReceivedHTTPAction.headers` parameter."""

    body: Union[str, None] = None
    """See the :paramref:`~ReceivedHTTPAction.body` parameter."""


ReceivedAction: TypeAlias = Union[
    ReceivedViewAction, ReceivedBroadcastAction, ReceivedHTTPAction
]
