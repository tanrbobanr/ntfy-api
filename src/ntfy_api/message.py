"""The `Message` class and its dependencies.

:copyright: (c) 2024 Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.

"""

import dataclasses
import sys
from collections.abc import Callable, Generator, Iterable
from typing import Annotated, Any, BinaryIO, Protocol, Union, get_args

# not 3.11 because we need frozen_default
if sys.version_info >= (3, 12):  # pragma: no cover
    from typing import dataclass_transform
else:  # pragma: no cover
    from typing_extensions import dataclass_transform

from types import MappingProxyType

from .__version__ import *  # noqa: F401,F403
from ._internals import WrappingDataclass, _unwrap_static
from .actions import (
    ReceivedAction,
    ReceivedBroadcastAction,
    ReceivedHTTPAction,
    ReceivedViewAction,
    _Action,
)
from .enums import Event, Priority, Tag

__all__ = ("Message", "ReceivedAttachment", "ReceivedMessage")


@dataclass_transform(frozen_default=True)
class _Message:
    """Message base class that is used to handle formatting."""

    _context: MappingProxyType[str, tuple[str, Callable[[Any], Any]]]

    def __init_subclass__(cls) -> None:
        """Handle dataclass initialization and build the serialization
        context.

        """
        cls._context = MappingProxyType(
            {k: cls._get_context(a) for k, a in cls.__annotations__.items()}
        )
        dataclasses.dataclass(frozen=True)(cls)

    @classmethod
    def _get_context(
        cls, annotation: type
    ) -> tuple[str, Callable[[Any], Any]]:
        """Get the context information from the given type annotation."""
        args = get_args(annotation)
        serializer: Callable[[Any], Any] = cls._default_serializer

        if len(args) == 3:
            serializer = args[2]

        return (args[1], serializer)

    @staticmethod
    def _default_serializer(value: Any) -> str:
        """Default serializer that does the following:

        - Return the value if it is a string

        - Stringify integers

        - Format booleans as strings

        """
        if isinstance(value, str):
            for o, n in (("\n", "n"), ("\r", "r"), ("\f", "f")):
                value = value.replace(o, f"\\{n}")
            return value

        if isinstance(value, bool):
            return ("0", "1")[value]

        if isinstance(value, int):
            return str(value)

        raise TypeError(f"Unknown type: {value.__class__.__name__!r}")

    def _serialize(self) -> Generator[tuple[str, Any], None, None]:
        """Generate segments that will later be turned into a dictionary
        in :meth:`.serialize`.

        """
        for k, v in self.__dict__.items():
            if v is None:
                continue

            key, serializer = self._context[k]

            yield (key, _unwrap_static(serializer)(v))

    def serialize(self) -> dict[str, Any]:
        """Serialize this message into a header dictionary."""
        return dict(self._serialize())


