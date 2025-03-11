import json
import os
import unittest.mock

from src.ntfy_api.client import NtfyClient
from src.ntfy_api.creds import Credentials
from src.ntfy_api.message import _ReceivedMessage

from . import mocks


def _read(filename: str) -> bytes:
    with open(f"tests/responses/{filename}", "rb") as infile:
        return infile.read()


RECEIVED_EXAMPLES_RAW = tuple(
    _read(f)
    for f in next(os.walk("tests/responses"))[2]
    if f.startswith("received")
)
RECEIVED_EXAMPLES_PARSED = tuple(
    _ReceivedMessage.from_json(json.loads(e))
    for e in RECEIVED_EXAMPLES_RAW
    if e
)


def _client() -> NtfyClient:
    return NtfyClient(
        base_url="https://www.example.com",
        default_topic="default_topic",
        credentials=Credentials(basic=("user", "pass")),
    )


def test_connect() -> None:
    client = _client()
    sub = client.subscribe()
    ic = mocks.InstanceCache(mocks.websockets.ClientConnection, _stall=True)
    with (
        unittest.mock.patch("src.ntfy_api.subscription.ws_client.connect", ic),
        unittest.mock.patch(
            "src.ntfy_api.subscription.ws_exc.ConnectionClosed",
            mocks.websockets.ConnectionClosed,
        ),
    ):
        sub.connect()
        assert sub._ws_conn is ic.instance
        assert ic.instance.uri == "wss://www.example.com/default_topic/ws"
        assert ic.instance.additional_headers == {
            "Authorization": "Basic dXNlcjpwYXNz",
        }
        assert sub._thread is not None
        assert sub._thread.is_alive()
        ic.instance.close()
        sub._thread.join()


def test_connect_multiple_topics() -> None:
    client = _client()
    sub = client.subscribe(topics=("a", "b"))
    ic = mocks.InstanceCache(mocks.websockets.ClientConnection, _stall=True)
    with (
        unittest.mock.patch("src.ntfy_api.subscription.ws_client.connect", ic),
        unittest.mock.patch(
            "src.ntfy_api.subscription.ws_exc.ConnectionClosed",
            mocks.websockets.ConnectionClosed,
        ),
    ):
        sub.connect()
        assert ic.instance.uri == "wss://www.example.com/a,b/ws"
        ic.instance.close()
        sub._thread.join()


def test_connect_custom_client() -> None:
    client = _client()
    sub = client.subscribe()
    wsc = mocks.websockets.ClientConnection(
        uri="uri", additional_headers={}, _stall=True
    )
    with unittest.mock.patch(
        "src.ntfy_api.subscription.ws_exc.ConnectionClosed",
        mocks.websockets.ConnectionClosed,
    ):
        sub.connect(wsc)
        assert sub._ws_conn is wsc
        assert sub._thread is not None
        assert sub._thread.is_alive()
        wsc.close()
        sub._thread.join()


def test_close() -> None:
    client = _client()
    sub = client.subscribe()
    wsc = mocks.websockets.ClientConnection(
        uri="uri", additional_headers={}, _stall=True
    )
    with unittest.mock.patch(
        "src.ntfy_api.subscription.ws_exc.ConnectionClosed",
        mocks.websockets.ConnectionClosed,
    ):
        sub.connect(wsc)
        sub.close()
        assert sub._ws_conn is None
        assert sub._thread is not None and not sub._thread.is_alive()


def test_recv() -> None:
    client = _client()
    sub = client.subscribe()
    wsc = mocks.websockets.ClientConnection(
        uri="uri",
        additional_headers={},
        _content=(_read("invalid.txt"), *RECEIVED_EXAMPLES_RAW),
        _stall_before_close=True,
    )
    received = list(RECEIVED_EXAMPLES_PARSED)
    with unittest.mock.patch(
        "src.ntfy_api.subscription.ws_exc.ConnectionClosed",
        mocks.websockets.ConnectionClosed,
    ):
        sub.connect(wsc)
        wsc._all_sent.wait()
        assert len(received) == len(sub.messages.queue)
        while not sub.messages.empty():
            value = sub.messages.get(timeout=0.1)
            assert value in received
            received.remove(value)
        sub.close()
    assert len(received) == 0


def test_context_manager() -> None:
    ic = mocks.InstanceCache(mocks.websockets.ClientConnection, _stall=True)
    client = _client()
    sub = client.subscribe()

    with (
        unittest.mock.patch("src.ntfy_api.subscription.ws_client.connect", ic),
        unittest.mock.patch(
            "src.ntfy_api.subscription.ws_exc.ConnectionClosed",
            mocks.websockets.ConnectionClosed,
        ),
    ):
        with sub as s:
            assert s is sub
            assert s._ws_conn is ic.instance
        assert sub._ws_conn is None
        assert ic.instance.is_closed


def test_context_manager_with_connect() -> None:
    client = _client()
    sub = client.subscribe()
    wsc = mocks.websockets.ClientConnection(
        uri="uri", additional_headers={}, _stall_before_close=True
    )

    with unittest.mock.patch(
        "src.ntfy_api.subscription.ws_exc.ConnectionClosed",
        mocks.websockets.ConnectionClosed,
    ):
        sub.connect(wsc)
        with sub as s:
            assert s is sub
            assert s._ws_conn is wsc
        assert sub._ws_conn is None
        assert wsc.is_closed


def test_no_connection() -> None:
    """Ensure thread function loop breaks if `._ws_conn` is not set."""
    client = _client()
    sub = client.subscribe()
    wsc = mocks.websockets.ClientConnection(
        uri="uri",
        additional_headers={},
        _content=RECEIVED_EXAMPLES_RAW,
        _stall=True,
    )

    with unittest.mock.patch(
        "src.ntfy_api.subscription.ws_exc.ConnectionClosed",
        mocks.websockets.ConnectionClosed,
    ):
        sub.connect(wsc)
        object.__setattr__(sub, "_ws_conn", None)
        wsc.unstall()
        sub._thread.join(0.5)
        assert not sub._thread.is_alive()
        assert len(sub.messages.queue) == 1
