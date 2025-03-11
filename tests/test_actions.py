from collections.abc import Mapping
from typing import Annotated, Union

import pytest

from src.ntfy_api.actions import _Action


class _TestAction(_Action, action="testaction"):
    str_noassign: Annotated[str, False]
    bool_noassign: Annotated[str, False]
    mapping_noassign: Annotated[str, False]
    str_assign: str
    bool_assign: str
    # will not format values correctly, but the behavior is still known
    # and will be tested - mappings with assign=true should still never
    # be used
    mapping_assign: Mapping[str, str]
    unset_default: Union[Mapping[str, str], None] = None


class _TestAction2(_Action, action="testaction2"):
    value: str


def test_action() -> None:
    assert (
        _TestAction(
            str_noassign='\\"',
            bool_noassign=True,
            mapping_noassign={"a": "b", "c": "d"},
            str_assign='\\"',
            bool_assign=False,
            mapping_assign={"a": "b", "c": "d"},
        ).serialize()
        == 'testaction,"\\\\\\"",true,mapping_noassign.a=b'
        ',mapping_noassign.c=d,str_assign="\\\\\\"",bool_assign=false'
        ",mapping_assign=mapping_assign.a=b,mapping_assign.c=d"
    )


def test_unknown_type() -> None:
    with pytest.raises(TypeError):
        _TestAction2(b"").serialize()
