import json
from typing import Union

import httpx

from .__version__ import *  # noqa: F401,F403

__all__ = ("APIError",)


class APIError(Exception):
    """An error received from the ntfy API.

    :param response: The :class:`httpx.Response` object that encountered
        the error.
    :type response: httpx.Response
    :param stream: Whether or not the response is streaming.
    :type stream: bool

    """

    def __init__(self, response: httpx.Response, stream: bool) -> None:
        try:
            data: dict[str, Union[str, int]] = json.loads(
                next(response.iter_lines()) if stream else response.content
            )
            msg = "; ".join(
                f"{k}={v!r}"
                for k, v in (
                    (k, data.get(k)) for k in ("http", "code", "error", "link")
                )
                if v is not None
            )
            super().__init__(f"Error interacting with the API ({msg})")
        except Exception:
            super().__init__(
                "Error interacting with the API (http:"
                f" {response.status_code})"
            )