class Message(_Message):
    """Represents a message that will be published via
    :meth:`.NtfyClient.publish`.

    :param topic: The topic this message should be sent to.
    :type topic: str
    :param message: The message body.
    :type message: str
    :param title: The message title.
    :type title: str
    :param priority: The message priority.
    :type priority: int
    :param tags: A set of tags that will be displayed along with the
        message. If the tag is a supported emoji short code (i.e.
        those found in the :class:`.Tag` enum), they will be displayed
        to the left of the title. Unrecognized tags will be displayed
        below the message.
    :type tags: str | typing.Iterable[str]
    :param markdown: Whether or not to render the message with markdown.
    :type markdown: bool
    :param delay: When to schedule the message. This should be either a
        unix timestamp or a natural-language date/time or offset
        (see https://github.com/olebedev/when). Any value between 10
        seconds and 3 days may be used.
    :type delay: int | str
    :param templating: If :py:obj:`True`, :paramref:`.data` will be
        interpreted as JSON and used as the template context of
        Go-styled templates in the :paramref:`.message` and
        :paramref:`.title`. Mutually exclusive with
        :paramref:`filename`.
    :type templating: bool
    :param actions: Actions attached to this message.
    :type actions: typing.Iterable[_Action]
    :param click: The redirect URL that will be activated when the
        notification is clicked.
    :type click: str
    :param attachment: An externally-hosted attachment to be included in
        the message.
    :type attachment: str
    :param filename: The filename of the included attachment. If not
        provided, it will be derived from the URL resource
        identifier. Mutually exclusive with :paramref:`templating`.
    :type filename: str
    :param icon: An externally-hosted icon that will be displayed next
        to the notification.
    :type icon: str
    :param email: The email address to forward this message to.
    :type email: str
    :param call: The phone number to forward this message to.
    :type call: str
    :param cache: Whether or not to make use of the message cache.
    :type cache: bool
    :param firebase: Whether or not to enable Firebase.
    :type firebase: bool
    :param unified_push: Whether or not to enable UnifiedPush.
    :type unified_push: bool
    :param data: If defined, it should be one of the following:

        * If sending a local file as an attachment, the raw
            attachment file data. If doing so, it is recommended to
            use the :paramref:`filename` option in addition to this.

        * If using templating, the template data.

    :type data: typing.BinaryIO | dict[str, typing.Any]

    """

    def __post_init__(self) -> None:
        if self.templating is not None and self.filename is not None:
            raise ValueError(
                "The 'templating' and 'filename' options for 'Message' objects"
                " are mutually exclusive"
            )

    @staticmethod
    def _ignore(value: Any) -> Any:
        return value

    @staticmethod
    def _tags_serializer(value: Union[str, Iterable[str]]) -> str:
        if isinstance(value, str):
            return value
        return ",".join(value)

    @staticmethod
    def _actions_serializer(value: Iterable[_Action]) -> str:
        return ";".join(v.serialize() for v in value)

    topic: Annotated[Union[str, None], "__topic__"] = None
    """See the :paramref:`~Message.topic` parameter."""

    message: Annotated[Union[str, None], "X-Message"] = None
    """See the :paramref:`~Message.message` parameter."""

    title: Annotated[Union[str, None], "X-Title"] = None
    """See the :paramref:`~Message.title` parameter."""

    priority: Annotated[Union[int, None], "X-Priority"] = None
    """See the :paramref:`~Message.priority` parameter."""

    tags: Annotated[
        Union[str, Iterable[str], None], "X-Tags", _tags_serializer
    ] = None
    """See the :paramref:`~Message.tags` parameter."""

    markdown: Annotated[Union[bool, None], "X-Markdown"] = None
    """See the :paramref:`~Message.markdown` parameter."""

    delay: Annotated[Union[int, str, None], "X-Delay"] = None
    """See the :paramref:`~Message.delay` parameter."""

    templating: Annotated[Union[bool, None], "X-Template"] = None
    """See the :paramref:`~Message.templating` parameter."""

    actions: Annotated[
        Union[Iterable[_Action], None], "X-Actions", _actions_serializer
    ] = None
    """See the :paramref:`~Message.actions` parameter."""

    click: Annotated[Union[str, None], "X-Click"] = None
    """See the :paramref:`~Message.click` parameter."""

    attachment: Annotated[Union[str, None], "X-Attach"] = None
    """See the :paramref:`~Message.attachment` parameter."""

    filename: Annotated[Union[str, None], "X-Filename"] = None
    """See the :paramref:`~Message.filename` parameter."""

    icon: Annotated[Union[str, None], "X-Icon"] = None
    """See the :paramref:`~Message.icon` parameter."""

    email: Annotated[Union[str, None], "X-Email"] = None
    """See the :paramref:`~Message.email` parameter."""

    call: Annotated[Union[str, None], "X-Call"] = None
    """See the :paramref:`~Message.call` parameter."""

    cache: Annotated[Union[bool, None], "X-Cache"] = None
    """See the :paramref:`~Message.cache` parameter."""

    firebase: Annotated[Union[bool, None], "X-Firebase"] = None
    """See the :paramref:`~Message.firebase` parameter."""

    unified_push: Annotated[Union[bool, None], "X-UnifiedPush"] = None
    """See the :paramref:`~Message.unified_push` parameter."""

    data: Annotated[
        Union[BinaryIO, dict[str, Any], None], "__data__", _ignore
    ] = None
    """See the :paramref:`~Message.data` parameter."""

    def get_args(
        self,
    ) -> tuple[Union[str, None], dict[str, str], dict[str, Any]]:
        """Get the topic, headers, and POST kwargs."""
        headers = self.serialize()
        topic = headers.pop("__topic__", None)
        data = headers.pop("__data__", None)

        if data is None:
            kwargs = {}
        elif self.templating is True:
            kwargs = {"json": data}
        else:
            kwargs = {"data": data}

        return (topic, headers, kwargs)


