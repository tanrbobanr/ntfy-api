"""The `NtfyClient` class used for handling interactions with the ntfy
API.

:copyright: (c) 2024 Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.

"""

import dataclasses
import json
import sys
from collections.abc import Generator, Iterable
from types import MappingProxyType, TracebackType
from typing import Literal, Union

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

import httpx

from .__version__ import *  # noqa: F401,F403
from ._internals import URL, StrTuple
from .creds import Credentials
from .errors import APIError
from .filter import Filter
from .message import Message, ReceivedMessage, _ReceivedMessage
from .subscription import NtfySubscription

__all__ = ("NtfyClient",)


@dataclasses.dataclass(eq=False, frozen=True)
class NtfyClient:
    """The class that handles publishing :class:`.Message` instances and
    creation of :class:`.NtfySubscription` instances.

    :param base_url: The base URL of a ntfy server.
    :type base_url: str
    :param default_topic: If provided, it will be used as a fallback
        topic in cases where no topic is provided in the
        :class:`.Message` instance being published, or as an argument
        (:paramref:`.publish.topic`) to the :attr:`.publish` method.
    :type default_topic: str, optional
    :param credentials: The user credentials, if any.
    :type credentials: Credentials, optional

    """

    base_url: str
    """See the :paramref:`~NtfyClient.base_url` parameter."""

    default_topic: Union[str, None] = None
    """See the :paramref:`~NtfyClient.default_topic` parameter."""

    credentials: Union[Credentials, None] = None
    """See the :paramref:`~NtfyClient.credentials` parameter."""

    _url: URL = dataclasses.field(init=False)
    _auth_header: MappingProxyType[str, str] = dataclasses.field(init=False)
    _http_client: Union[httpx.Client, None] = dataclasses.field(
        default=None, init=False
    )

    def __post_init__(self) -> None:
        """Initialize the :class:`URL` instance, and set the
        authentication headers.

        """
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

        :return: This :class:`NtfyClient` instance.
        :rtype: NtfyClient

        """
        if not self._http_client:
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

    def connect(self, client: Union[httpx.Client, None] = None) -> Self:
        """Start a new connection pool.

        :param client: If defined, uses the provided client. Otherwise,
            a new one is created.
        :type client: httpx.Client | None, optional

        :return: This :class:`NtfyClient` instance.
        :rtype: NtfyClient

        """
        object.__setattr__(self, "_http_client", client or httpx.Client())
        return self

    def close(self) -> None:
        """Close the HTTP connection pool, if it exists."""
        if self._http_client and not self._http_client.is_closed:
            self._http_client.close()
        object.__setattr__(self, "_http_client", None)

    def publish(
        self,
        msg: Message,
        topic: Union[str, None] = None,
        topic_override: bool = False,
    ) -> httpx.Response:
        """Publish a :class:`.Message` instance.

        .. note::
            If no connection pool exists (i.e. :meth:`.connect` wasn't
            called and this client is not being used as a context
            manager), a single-use connection will be used.

        :param msg: The :class:`.Message` instance containing the
            content to publish.
        :type msg: Message
        :param topic: A topic that will be used if no
            topic was provided in the given Message object.
        :type topic: str | None, optional
        :param topic_override: A flag that, if set to ``True``, will
            cause the given :paramref:`topic` (if provided) to be used
            regardless of whether or not a topic is present in the given
            :class:`.Message` instance.
        :type topic_override: bool, optional

        :return: The httpx.Response instance.
        :rtype: httpx.Response

        :raises ValueError: If no topic was provided as an argument, no
            topic was found in the provided :class:`.Message` instance,
            and no :attr:`~NtfyClient.default_topic` was given when
            creating this :class:`NtfyClient` instance.

        """
        msg_topic, headers, kwargs = msg.get_args()
        if msg_topic:
            if topic and topic_override:
                msg_topic = topic
        else:
            if topic:
                msg_topic = topic
            else:
                if not self.default_topic:
                    raise ValueError("No topic could be resolved")
                msg_topic = self.default_topic

        resp = (self._http_client.post if self._http_client else httpx.post)(
            url=self._url.unparse(endpoint=msg_topic),
            headers={**self._auth_header, **headers},
            **kwargs,
        )
        if resp.status_code != 200:
            raise APIError(resp, False)
        return resp

    def poll(
        self,
        topic: Union[str, None] = None,
        filter: Union[Filter, None] = None,
    ) -> Generator[ReceivedMessage, None, None]:
        """Poll for messages using an HTTP connection.

        .. note::
            If no connection pool exists (i.e. :meth:`.connect` wasn't
            called and this client is not being used as a context
            manager), a single-use connection will be used.

        :param topic: The topic to poll. If not provide, this instance's
            default topic will be used.
        :type topic: str, optional
        :param filter: An optional :class:`.Filter` instance used to
            filter responses.
        :type filter: Filter, optional

        :return: A generator of
            :class:`~ntfy_api.message.ReceivedMessage` instances.
        :rtype: typing.Iterator[ReceivedMessage]

        :raises ValueError: If no topic was provided as an argument, and
            no :attr:`~NtfyClient.default_topic` was given when creating
            this :class:`NtfyClient` instance.

        """
        if not topic:
            if not self.default_topic:
                raise ValueError("No topic could be resolved")
            topic = self.default_topic

        with (self._http_client.stream if self._http_client else httpx.stream)(
            method="GET",
            url=self._url.unparse(
                endpoint=(
                    topic,
                    "json",
                )
            ),
            headers={
                "X-Poll": "1",
                **self._auth_header,
                **(filter.serialize() if filter else {}),
            },
        ) as response:
            if response.status_code != 200:
                raise APIError(response, True)
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    yield _ReceivedMessage.from_json(data)

    def subscribe(
        self,
        topics: Union[str, Iterable[str], None] = None,
        filter: Union[Filter, None] = None,
        max_queue_size: int = 0,
    ) -> NtfySubscription:
        """A factory for :class:`.NtfySubscription` instances, which uses
        the same base URL and credentials as this :class:`NtfyClient`
        instance.

        .. note::
            The :class:`.NtfySubscription` instance is created but the
            connection is not yet started. Use its
            :meth:`.NtfySubscription.connect` method or the context
            manager protocol to start receiving messages.

        :param topics: Zero or more topics to subscribe to. If none are
            given, this instance's default topic will be used.
        :type topics: str | typing.Iterable[str] | None
        :param filter: An optional :class:`.Filter`
            instance used to filter responses.
        :type filter: Filter | None
        :param max_queue_size: The maximum size of the message queue. If
            `<=0`, the queue is unbounded. If the queue is filled,
            all new messages are discarded. Only when the queue has
            room for another message, will messages start being
            added again. This means that, if bounded, some messages
            may be dropped if the frequency of received messages is
            greater than your program's ability to handle those
            messages. Defaults to ``0``.
        :type max_queue_size: int, optional

        :return: The created :class:`.NtfySubscription`
            instance.
        :rtype: NtfySubscription

        :raises ValueError: If both the :paramref:`.subscribe.topics`
            argument and this instance's
            :attr:`~NtfyClient.default_topic` are :py:obj:`None`.

        """
        _topics: StrTuple
        if topics is None:
            if self.default_topic is None:
                raise ValueError(
                    "the 'topics' argument must be provided if the NtfyClient"
                    " instance's 'default_topic' is also not defined"
                )
            _topics = (self.default_topic,)
        else:
            _topics = (topics,) if isinstance(topics, str) else tuple(topics)

        return NtfySubscription(
            base_url=self.base_url,
            topics=_topics,
            credentials=self.credentials,
            filter=filter,
            max_queue_size=max_queue_size,
        )
