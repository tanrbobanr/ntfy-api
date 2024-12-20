"""The `NtfySubscriber` class used for handling subscriptions to
topics.

:copyright: (c) 2024 Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.

"""

__author__ = "Tanner Corcoran"
__license__ = "Apache 2.0 License"
__copyright__ = "Copyright (c) 2024 Tanner Corcoran"


import logging
import json
import base64
import dataclasses
from typing import (
    ClassVar,
    Generator,
    Union,
)
from types import MappingProxyType
from typing import Self

import httpx
from websockets.sync.client import connect as ws_connect

from .._internals import _Unset, _UnsetType
from .._url import NtfyURL
from .message import MessageData, _MessageData

logger = logging.getLogger(__name__)


@dataclasses.dataclass(eq=False, frozen=True)
class NtfySubscriber:
    """The class that handles topic subscriptions.

    Args:
        url: The URL of a ntfy server.
        topic: The topic to subscribe to (can be multiple, comma-separated).
        basic: Basic authentication. If defined, it may be either a
            base64-encoded username and password, or a tuple containing
            the username and password.
        bearer: Token authentication. If both `bearer` and `basic` are
            defined, `bearer` is used.
        since: Return cached messages since timestamp, duration or message ID.
        scheduled: Include scheduled/delayed messages in message list.
        message_filter: Only return messages that match this exact message string.
        title_filter: Only return messages that match this exact title string.
        id_filter: Only return messages that match this exact message ID.
        priority_filter: Only return messages that match any priority listed
            (comma-separated).
        tags_filter: Only return messages that match all listed tags
            (comma-separated).
    """
    url: str
    topic: str
    basic: Union[str, tuple[str, str], None] = None
    bearer: Union[str, None] = None
    since: Union[str, int, _UnsetType] = _Unset
    scheduled: Union[bool, _UnsetType] = _Unset
    message_filter: Union[str, _UnsetType] = _Unset
    title_filter: Union[str, _UnsetType] = _Unset
    id_filter: Union[str, _UnsetType] = _Unset
    priority_filter: Union[str, _UnsetType] = _Unset
    tags_filter: Union[str, _UnsetType] = _Unset
    _url: ClassVar[NtfyURL]
    _auth_header: ClassVar[MappingProxyType[str, str]]
    _client: ClassVar[httpx.Client]

    def __post_init__(self) -> None:
        # URL parsing
        object.__setattr__(self, "_url", NtfyURL.parse(self.url, self.topic))

        # Handle auth
        def _set_header(type: str, value: str) -> None:
            object.__setattr__(
                self,
                "_auth_header",
                MappingProxyType({"Authorization": f"{type} {value}"})
            )

        if self.bearer is not None:
            _set_header("Bearer", self.bearer)
        elif isinstance(self.basic, str):
            _set_header("Basic", self.basic)
        elif self.basic and len(self.basic) == 2:
            _set_header(
                "Basic",
                base64.b64encode(
                    ":".join(self.basic).encode("ascii")
                ).decode("ascii")
            )
        elif self.basic:
            raise ValueError("Invalid basic credentials")
        else:
            object.__setattr__(self, "_auth_header", MappingProxyType({}))

        # HTTP client
        object.__setattr__(self, "_client", None)

    def __enter__(self) -> Self:
        """Enter the context manager protocol.

        Returns:
            Self: The subscriber instance
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager protocol, ensuring the client is closed."""
        self.close()

    def _build_headers(self) -> dict[str, str]:
        """Build headers dictionary from instance attributes."""
        headers = dict(self._auth_header)

        # Add filter headers if set
        for attr, header in {
            "message_filter": "X-Message",
            "title_filter": "X-Title",
            "id_filter": "X-ID",
            "priority_filter": "X-Priority",
            "tags_filter": "X-Tags",
            "since": "X-Since",
            "scheduled": "X-Scheduled"
        }.items():
            value = getattr(self, attr)
            if value is not _Unset:
                if isinstance(value, bool):
                    headers[header] = "1" if value else "0"
                else:
                    headers[header] = str(value)

        return headers

    def _build_url(self, endpoint: str) -> str:
        """Build full URL with given endpoint.

        Args:
            endpoint: The API endpoint (e.g., 'json', 'ws')

        Returns:
            str: The complete URL
        """
        return self._url.unparse_with_endpoint(endpoint)

    def subscribe(self) -> Generator[MessageData, None, None]:
        """Subscribe to topic(s) using WebSocket connection.

        Yields:
            MessageData: Messages received from the server
        """
        url = self._build_url("ws")
        if not url.startswith(("ws://", "wss://")):
            url = url.replace("http://", "ws://").replace("https://", "wss://")

        logger.debug("Connecting to WebSocket at %s", url)

        with ws_connect(
            url,
            additional_headers=self._auth_header
        ) as websocket:
            while True:
                try:
                    data = json.loads(websocket.recv())
                    logger.debug("Received message: %s", data)
                    yield _MessageData.from_json(data)
                except json.JSONDecodeError as e:
                    logger.warning("Error decoding message: %s", e)
                    continue
                except (AttributeError, TypeError, ValueError) as e:
                    logger.warning("Error parsing message data: %s", e)
                    continue
                except Exception as e:
                    logger.error("Fatal error occurred: %s", e)
                    break

    def _ensure_client(self) -> None:
        """Ensure HTTP client is initialized."""
        if self._client is None or self._client.is_closed:
            object.__setattr__(self, "_client", httpx.Client())

    def poll(self) -> Generator[MessageData, None, None]:
        """Poll for messages using HTTP connection.

        Yields:
            MessageData: Messages received from the server
        """
        url = self._build_url("json")
        headers = self._build_headers()
        headers["X-Poll"] = "1"

        self._ensure_client()

        with self._client.stream("GET", url, headers=headers) as response:
            if response.status_code not in {200, 201, 202, 206}:
                logger.error("HTTP request failed with status code: %d", response.status_code)
                return

            logger.debug("Connected to %s with status code %d", url, response.status_code)

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        yield _MessageData.from_json(data)
                    except json.JSONDecodeError as e:
                        logger.warning("Error decoding message: %s", e)
                        continue
                    except (AttributeError, TypeError, ValueError) as e:
                        logger.warning("Error parsing message data: %s", e)
                        continue

    def close(self) -> None:
        """Close the httpx.Client instance"""
        if hasattr(self, '_client') and not self._client.is_closed:
            self._client.close()