class ReceivedAttachment(Protocol):
    """Protocol defining the interface for an attachment in a received
    message.

    :param name: Name of the attachment.
    :type name: str
    :param url: URL of the attachment.
    :type url: str
    :param type: Mime type of the attachment (only if uploaded to ntfy
        server).
    :type type: str | None
    :param size: Size in bytes (only if uploaded to ntfy server).
    :type size: int | None
    :param expires: Expiry date as Unix timestamp (only if uploaded to
        ntfy server).
    :type expires: int | None

    """

    name: str
    """See the :paramref:`~ReceivedAttachment.name` parameter."""

    url: str
    """See the :paramref:`~ReceivedAttachment.url` parameter."""

    type: Union[str, None]
    """See the :paramref:`~ReceivedAttachment.type` parameter."""

    size: Union[int, None]
    """See the :paramref:`~ReceivedAttachment.size` parameter."""

    expires: Union[int, None]
    """See the :paramref:`~ReceivedAttachment.expires` parameter."""


class ReceivedMessage(Protocol):
    """Protocol defining the interface for a message received from the
    ntfy server.

    :param id: Randomly chosen message identifier.
    :type id: str
    :param time: Message datetime as Unix timestamp.
    :type time: int
    :param event: Type of event.
    :type event: Event
    :param topic: Topics the message is associated with.
    :type topic: str
    :param message: Message body.
    :type message: str | None
    :param expires: When the message will be deleted.
    :type expires: int | None
    :param title: Message title.
    :type title: str | None
    :param tags: List of tags that may map to emojis.
    :type tags: tuple[Tag, ...] | None
    :param priority: Message priority.
    :type priority: Priority | None
    :param click: Website opened when notification is clicked.
    :type click: str | None
    :param actions: Action buttons that can be displayed.
    :type actions: tuple[ReceivedAction, ...] | None
    :param attachment: Details about an attachment if present.
    :type attachment: ReceivedAttachment | None
    :param icon: The icon URL sent with the message.
    :type icon: str | None
    :param content_type: The content type.
    :type content_type: str | None

    """

    id: str
    """See the :paramref:`~ReceivedMessage.id` parameter."""

    time: int
    """See the :paramref:`~ReceivedMessage.time` parameter."""

    event: Event
    """See the :paramref:`~ReceivedMessage.event` parameter."""

    topic: str
    """See the :paramref:`~ReceivedMessage.topic` parameter."""

    message: Union[str, None]
    """See the :paramref:`~ReceivedMessage.message` parameter."""

    expires: Union[int, None]
    """See the :paramref:`~ReceivedMessage.expires` parameter."""

    title: Union[str, None]
    """See the :paramref:`~ReceivedMessage.title` parameter."""

    tags: Union[tuple[Tag, ...], None]
    """See the :paramref:`~ReceivedMessage.tags` parameter."""

    priority: Union[Priority, None]
    """See the :paramref:`~ReceivedMessage.priority` parameter."""

    click: Union[str, None]
    """See the :paramref:`~ReceivedMessage.click` parameter."""

    actions: Union[tuple[ReceivedAction, ...], None]
    """See the :paramref:`~ReceivedMessage.actions` parameter."""

    attachment: Union[ReceivedAttachment, None]
    """See the :paramref:`~ReceivedMessage.attachment` parameter."""

    icon: Union[str, None]
    """See the :paramref:`~ReceivedMessage.icon` parameter."""

    content_type: Union[str, None]
    """See the :paramref:`~ReceivedMessage.content_type` parameter."""


