"""The `NtfyPublisher` class used for handling the publication of
messages.

:copyright: (c) 2024 Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.

"""

__author__ = "Tanner Corcoran"
__license__ = "Apache 2.0 License"
__copyright__ = "Copyright (c) 2024 Tanner Corcoran"


import sys
import base64
import dataclasses
import urllib.parse
from typing import (
    Any,
    ClassVar,
    Union,
)
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
from types import MappingProxyType

import httpx

from .message import Message


@dataclasses.dataclass(eq=False, frozen=True)
class _NtfyURL:
    scheme: str
    netloc: str
    path: str
    params: str
    query: str
    fragment: str

    @classmethod
    def parse(cls, url: str, topic: Union[str, None] = None) -> Self:
        s, n, p, r, q, f = urllib.parse.urlparse(url)
        p = p.rstrip("/")
        if topic:
            topic = topic.rstrip("/")
            p += f"/{topic}"
        return cls(*urllib.parse.urlparse(url))

    def _unparse(self, path: str) -> str:
        return urllib.parse.urlunparse((
            self.scheme,
            self.netloc,
            path,
            self.params,
            self.query,
            self.fragment,
        ))

    def unparse(self) -> str:
        return self._unparse(self.path)

    def unparse_with_topic(self, topic: str) -> str:
        return self._unparse(self.path + "/" + topic.lstrip("/"))


@dataclasses.dataclass(eq=False, frozen=True)
class NtfyPublisher:
    """The class that handles publishing message instances (or JSON).

    Args:
        url: The URL of a ntfy server.
        topic: The topic (if you wish to hard-code it into the URL).
        basic: Basic authentication. If defined, it may be either a
            base64-encoded username and password, or a tuple containing
            the username and password.
        bearer: Token authentication. If both `bearer` and `basic` are
            defined, `bearer` is used.

    """
    url: str
    topic: Union[str, None] = None
    basic: Union[str, tuple[str, str], None] = None
    bearer: Union[str, None] = None
    _url: ClassVar[_NtfyURL]
    _auth_header: ClassVar[MappingProxyType[str, str]]
    _client: ClassVar[httpx.Client]

    def __post_init__(self) -> None:
        # url
        object.__setattr__(self, "_url", _NtfyURL.parse(self.url, self.topic))

        # handle auth
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

        # client
        object.__setattr__(self, "_client", httpx.Client())

    def publish(self, msg: Message) -> httpx.Response:
        """Publish a message using headers"""
        topic, headers, data = msg.get_args()
        url = (
            self._url.unparse_with_topic(topic)
            if topic else self._url.unparse()
        )
        return self._client.post(
            url=url,
            content=data,
            headers={**self._auth_header, **headers}
        )

    __lshift__ = publish

    def publish_json(self, raw: dict[str, Any]) -> httpx.Response:
        """Publish a message using JSON"""
        return self._client.post(
            url=self._url.unparse(),
            json=raw,
            headers=self._auth_header
        )

    def close(self) -> None:
        """Close the `httpx.Client` instance"""
        if not self._client.is_closed:
            self._client.close()
