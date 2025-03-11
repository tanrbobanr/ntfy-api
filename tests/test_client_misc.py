import unittest.mock

from src.ntfy_api.client import NtfyClient
from src.ntfy_api.creds import Credentials

from . import mocks


def _client() -> NtfyClient:
    return NtfyClient(
        base_url="https://www.example.com",
        default_topic="default_topic",
        credentials=Credentials(basic=("user", "pass")),
    )


@unittest.mock.patch("src.ntfy_api.client.httpx", mocks.httpx)
def test_connect() -> None:
    client = _client()
    assert client._http_client is None
    client.connect()
    assert isinstance(client._http_client, mocks.httpx.Client)


def test_connect_custom_client() -> None:
    m = mocks.httpx.Client()
    client = _client()
    client.connect(m)
    assert client._http_client is m


def test_close() -> None:
    m = mocks.httpx.Client()

    with unittest.mock.patch("src.ntfy_api.client.httpx.Client", lambda: m):
        client = _client()
        client.close()
        assert not m.is_closed
        client.connect()
        client.close()
        assert m.is_closed


def test_context_manager() -> None:
    ic = mocks.InstanceCache(mocks.httpx.Client)

    with unittest.mock.patch("src.ntfy_api.client.httpx.Client", ic):
        client = _client()
        with client as c:
            assert c is client
            assert client._http_client is ic.instance
        assert client._http_client is None
        assert ic.instance.is_closed


def test_context_manager_with_connect() -> None:
    """Make sure `connect()` is not called if `._http_client` is already
    set upon `__enter__`.

    """
    m = mocks.httpx.Client()
    client = _client()
    client.connect(m)
    with client as c:
        assert c is client
        assert client._http_client is m
    assert client._http_client is None
    assert m.is_closed
