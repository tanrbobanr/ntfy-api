import dataclasses
import sys
from collections.abc import Iterable, Iterator, Mapping
from types import TracebackType
from typing import Any, Union

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
del sys


@dataclasses.dataclass
class Capture:
    url: str
    method: Union[str, None] = None
    headers: Union[Mapping[str, str], None] = None
    json: Union[Any, None] = None
    data: Union[Mapping[str, Any], None] = None
    content: Union[str, bytes, None] = None
    _response_: Union["Response", "StreamingResponse", None] = None


@dataclasses.dataclass
class Response:
    status_code: int
    standalone: bool
    capture: Capture
    client: "Client"
    content: Union[str, bytes, None]


@dataclasses.dataclass
class StreamingResponse:
    status_code: int
    standalone: bool
    capture: Capture
    client: "Client"
    content: Iterable[Union[str, bytes]]

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Union[type[BaseException], None],
        exc_val: Union[BaseException, None],
        exc_tb: Union[TracebackType, None],
    ) -> bool:
        return False

    def iter_lines(self) -> Iterator[Union[str, bytes]]:
        return iter(self.content)


class Client:
    def __init__(self, *, standalone: bool = False) -> None:
        self._standalone = standalone
        self._captures: list[Capture] = list()
        self._status_codes: dict[str, int] = dict()
        self._content: dict[
            str, Union[str, bytes, Iterable[Union[str, bytes]]]
        ] = dict()
        self._closed: bool = False

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Union[type[BaseException], None],
        exc_val: Union[BaseException, None],
        exc_tb: Union[TracebackType, None],
    ) -> bool:
        return False

    def close(self) -> None:
        self._closed = True

    @property
    def captures(self) -> tuple[Capture, ...]:
        return tuple(self._captures)

    @property
    def is_closed(self) -> bool:
        return self._closed

    def set_status(self, method: str, status_code: int) -> None:
        self._status_codes[method.strip().lower()] = status_code

    def set_content(
        self,
        method: str,
        content: Union[str, bytes, Iterable[Union[str, bytes]]],
    ) -> None:
        self._content[method.strip().lower()] = content

    def post(self, *args: Any, **kwargs: Any) -> Response:
        content = self._content.get("post")
        if content is not None and not isinstance(content, (str, bytes)):
            raise ValueError("Incorrect content type")
        cap = Capture(*args, **kwargs)
        resp = Response(
            status_code=self._status_codes.get("post", 200),
            standalone=self._standalone,
            capture=cap,
            client=self,
            content=content,
        )
        cap._response_ = resp
        self._captures.append(cap)
        return resp

    def stream(self, *args, **kwargs) -> StreamingResponse:
        content = self._content.get("stream")
        cap = Capture(*args, **kwargs)
        resp = StreamingResponse(
            status_code=self._status_codes.get("stream", 200),
            standalone=self._standalone,
            capture=cap,
            client=self,
            content=content,
        )
        cap._response_ = resp
        self._captures.append(cap)
        return resp


# with (self._http_client.stream if self._http_client else httpx.stream)(
#             method="GET",
#             url=self._url.unparse("json"),
#             headers={
#                 "X-Poll": "1",
#                 **self._auth_header,
#                 **(filter.serialize() if filter else {}),
#             }
#         ) as response:
#             for line in response.iter_lines():
#                 if line:
#                     data = json.loads(line)
#                     yield _ReceivedMessage.from_json(data)


def post(*args: Any, **kwargs: Any) -> Response:
    return Client(standalone=True).post(*args, **kwargs)
