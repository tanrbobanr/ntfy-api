# _url.py
"""URL handling utilities for ntfy API.

:copyright: (c) 2024 Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.
"""

__author__ = "Tanner Corcoran"
__license__ = "Apache 2.0 License"
__copyright__ = "Copyright (c) 2024 Tanner Corcoran"

import sys
import dataclasses
import urllib.parse
from typing import Union

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


@dataclasses.dataclass(eq=False, frozen=True)
class NtfyURL:
    """Internal URL handling for ntfy API endpoints."""
    scheme: str
    netloc: str
    path: str
    params: str
    query: str
    fragment: str

    @classmethod
    def parse(cls, url: str, topic: Union[str, None] = None) -> Self:
        """Parse a URL and optionally append a topic.

        Args:
            url: The base URL to parse
            topic: Optional topic to append to the path

        Returns:
            NtfyURL: A new URL instance
        """
        s, n, p, r, q, f = urllib.parse.urlparse(url)
        p = p.rstrip("/")
        if topic:
            topic = topic.rstrip("/")
            p += f"/{topic}"
        return cls(s, n, p, r, q, f)

    def _unparse(self, path: str) -> str:
        """Internal method to reconstruct URL with a given path."""
        return urllib.parse.urlunparse((
            self.scheme,
            self.netloc,
            path,
            self.params,
            self.query,
            self.fragment,
        ))

    def unparse(self) -> str:
        """Reconstruct the full URL string.

        Returns:
            str: The complete URL
        """
        return self._unparse(self.path)

    def unparse_with_topic(self, topic: str) -> str:
        """Reconstruct the URL with an appended topic.

        Args:
            topic: The topic to append to the path

        Returns:
            str: The complete URL including the topic
        """
        return self._unparse(self.path + "/" + topic.lstrip("/"))

    def unparse_with_endpoint(self, endpoint: str) -> str:
        """Reconstruct the URL with an API endpoint appended.

        Args:
            endpoint: The API endpoint (e.g., 'json', 'ws', 'sse')

        Returns:
            str: The complete URL including the endpoint
        """
        return self._unparse(f"{self.path}/{endpoint.lstrip('/')}")
