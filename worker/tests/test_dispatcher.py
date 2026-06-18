import pytest
from dispatcher import _normalize_graph


def test_normalize_graph_typical():
    doc = {
        "_id": "g1",
        "nodes": [
            {"id": "n1", "type": "csv_reader", "data": {"key": "x.csv"}},
            {"_id": "n2", "type": "filter", "position": {"x": 0, "y": 0}, "data": {}},
        ],
        "edges": [
            {"id": "e1", "source": "n1", "target": "n2", "sourceHandle": "out", "targetHandle": "in"},
        ],
        "version": 3,
    }
    out = _normalize_graph(doc)
    assert out["_id"] == "g1"
    assert len(out["nodes"]) == 2
    assert out["nodes"][0]["id"] == "n1"
    assert out["edges"][0]["source"] == "n1"
    assert out["edges"][0]["target"] == "n2"
    assert out["version"] == 3


def test_normalize_graph_node_missing_id():
    with pytest.raises(ValueError, match="missing id"):
        _normalize_graph({"nodes": [{"type": "x"}], "edges": []})


def test_normalize_graph_edge_missing_source():
    with pytest.raises(ValueError, match="missing source or target"):
        _normalize_graph({
            "nodes": [{"id": "a"}, {"id": "b"}],
            "edges": [{"target": "b"}],
        })


def test_normalize_graph_edge_id_generated():
    out = _normalize_graph({
        "nodes": [{"id": "a"}, {"id": "b"}],
        "edges": [{"source": "a", "target": "b"}],
    })
    assert out["edges"][0]["id"] == "edge_0"
