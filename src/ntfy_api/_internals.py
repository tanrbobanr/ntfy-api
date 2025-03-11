"""Internal utilities.

:copyright: (c) 2024 Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.

"""

import collections
import copy
import dataclasses
import queue
import sys
import urllib.parse
from collections.abc import Iterable, Mapping
from types import MappingProxyType
from typing import (
    Annotated,
    Any,
    Callable,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self, dataclass_transform
else:  # pragma: no cover
    from typing_extensions import Self, dataclass_transform
if sys.version_info >= (3, 10):  # pragma: no cover
    from typing import TypeAlias
else:  # pragma: no cover
    from typing_extensions import TypeAlias

from .__version__ import *  # noqa: F401,F403

_T = TypeVar("_T")
StrTuple: TypeAlias = Union[tuple[str], tuple[str, ...]]


_SECURE_URL_SCHEMES: set[str] = {
    "https",
    "wss",
    "sftp",
    "aaas",
    "msrps",
    "sips",
}


if sys.version_info >= (3, 10):  # pragma: no cover

    def _unwrap_static(wrapper: Callable[[Any], Any]) -> Callable[[Any], Any]:
        """Get the callable from the given wrapper."""
        return wrapper

else:  # pragma: no cover

    def _unwrap_static(wrapper: Callable[[Any], Any]) -> Callable[[Any], Any]:
        """Get the callable from the given wrapper."""
        return (
            wrapper.__func__ if isinstance(wrapper, staticmethod) else wrapper
        )


@dataclasses.dataclass(eq=False, frozen=True)
class URL:
    """Internal URL handling for ntfy API endpoints.

    :param scheme: The URL scheme (e.g., ``scheme`` in
        ``scheme://netloc/path;parameters?query#fragment``).
    :type scheme: str
    :param netloc: The URL netloc (e.g., ``netloc`` in
        ``scheme://netloc/path;parameters?query#fragment``).
    :type netloc: str
    :param path: The URL path (e.g., ``path`` in
        ``scheme://netloc/path;parameters?query#fragment``).
    :type path: str
    :param params: The URL params (e.g., ``params`` in
        ``scheme://netloc/path;parameters?query#fragment``).
    :type params: str
    :param query: The URL query (e.g., ``query`` in
        ``scheme://netloc/path;parameters?query#fragment``).
    :type query: str
    :param fragment: The URL fragment (e.g., ``fragment`` in
        ``scheme://netloc/path;parameters?query#fragment``).
    :type fragment: str

    """

    scheme: str
    """See the :paramref:`~URL.scheme` parameter."""

    netloc: str
    """See the :paramref:`~URL.netloc` parameter."""

    path: str
    """See the :paramref:`~URL.path` parameter."""

    params: str
    """See the :paramref:`~URL.params` parameter."""

    query: str
    """See the :paramref:`~URL.query` parameter."""

    fragment: str
    """See the :paramref:`~URL.fragment` parameter."""

    @classmethod
    def parse(cls, url: str) -> Self:
        """Parse a URL-like string into a new :class:`URL` instance.

        :param url: The URL-like string to parse.
        :type url: str

        :return: A new :class:`URL` instance.
        :rtype: URL

        """
        s, n, p, r, q, f = urllib.parse.urlparse(url)
        return cls(s, n, p.rstrip("/"), r, q, f)

    def _unparse(self, path: str, scheme: str) -> str:
        """Internal method to reconstruct URL with a given path and
        scheme.

        :param path: The path to use in place of :attr:`.path`.
        :type path: str
        :param scheme: The path to use in place of :attr:`.scheme`.
        :type scheme: str

        :return: The reconstructed URL.
        :rtype: str

        """
        return urllib.parse.urlunparse((
            scheme,
            self.netloc,
            path,
            self.params,
            self.query,
            self.fragment,
        ))

    def unparse(
        self,
        endpoint: Union[str, Iterable[str], None] = None,
        scheme: Union[tuple[str, str], None] = None,
    ) -> str:
        """Reconstruct the full URL string.

        :param endpoint: An endpoint to be appended to the path before
            parsing.
        :type endpoint: str | typing.Iterable[str] | None,
            optional
        :param scheme: A scheme two-tuple (insecure, secure) to be used
            instead of the existing scheme. Which version is used
            (insecure vs secure) will be decided based on the current
            scheme's security status.
        :type scheme: tuple[str, str] | None, optional

        :return: The constructed URL.
        :rtype: str

        """
        if endpoint:
            if isinstance(endpoint, str):
                endpoint = (endpoint,)
            e = "/".join(x.lstrip("/") for x in endpoint)
            _path = f"{self.path}/{e}"
        else:
            _path = self.path
        _scheme = (
            scheme[self.scheme in _SECURE_URL_SCHEMES]
            if scheme
            else self.scheme
        )

        return self._unparse(_path, _scheme)


class ClearableQueue(queue.Queue[_T]):
    """A :class:`queue.Queue` subclass that adds a single
    :meth:`.clear` method, which clears all remaining items in the
    queue.

    """

    queue: collections.deque[_T]

    def clear(self) -> None:
        """Clear all remaining items in the queue."""
        with self.mutex:
            unfinished = self.unfinished_tasks - len(self.queue)

            # finish unfinished tasks
            if unfinished <= 0:
                # would likely only happen if queue has been manually
                # tampered with
                if unfinished < 0:
                    raise ValueError("task_done() called too many times")

                # notify threads waiting on the all_tasks_done threading
                # condition
                self.all_tasks_done.notify_all()

            # updated unfinished tasks and clear queue
            self.unfinished_tasks = unfinished
            self.queue.clear()

            # notify threads waiting on the not_full threading condition
            self.not_full.notify_all()


@dataclass_transform()
class WrappingDataclass:
    """A special dataclass type that allows for its attributes to be
    annotated with wrapper types.

    """

    _context: MappingProxyType[str, Callable[[Any], Any]]

    def __init_subclass__(cls) -> None:
        """Build context and initialize dataclass."""
        cls._context = MappingProxyType({
            k: c
            for k, c in (
                (k, cls._get_context(v))
                for k, v in cls.__annotations__.items()
            )
            if c is not None
        })
        dataclasses.dataclass(cls)

    @classmethod
    def _get_context(
        cls, annotation: type
    ) -> Union[Callable[[Any], Any], None]:
        """Get the context information from the given type annotation.

        :param annotation: The annotation to get the context from.
        :type annotation: type

        :return: The context, if any.
        :rtype: typing.Callable[[typing.Any], typing.Any] | None

        """
        origin = get_origin(annotation)

        if origin is not Annotated:
            return None

        # typing.Annotated must have at least two arguments, so we know
        # that index 1 will not be out of range
        return get_args(annotation)[1]

    @classmethod
    def from_json(cls, data: Mapping[str, Any]) -> Self:
        """Parse a new :class:`.WrappingDataclass` instance from the
        given data.

        .. note:: :paramref:`.data` is not modified when wrappers (if
            any) are applied. Instead, a shallow copy of the mapping is
            created and used. Keep in mind that, because it is a shallow
            copy, the wrappers may still modify the mapping values
            in-place.

        :param data: The JSON-like data.
        :type data: typing.Mapping[str, typing.Any]

        :return: The parsed :class:`.WrappingDataclass` instance.
        :rtype: WrappingDataclass

        """
        _data = dict(copy.copy(data))
        for k, v in data.items():
            wrapper = cls._context.get(k)
            if not wrapper:
                continue
            _data[k] = _unwrap_static(wrapper)(v)

        return cls(**_data)
