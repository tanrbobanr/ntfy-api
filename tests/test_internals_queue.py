import pytest

from src.ntfy_api._internals import ClearableQueue


def test_clear_unfinished_tasks() -> None:
    # create and fill
    q = ClearableQueue()
    q.put("a")
    q.put("b")

    # pull one out but do not finish task
    assert q.get() == "a"
    assert q.unfinished_tasks == 2
    assert q.qsize() == 1

    # test clear()
    q.clear()
    assert q.unfinished_tasks == 1
    assert q.qsize() == 0
    assert len(q.queue) == 0
    assert q.all_tasks_done


def test_clear_unfinished_tasks_branch() -> None:
    """Tests the branch that notifies the `all_tasks_done` condition"""
    # create and fill
    q = ClearableQueue()
    q.put("a")
    q.put("b")

    # pull one out but do not finish task
    assert q.get() == "a"
    q.task_done()
    assert q.unfinished_tasks == 1
    assert q.qsize() == 1

    # test clear()
    q.clear()
    assert q.unfinished_tasks == 0
    assert q.qsize() == 0
    assert len(q.queue) == 0
    assert q.all_tasks_done


def test_clear_negative_unfinished_tasks() -> None:
    q = ClearableQueue()
    q.unfinished_tasks = -1
    with pytest.raises(ValueError):
        q.clear()
