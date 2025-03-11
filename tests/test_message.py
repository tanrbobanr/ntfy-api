import pytest

from src.ntfy_api.actions import ViewAction
from src.ntfy_api.enums import Priority, Tag
from src.ntfy_api.message import Message


def test_message_all() -> None:
    assert Message(
        topic="T",
        message="m\n\t'\"",
        title="t",
        priority=Priority.urgent,
        tags=(Tag.a, Tag.ab),
        markdown=True,
        delay="10m",
        templating=None,
        actions=[
            ViewAction(label="a", url="https://a", clear=True),
            ViewAction(label="b", url="https://b", clear=True),
        ],
        click="https://www.example.com",
        attachment="https://www.example.com/_static/example.png",
        filename="example.png",
        icon="https://www.example.com/_static/example.png",
        email="user@example.com",
        call="+11234567890",
        cache=True,
        firebase=False,
        unified_push=False,
        data={"example": "data"},
    ).get_args() == (
        "T",
        {
            "X-Message": "m\\n\t'\"",
            "X-Title": "t",
            "X-Priority": "5",
            "X-Tags": "a,ab",
            "X-Markdown": "1",
            "X-Delay": "10m",
            "X-Actions": (
                "view,a,https://a,clear=true;view,b,https://b,clear=true"
            ),
            "X-Click": "https://www.example.com",
            "X-Attach": "https://www.example.com/_static/example.png",
            "X-Filename": "example.png",
            "X-Icon": "https://www.example.com/_static/example.png",
            "X-Email": "user@example.com",
            "X-Call": "+11234567890",
            "X-Cache": "1",
            "X-Firebase": "0",
            "X-UnifiedPush": "0",
        },
        {"data": {"example": "data"}},
    )


def test_message_empty() -> None:
    assert Message().get_args() == (None, {}, {})


def test_message_templating() -> None:
    # if templating=True, data type should be "json"
    assert Message(templating=True, data={"example": "data"}).get_args() == (
        None,
        {"X-Template": "1"},
        {"json": {"example": "data"}},
    )


def test_mutual_exclusivity() -> None:
    with pytest.raises(ValueError):
        Message(filename="f", templating=True)


def test_unknown_type() -> None:
    with pytest.raises(TypeError):
        Message(topic=b"").serialize()


def test_single_tag() -> None:
    assert Message(tags=Tag.a).serialize() == {"X-Tags": "a"}
