import pytest
from executor import _topological_sort, _is_batch_result, _get_input_node_ids


def test_topological_sort_linear():
    nodes = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    edges = [
        {"source": "a", "target": "b"},
        {"source": "b", "target": "c"},
    ]
    out = _topological_sort(nodes, edges)
    assert [n["id"] for n in out] == ["a", "b", "c"]


def test_topological_sort_branch():
    nodes = [{"id": "src"}, {"id": "m1"}, {"id": "m2"}, {"id": "dst"}]
    edges = [
        {"source": "src", "target": "m1"},
        {"source": "src", "target": "m2"},
        {"source": "m1", "target": "dst"},
        {"source": "m2", "target": "dst"},
    ]
    out = _topological_sort(nodes, edges)
    ids = [n["id"] for n in out]
    assert ids[0] == "src"
    assert ids[-1] == "dst"
    assert set(ids[1:-1]) == {"m1", "m2"}


def test_topological_sort_loop_is_stuck():
    nodes = [{"id": "a"}, {"id": "b"}]
    edges = [
        {"source": "a", "target": "b"},
        {"source": "b", "target": "a"},
    ]
    out = _topological_sort(nodes, edges)
    assert len(out) == 0


def test_get_input_node_ids():
    edges = [
        {"source": "a", "target": "b"},
        {"source": "c", "target": "b"},
        {"source": "b", "target": "d"},
    ]
    assert set(_get_input_node_ids("b", edges)) == {"a", "c"}
    assert _get_input_node_ids("a", edges) == []


def test_is_batch_result_true():
    batch = [{"key": "a", "data": b""}, {"key": "b", "data": b""}]
    assert _is_batch_result(batch) is True


def test_is_batch_result_false():
    assert _is_batch_result(b"xxx") is False
    assert _is_batch_result({"key": "a", "data": b""}) is False
    assert _is_batch_result([]) is False
    assert _is_batch_result(["not dict"]) is False
    assert _is_batch_result([{"no_key": 1}]) is False


def test_is_batch_result_single_dict_not():
    assert _is_batch_result({"key": "a", "data": b""}) is False
