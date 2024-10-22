"""Action definitions.

:copyright: (c) 2024 Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.

"""

__author__ = "Tanner Corcoran"
__license__ = "Apache 2.0 License"
__copyright__ = "Copyright (c) 2024 Tanner Corcoran"


import sys
import dataclasses
from typing import (
    Annotated,
    Any,
    Union,
    get_args,
    get_origin,
)
from collections.abc import (
    Generator,
    Mapping,
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


@dataclass_transform(eq_default=False, frozen_default=True)
class _Action:
    """Action base class that is used to handle formatting"""
    _action: str
    _context: MappingProxyType[str, bool]

    def __init_subclass__(cls, action: str) -> None:
        """Handle subclass arguments, initialize dataclass, and build
        the serialization context.

        """
        cls._action = action
        cls._context = MappingProxyType({
            k:cls._get_context(a)
            for k, a in cls.__annotations__.items()
        })
        dataclasses.dataclass(eq=False, frozen=True)(cls)

    @classmethod
    def _get_context(cls, annotation: type) -> bool:
        """Get the context information from the given type annotation"""
        origin = get_origin(annotation)
        assign: bool = True

        if origin != Annotated:
            return assign

        args = get_args(annotation)

        if len(args) == 2:
            assign = args[1]
        
        return assign

    @classmethod
    def _default_serializer(cls, key: Union[str, None], value: Any) -> str:
        """Serializer used to serialize values. Does the following:
        - Escapes backslashes (`\\`) and double quotes (`"`) in strings
        - Encloses strings in double quotes if needed
        - Formats booleans as strings
        - Formats mappings as `<key>.k=v,...` (e.g. `extras.x=y`)

        """
        if isinstance(value, str):
            for k in ("\\", "\""):
                value = value.replace(k, f"\\{k}")
            if set(value).intersection({",", ";", "=", "'", "\"", "\\"}):
                return f"\"{value}\""
            return value

        if isinstance(value, bool):
            return ("false", "true")[value]
        
        if key and isinstance(value, Mapping):
            return ",".join(
                f"{key}.{k}={cls._default_serializer(None, v)}"
                for k, v in value.items()
            )

        raise TypeError(f"Unknown type: {value.__class__.__name__!r}")

    def _serialize(self) -> Generator[str, None, None]:
        """Generate segments that will later be joined in `~.serialize`.

        """
        yield self._action

        for k, v in self.__dict__.items():
            if v is _Unset:
                continue

            assign = self._context[k]
            value = self._default_serializer(k, v)

            if not assign:
                yield value
                continue

            yield f"{k}={value}"

    def serialize(self) -> str:
        """Serialize this action into a single header value"""
        return ",".join(self._serialize())


class ViewAction(_Action, action="view"):
    """
    Args:
        label: The action label.
        url: The URL to open when the action is activated.
        clear: Whether or not to clear the notification after the action
            is activated.

    """
    label: Annotated[str, False]
    url: Annotated[str, False]
    clear: Union[bool, _UnsetType] = _Unset


class BroadcastAction(_Action, action="broadcast"):
    """
    Args:
        label: The action label.
        intent: The Android intent name.
        extras: The Android intent extras.
        clear: Whether or not to clear the notification after the action
            is activated.

    """
    label: Annotated[str, False]
    intent: Union[str, _UnsetType] = _Unset
    extras: Annotated[Union[Mapping[str, str], _UnsetType], False] = _Unset
    clear: Union[bool, _UnsetType] = _Unset


class HTTPAction(_Action, action="http"):
    """
    Args:
        label: The action label.
        url: The URL to send the HTTP request to.
        method: The HTTP method.
        headers: The HTTP headers.
        body: The HTTP body.
        clear: Whether or not to clear the notification after the action
            is activated.

    """
    label: Annotated[str, False]
    url: Annotated[str, False]
    method: Union[str, _UnsetType] = _Unset
    headers: Annotated[Union[Mapping[str, str], _UnsetType], False] = _Unset
    body: Union[str, _UnsetType] = _Unset
    clear: Union[bool, _UnsetType] = _Unset
