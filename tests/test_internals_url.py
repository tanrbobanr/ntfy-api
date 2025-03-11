from src.ntfy_api._internals import URL


def test_parse() -> None:
    parsed = URL.parse("https://www.example.com/path;x=1?y=2")
    assert (
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment,
    ) == (
        "https",
        "www.example.com",
        "/path",
        "x=1",
        "y=2",
        "",
    )


def test_parse_with_trailing_slash() -> None:
    parsed = URL.parse("https://www.example.com/path/;x=1?y=2")
    assert (
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment,
    ) == (
        "https",
        "www.example.com",
        "/path",
        "x=1",
        "y=2",
        "",
    )


def test_unparse_internal() -> None:
    assert (
        URL(
            scheme="https",
            netloc="www.example.com",
            path="/path",
            params="x=1",
            query="y=2",
            fragment="",
        )._unparse("path2", "wss")
        == "wss://www.example.com/path2;x=1?y=2"
    )


def test_unparse() -> None:
    assert (
        URL.parse("https://www.example.com/path;x=1?y=2").unparse()
        == "https://www.example.com/path;x=1?y=2"
    )


def test_unparse_with_endpoint() -> None:
    assert (
        URL.parse("https://www.example.com/path;x=1?y=2").unparse(
            endpoint="endpoint"
        )
        == "https://www.example.com/path/endpoint;x=1?y=2"
    )


def test_unparse_with_endpoints() -> None:
    assert (
        URL.parse("https://www.example.com/path;x=1?y=2").unparse(
            endpoint=("e1", "e2")
        )
        == "https://www.example.com/path/e1/e2;x=1?y=2"
    )


def test_unparse_with_scheme() -> None:
    assert (
        URL.parse("https://www.example.com/path;x=1?y=2").unparse(
            scheme=("ws", "wss")
        )
        == "wss://www.example.com/path;x=1?y=2"
    )


def test_unparse_with_endpoint_and_scheme() -> None:
    assert (
        URL.parse("ftp://www.example.com/path;x=1?y=2").unparse(
            endpoint="endpoint", scheme=("ws", "wss")
        )
        == "ws://www.example.com/path/endpoint;x=1?y=2"
    )