class _ReceivedAttachment(ReceivedAttachment, WrappingDataclass):
    """Private implementation of the :class:`ReceivedAttachment`
    protocol.

    :param name: Name of the attachment.
    :type name: str
    :param url: URL of the attachment.
    :type url: str
    :param type: Mime type of the attachment (only if uploaded to ntfy
        server).
    :type type: str | None
    :param size: Size in bytes (only if uploaded to ntfy server).
    :type size: int | None
    :param expires: Expiry date as Unix timestamp (only if uploaded to
        ntfy server).
    :type expires: int | None

    """

    name: str
    """See the :paramref:`~_ReceivedAttachment.name` parameter."""

    url: str
    """See the :paramref:`~_ReceivedAttachment.url` parameter."""

    type: Union[str, None] = None
    """See the :paramref:`~_ReceivedAttachment.type` parameter."""

    size: Union[int, None] = None
    """See the :paramref:`~_ReceivedAttachment.size` parameter."""

    expires: Union[int, None] = None
    """See the :paramref:`~_ReceivedAttachment.expires` parameter."""


class _ReceivedMessage(ReceivedMessage, WrappingDataclass):
    """Private implementation of the :class:`ReceivedMessage` protocol.

    :param id: Randomly chosen message identifier.
    :type id: str
    :param time: Message datetime as Unix timestamp.
    :type time: int
    :param event: Type of event.
    :type event: Event
    :param topic: Topics the message is associated with.
    :type topic: str
    :param message: Messag body.
    :type message: str | None
    :param expires: When the message will be deleted.
    :type expires: int | None
    :param title: Message title.
    :type title: str | None
    :param tags: List of tags that may map to emojis.
    :type tags: tuple[Tag, ...] | None
    :param priority: Message priority.
    :type priority: Priority | None
    :param click: Website opened when notification is clicked.
    :type click: str | None
    :param actions: Action buttons that can be displayed.
    :type actions: tuple[ReceivedAction, ...] | None
    :param attachment: Details about an attachment if present.
    :type attachment: ReceivedAttachment | None
    :param icon: The icon URL sent with the message.
    :type icon: str | None
    :param content_type: The content type.
    :type content_type: str | None

    """

    @staticmethod
    def _parse_actions(
        actions: list[dict[str, Any]],
    ) -> tuple[ReceivedAction, ...]:
        return tuple(
            dict[str, type[ReceivedAction]]({
                "view": ReceivedViewAction,
                "broadcast": ReceivedBroadcastAction,
                "http": ReceivedHTTPAction,
            })[a.pop("action")].from_json(a)
            for a in actions
        )

    @staticmethod
    def _parse_tags(tags: list[str]) -> tuple[Tag, ...]:
        return tuple(map(Tag, tags))

    id: str
    """See the :paramref:`~_ReceivedMessage.id` parameter."""

    time: int
    """See the :paramref:`~_ReceivedMessage.time` parameter."""

    event: Annotated[Event, Event]
    """See the :paramref:`~_ReceivedMessage.event` parameter."""

    topic: str
    """See the :paramref:`~_ReceivedMessage.topic` parameter."""

    message: Union[str, None] = None
    """See the :paramref:`~_ReceivedMessage.message` parameter."""

    expires: Union[int, None] = None
    """See the :paramref:`~_ReceivedMessage.expires` parameter."""

    title: Union[str, None] = None
    """See the :paramref:`~_ReceivedMessage.title` parameter."""

    tags: Annotated[Union[tuple[Tag, ...], None], _parse_tags] = None
    """See the :paramref:`~_ReceivedMessage.tags` parameter."""

    priority: Annotated[Union[Priority, None], Priority] = None
    """See the :paramref:`~_ReceivedMessage.priority` parameter."""

    click: Union[str, None] = None
    """See the :paramref:`~_ReceivedMessage.click` parameter."""

    actions: Annotated[
        Union[tuple[ReceivedAction, ...], None], _parse_actions
    ] = None
    """See the :paramref:`~_ReceivedMessage.actions` parameter."""

    attachment: Annotated[
        Union[ReceivedAttachment, None], _ReceivedAttachment.from_json
    ] = None
    """See the :paramref:`~_ReceivedMessage.attachment` parameter."""

    icon: Union[str, None] = None
    """See the :paramref:`~_ReceivedMessage.icon` parameter."""

    content_type: Union[str, None] = None
    """See the :paramref:`~_ReceivedMessage.content_type` parameter."""
