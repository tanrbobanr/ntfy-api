"""The :class:`NtfySubscription` class used for handling subscriptions.

:copyright: (c) 2024 Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.

"""

import dataclasses
import json
import logging
import sys
import threading
from types import MappingProxyType, TracebackType
from typing import Literal, Union

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

from websockets import exceptions as ws_exc
from websockets.sync import client as ws_client

from .__version__ import *  # noqa: F401,F403
from ._internals import URL, ClearableQueue, StrTuple
from .creds import Credentials
from .filter import Filter
from .message import ReceivedMessage, _ReceivedMessage

__all__ = ("NtfySubscription",)
logger = logging.Logger(__name__)


@dataclasses.dataclass(eq=False, frozen=True)
class NtfySubscription:
    """The class that handles subscriptions.

    :param base_url: The base URL of a ntfy server.
    :param topics: The topics to subscribe to.
    :param credentials: The user credentials, if any.
    :param filter: Optional response filters.
    :param max_queue_size: The maximum size of the message queue. If
        ``<=0``, the queue is unbounded. If the queue is filled, all new
        messages are discarded. Only when the queue has room for
        another message, will messages start being added again. This
        means that, if bounded, some messages may be dropped if the
        frequency of received messages is greater than your
        program's ability to handle those messages.

    """

    base_url: str
    """See the :paramref:`~NtfySubscription.base_url` parameter."""

    topics: StrTuple
    """See the :paramref:`~NtfySubscription.topics` parameter."""

    credentials: Union[Credentials, None] = None
    """See the :paramref:`~NtfySubscription.credentials` parameter."""

    filter: Union[Filter, None] = None
    """See the :paramref:`~NtfySubscription.filter` parameter."""

    max_queue_size: int = 0
    """See the :paramref:`~NtfySubscription.max_queue_size` parameter.

    """

    messages: ClearableQueue[ReceivedMessage] = dataclasses.field(init=False)
    """The message queue.

    This attribute stores received messages. See :class:`queue.Queue`
    for details on how to interact with this attribute.

    """

    _url: URL = dataclasses.field(init=False)
    _auth_header: MappingProxyType[str, str] = dataclasses.field(init=False)
    _ws_conn: Union[ws_client.ClientConnection, None] = dataclasses.field(
        default=None, init=False
    )
    _thread: Union[threading.Thread, None] = dataclasses.field(
        default=None, init=False
    )

    def __post_init__(self) -> None:
        """Create message queue, and set URL and credentials."""
        # message queue
        object.__setattr__(
            self, "messages", ClearableQueue(self.max_queue_size)
        )

        # url
        object.__setattr__(self, "_url", URL.parse(self.base_url))

        # credentials
        object.__setattr__(
            self,
            "_auth_header",
            (self.credentials or Credentials()).get_header(),
        )

    def __enter__(self) -> Self:
        """Enter the context manager protocol.

        :returns: The `NtfySubscription` instance.
        :rtype: NtfySubscription

        """
        if not self._ws_conn:
            self.connect()
        return self

    def __exit__(
        self,
        exc_type: Union[type[BaseException], None],
        exc_val: Union[BaseException, None],
        exc_tb: Union[TracebackType, None],
    ) -> Literal[False]:
        """Exit the context manager protocol.

        This ensures the client is closed.

        :returns: Always :py:obj:`False`. See :meth:`object.__exit__`
            for more information on what this return value means.
        :rtype: typing.Literal[False]

        """
        self.close()
        return False

    def connect(
        self, connection: Union[ws_client.ClientConnection, None] = None
    ) -> Self:
        """Initiate the websocket connection.

        .. note::
            This also clears :attr:`~NtfySubscription.messages`.

        :param connection: The websocket connection to use. If not
            provided, one will be created.
        :type connection: websockets.sync.client.ClientConnection |
            None, optional

        :returns: This :class:`NtfySubscription` instance.
        :rtype: NtfySubscription

        """
        object.__setattr__(
            self,
            "_ws_conn",
            connection
            or ws_client.connect(
                uri=self._url.unparse(
                    endpoint=(",".join(self.topics), "ws"),
                    scheme=("ws", "wss"),
                ),
                additional_headers={
                    **self._auth_header,
                    **(self.filter.serialize() if self.filter else {}),
                },
            ),
        )
        self.messages.clear()
        object.__setattr__(
            self, "_thread", threading.Thread(target=self._thread_fn)
        )
        if self._thread:
            self._thread.start()

        # this if/else is mostly here for type safety, as self._thread
        # can be None, hence the pragma below
        else:  # pragma: no cover
            raise ValueError(
                "Attempted to start consumer thread, but the thread was not"
                " successfully created"
            )

        return self

    def _thread_fn(self) -> None:
        while True:
            if self._ws_conn is None:
                return
            try:
                raw = self._ws_conn.recv()
                data = json.loads(raw)
                self.messages.put(
                    _ReceivedMessage.from_json(data), block=False
                )
                print(self.messages)
            except json.JSONDecodeError as e:
                logger.warning(
                    f"Failed to process JSON input ('{e}'): {raw!r}"
                )
                continue
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(
                    "Failed to instantiated _ReceivedMessage instance"
                    f" ('{e}'): {raw!r}"
                )
                continue
            except ws_exc.ConnectionClosed:
                return

    def close(self) -> None:
        """Close the websocket connection, if it exists."""
        if self._ws_conn:  # pragma: no branch
            self._ws_conn.close()
            object.__setattr__(self, "_ws_conn", None)
        if self._thread and self._thread.is_alive():  # pragma: no branch
            self._thread.join()
