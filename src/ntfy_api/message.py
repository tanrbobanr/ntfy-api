"""The `Message` class and its dependencies.

:copyright: (c) 2024 Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.

"""

__author__ = "Tanner Corcoran"
__license__ = "Apache 2.0 License"
__copyright__ = "Copyright (c) 2024 Tanner Corcoran"


import io
import sys
import json
import dataclasses
from typing import (
    Annotated,
    Any,
    Union,
    get_args,
)
from collections.abc import (
    Callable,
    Generator,
    Iterable,
    Sequence,
)
# not 3.11 because we need frozen_default
if sys.version_info >= (3, 12):
    from typing import dataclass_transform
else:
    from typing_extensions import dataclass_transform
from types import MappingProxyType
from ._internals import (
    _Unset,
    _UnsetType,
)
from .actions import _Action


@dataclass_transform(eq_default=False, frozen_default=True)
class _Message:
    """Message base class that is used to handle formatting"""
    _context: MappingProxyType[str, tuple[str, Callable[[Any], Any]]]

    def __init_subclass__(cls) -> None:
        """Handle dataclass initialization and build the serialization
        context.

        """
        cls._context = MappingProxyType({
            k:cls._get_context(a)
            for k, a in cls.__annotations__.items()
        })
        dataclasses.dataclass(eq=False, frozen=True)(cls)

    @classmethod
    def _get_context(
        cls, annotation: type
    ) -> tuple[str, Callable[[Any], Any]]:
        """Get the context information from the given type annotation"""
        args = get_args(annotation)
        serializer: Callable[[Any], Any] = cls._default_serializer

        if len(args) == 3:
            serializer = args[2]

        return (args[1], serializer)

    @classmethod
    def _default_serializer(cls, value: Any) -> str:
        """Default serializer that does the following:
        - Return the value if it is a string
        - Stringify integers
        - Format booleans as strings

        """
        if isinstance(value, str):
            for o, n in (("\n", "n"), ("\r", "r"), ("\f", "f")):
                value = value.replace(o, f"\\{n}")
            return value

        if isinstance(value, int):
            return str(value)

        if isinstance(value, bool):
            return ("false", "true")[value]

        raise TypeError(f"Unknown type: {value.__class__.__name__!r}")

    def _serialize(self) -> Generator[tuple[str, Any], None, None]:
        """Generate segments that will later be turned into a dictionary
        in `~.serialize`.

        """
        for k, v in self.__dict__.items():
            if v is _Unset:
                continue

            key, serializer = self._context[k]

            yield (key, serializer(v))

    def serialize(self) -> dict[str, Any]:
        """Serialize this message into a header dictionary"""
        return dict(self._serialize())


class Message(_Message):
    """
    Args:
        topic: The topic this message should be sent to.
        message: The message body.
        title: The message title.
        priority: The message priority.
        tags: A set of tags that will be displayed along with the
            message. If the tag is a supported emoji short code (i.e.
            those found in the `~Tag` enum), they will be displayed to
            the left of the title. Unrecognized tags will be displayed
            below the message.
        markdown: Whether or not to render the message with markdown.
        delay: When to schedule the message. This should be either a
            unix timestamp or a natural-language date/time or offset
            (see https://github.com/olebedev/when). Any value between 10
            seconds and 3 days may be used.
        templating: If `True`, `data` will be interpreted as JSON and
            used as the template context of Go-styled templates in the
            `message` and `title`. Mutually exclusive with `filename`.
        actions: Actions attached to this message.
        click: The redirect URL that will be activated when the
            notification is clicked.
        attach: An externally-hosted attachment to be included in the
            message.
        filename: The filename of the included attachment. If not
            provided, it will be derived from the URL resource
            identifier. Mutually exclusive with `templating`.
        icon: An externally-hosted icon that will be displayed next to
            the notification.
        email: The email address to forward this message to.
        call: The phone number to forward this message to.
        cache: Whether or not to make use of the message cache.
        firebase: Whether or not to enable Firebase.
        unified_push: Whether or not to enable UnifiedPush.
        data: If defined, it should be one of the following
            - If sending a local file as an attachment, the raw
                attachment data if uploading a local file. If doing so,
                it is recommended to use the `filename` option in
                addition to this.
            - If using templating, the template data.

    """
    def __post_init__(self) -> None:
        if self.templating is not _Unset and self.filename is not _Unset:
            raise ValueError(
                "The 'templating' and 'filename' options for 'Message' objects"
                " are mutually exclusive"
            )

    @staticmethod
    def _ignore(value: Any) -> Any:
        return value
    
    @staticmethod
    def _tags_serializer(value: Sequence[str]) -> str:
        return ",".join(value)

    @staticmethod
    def _actions_serializer(value: Iterable[_Action]) -> str:
        return ";".join(v.serialize() for v in value)

    @staticmethod
    def _yn_serializer(value: bool) -> str:
        return ("no", "yes")[value]

    topic: Annotated[Union[str, _UnsetType], "__topic__"] = _Unset
    message: Annotated[Union[str, _UnsetType], "X-Message"] = _Unset
    title: Annotated[Union[str, _UnsetType], "X-Title"] = _Unset
    priority: Annotated[Union[int, _UnsetType], "X-Priority"] = _Unset
    tags: Annotated[
        Union[Sequence[str], _UnsetType],
        "X-Tags",
        _tags_serializer
    ] = _Unset
    markdown: Annotated[Union[bool, _UnsetType], "X-Markdown"] = _Unset
    delay: Annotated[Union[int, str, _UnsetType], "X-Delay"] = _Unset
    templating: Annotated[
        Union[bool, _UnsetType],
        "X-Template",
        _yn_serializer
    ] = _Unset
    actions: Annotated[
        Union[Iterable[_Action], _UnsetType],
        "X-Actions",
        _actions_serializer
    ] = _Unset
    click: Annotated[Union[str, _UnsetType], "X-Click"] = _Unset
    attach: Annotated[Union[str, _UnsetType], "X-Attach"] = _Unset
    filename: Annotated[Union[str, _UnsetType], "X-Filename"] = _Unset
    icon: Annotated[Union[str, _UnsetType], "X-Icon"] = _Unset
    email: Annotated[Union[str, _UnsetType], "X-Email"] = _Unset
    call: Annotated[Union[str, _UnsetType], "X-Call"] = _Unset
    cache: Annotated[
        Union[bool, _UnsetType],
        "X-Cache",
        _yn_serializer
    ] = _Unset
    firebase: Annotated[
        Union[bool, _UnsetType],
        "X-Firebase",
        _yn_serializer
    ] = _Unset
    unified_push: Annotated[
        Union[bool, _UnsetType],
        "X-UnifiedPush",
        _yn_serializer
    ] = _Unset
    data: Annotated[
        Union[io.BufferedReader, dict[str, Any], _UnsetType],
        "__data__",
        _ignore
    ] = _Unset

    def get_args(
        self
    ) -> tuple[
        Union[str, None],
        dict[str, str],
        Union[io.BufferedReader, str, None]
    ]:
        """Get the topic, headers, and data (in that order)"""
        serialized = self.serialize()
        topic = serialized.pop("__topic__", None)
        data = serialized.pop("__data__", None)
        if data and self.templating is True:
            data = json.dumps(data, separators=(",",";"))
        return (topic, serialized, data)
