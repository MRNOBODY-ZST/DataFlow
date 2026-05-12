"""DAG executor: topological sort + Ray remote execution."""
import logging
import os
from collections import defaultdict, deque

import ray

from nodes import NODE_REGISTRY
from nodes.base import NodeContext

logger = logging.getLogger(__name__)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "dataflow")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "dataflow123")
MINIO_INPUT_BUCKET = os.getenv("MINIO_INPUT_BUCKET", "dataflow-input")
MINIO_OUTPUT_BUCKET = os.getenv("MINIO_OUTPUT_BUCKET", "dataflow-output")
MINIO_TEMP_BUCKET = os.getenv("MINIO_TEMP_BUCKET", "dataflow-temp")


def _make_minio():
    from minio import Minio
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )


def _topological_sort(nodes: list[dict], edges: list[dict]) -> list[dict]:
    """Kahn's algorithm — returns nodes in execution order."""
    node_map = {n["id"]: n for n in nodes}
    in_degree: dict[str, int] = defaultdict(int)
    children: dict[str, list[str]] = defaultdict(list)

    for e in edges:
        children[e["source"]].append(e["target"])
        in_degree[e["target"]] += 1

    queue = deque([n for n in nodes if in_degree[n["id"]] == 0])
    order: list[dict] = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for child_id in children[node["id"]]:
            in_degree[child_id] -= 1
            if in_degree[child_id] == 0:
                queue.append(node_map[child_id])
    return order


def _get_input_node_ids(node_id: str, edges: list[dict]) -> list[str]:
    return [e["source"] for e in edges if e["target"] == node_id]


@ray.remote
def _execute_node_remote(node_type: str, inputs: list, config: dict, ctx_kwargs: dict):
    minio_client = _make_minio()
    ctx = NodeContext(minio_client=minio_client, **ctx_kwargs)
    node_cls = NODE_REGISTRY.get(node_type)
    if node_cls is None:
        raise ValueError(f"Unknown node type: {node_type}")
    return node_cls().execute(inputs, ctx)


def run_pipeline(graph: dict, task_id: str, input_key: str, reporter) -> str | None:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    ordered = _topological_sort(nodes, edges)
    total = len(ordered)
    results: dict[str, object] = {}  # node_id -> Ray ObjectRef

    for i, node in enumerate(ordered):
        node_id = node["id"]
        node_type = node["type"]
        config = dict(node.get("data", {}))

        # Inject input_key for source nodes (no incoming edges)
        if not _get_input_node_ids(node_id, edges) and "key" not in config:
            config["input_key"] = input_key

        input_refs = [results[src] for src in _get_input_node_ids(node_id, edges)]
        resolved_inputs = ray.get(input_refs) if input_refs else []

        ctx_kwargs = {
            "task_id": task_id,
            "node_id": node_id,
            "config": config,
            "input_bucket": MINIO_INPUT_BUCKET,
            "output_bucket": MINIO_OUTPUT_BUCKET,
            "temp_bucket": MINIO_TEMP_BUCKET,
        }

        reporter.report(task_id, node_id, int((i / total) * 100), "RUNNING")
        results[node_id] = _execute_node_remote.remote(node_type, resolved_inputs, config, ctx_kwargs)

    # Get final output (last node in topo order is the sink)
    last_node_id = ordered[-1]["id"] if ordered else None
    if last_node_id:
        output = ray.get(results[last_node_id])
        reporter.report(task_id, last_node_id, 100, "SUCCESS")
        return output if isinstance(output, str) else None
    return None
