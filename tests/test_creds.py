from types import MappingProxyType

import pytest

from src.ntfy_api.creds import Credentials


def test_none() -> None:
    assert Credentials().get_header() == MappingProxyType({})


def test_basic_encoded() -> None:
    assert Credentials(
        basic="dXNlcm5hbWU6cGFzc3dvcmQ="
    ).get_header() == MappingProxyType(
        {"Authorization": "Basic dXNlcm5hbWU6cGFzc3dvcmQ="}
    )


def test_basic_unencoded() -> None:
    assert Credentials(
        basic=("username", "password")
    ).get_header() == MappingProxyType(
        {"Authorization": "Basic dXNlcm5hbWU6cGFzc3dvcmQ="}
    )


def test_basic_invalid() -> None:
    with pytest.raises(ValueError):
        Credentials(basic=123).get_header()


def test_bearer() -> None:
    assert Credentials(bearer="token").get_header() == MappingProxyType(
        {"Authorization": "Bearer token"}
    )


def test_priority() -> None:
    assert Credentials(
        basic=("username", "password"), bearer="token"
    ).get_header() == MappingProxyType({"Authorization": "Bearer token"})
