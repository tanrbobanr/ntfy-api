import dataclasses
import threading
from collections.abc import Iterable, Iterator, Mapping
from typing import Union


class ConnectionClosed(Exception):
    pass


@dataclasses.dataclass
class ClientConnection:
    uri: str
    additional_headers: Mapping[str, str]
    _content: Union[Iterable[Union[str, bytes]], None] = None
    _stall: bool = False
    _stall_before_close: bool = False
    _content_iter: Iterator[Union[str, bytes, None]] = dataclasses.field(
        init=False
    )
    _available: threading.Event = dataclasses.field(init=False)
    _all_sent: threading.Event = dataclasses.field(init=False)
    _is_closed: bool = dataclasses.field(default=False, init=False)

    def __post_init__(self) -> None:
        self._content_iter = iter((*(self._content or tuple()), None))
        self._all_sent = threading.Event()
        self._available = threading.Event()
        if not self._stall:
            self._available.set()

    @property
    def is_closed(self) -> bool:
        return self._is_closed

    def recv(self) -> Union[str, bytes]:
        self._available.wait()
        value = next(self._content_iter)
        if value is None:
            self._all_sent.set()
            if self._stall_before_close:
                self._available.clear()
                self._available.wait()
            raise ConnectionClosed()
        return value

    def unstall(self) -> None:
        self._available.set()

    def close(self) -> None:
        self._is_closed = True
        self._available.set()
