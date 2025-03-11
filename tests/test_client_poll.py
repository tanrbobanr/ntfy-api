import json
import os
import unittest.mock

import pytest

from src.ntfy_api.client import NtfyClient
from src.ntfy_api.creds import Credentials
from src.ntfy_api.errors import APIError
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


def test_poll_standalone() -> None:
    """General test"""
    m = mocks.httpx.Client(standalone=True)
    m.set_content("stream", RECEIVED_EXAMPLES_RAW)

    received = list(RECEIVED_EXAMPLES_PARSED)

    with unittest.mock.patch("src.ntfy_api.client.httpx.stream", m.stream):
        for msg in _client().poll():
            assert msg in received
            received.remove(msg)
    assert len(received) == 0
    capture = m.captures[0]
    assert capture._response_.status_code == 200
    assert capture._response_.standalone
    assert capture.url == "https://www.example.com/default_topic/json"
    assert capture.headers == {
        "X-Poll": "1",
        "Authorization": "Basic dXNlcjpwYXNz",
    }
    assert capture.json is None
    assert capture.data is None
    assert capture.content is None


def test_poll_standalone_error() -> None:
    """Ensure error is thrown if non-200 HTTP status code"""
    m = mocks.httpx.Client(standalone=True)
    m.set_status("stream", 400)
    m.set_content(
        "stream",
        (
            _read(
                "sent_error.txt",
            )
        ),
    )
    with unittest.mock.patch("src.ntfy_api.client.httpx.stream", m.stream):
        with pytest.raises(APIError):
            next(_client().poll())
    assert m.captures[0]._response_.status_code == 400


@unittest.mock.patch("src.ntfy_api.client.httpx", mocks.httpx)
def test_poll_standalone_no_topic() -> None:
    """Ensure error is thrown if no topic is found"""
    with pytest.raises(ValueError):
        # wrap it in tuple so that the first statements get called
        tuple(NtfyClient(base_url="https://www.example.com").poll())


def test_poll_standalone_custom_topic() -> None:
    """Ensure custom topic overrides default topic"""
    m = mocks.httpx.Client(standalone=True)
    m.set_content("stream", RECEIVED_EXAMPLES_RAW)

    with unittest.mock.patch("src.ntfy_api.client.httpx.stream", m.stream):
        next(_client().poll(topic="custom_topic"))

    capture = m.captures[0]
    assert capture.url == "https://www.example.com/custom_topic/json"
