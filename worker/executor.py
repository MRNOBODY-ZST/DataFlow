"""DAG executor: topological sort + Ray remote execution with batch fan-out."""
import logging
import os
import pathlib
import re
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


class NodeExecutionError(Exception):
    """
    Raised by worker to wrap any failure inside a node's execute().
    Driver-side run_pipeline extracts just the friendly message.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


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


def _is_batch_result(value) -> bool:
    return (
        isinstance(value, list)
        and len(value) > 0
        and isinstance(value[0], dict)
        and "key" in value[0]
        and "data" in value[0]
    )


def _stem(key: str) -> str:
    return pathlib.PurePosixPath(key).stem


def _friendly(err: Exception) -> str:
    if isinstance(err, NodeExecutionError):
        return err.message
    if isinstance(err, RuntimeError):
        return str(err)
    return f"{type(err).__name__}: {err}"


@ray.remote
def _execute_node_remote(node_type: str, inputs: list, config: dict, ctx_kwargs: dict):
    minio_client = _make_minio()
    ctx = NodeContext(minio_client=minio_client, **ctx_kwargs)
    node_cls = NODE_REGISTRY.get(node_type)
    if node_cls is None:
        raise NodeExecutionError(f"Unknown node type: {node_type}")
    try:
        return node_cls().execute(inputs, ctx)
    except NodeExecutionError:
        raise
    except Exception as e:
        raise NodeExecutionError(_friendly(e)) from None


@ray.remote
def _execute_batch_item(node_type: str, item_data, config: dict, ctx_kwargs: dict):
    minio_client = _make_minio()
    ctx = NodeContext(minio_client=minio_client, **ctx_kwargs)
    node_cls = NODE_REGISTRY.get(node_type)
    if node_cls is None:
        raise NodeExecutionError(f"Unknown node type: {node_type}")
    if isinstance(item_data, dict) and "data" in item_data:
        inputs = [item_data["data"]]
    else:
        inputs = [item_data]
    try:
        return node_cls().execute(inputs, ctx)
    except NodeExecutionError:
        raise
    except Exception as e:
        raise NodeExecutionError(_friendly(e)) from None


def _extract_friendly_from_ray_error(ray_err) -> str:
    s = str(ray_err)
    for pat in [r"NodeExecutionError:\s*(.+)", r"RuntimeError:\s*(.+)"]:
        m = re.search(pat, s, re.S)
        if m:
            return m.group(1).strip()
    last_line = s.strip().split("\n")[-1] if s else ""
    return last_line[:400] if last_line else str(ray_err)[:400]


def run_pipeline(graph: dict, task_id: str, reporter, user_id: str = "") -> str | None:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    ordered = _topological_sort(nodes, edges)
    total = len(ordered)
    results: dict[str, object] = {}
    batch_mode: dict[str, bool] = {}
    source_keys: dict[str, str] = {}

    user_prefix = f"u/{user_id}" if user_id else ""

    for i, node in enumerate(ordered):
        node_id = node["id"]
        node_type = node["type"]
        config = dict(node.get("data", {}))

        input_node_ids = _get_input_node_ids(node_id, edges)
        input_refs = [results[src] for src in input_node_ids]

        try:
            resolved_inputs = ray.get(input_refs) if input_refs else []
        except Exception as e:
            raise RuntimeError(f"上游节点输入获取失败: {_extract_friendly_from_ray_error(e)}") from None

        any_batch_upstream = any(batch_mode.get(src, False) for src in input_node_ids)

        node_source_key = config.get("key", "")
        if not node_source_key:
            for src_id in input_node_ids:
                if source_keys.get(src_id):
                    node_source_key = source_keys[src_id]
                    break
        source_keys[node_id] = node_source_key

        scoped_config = dict(config)
        if user_prefix:
            if "key" in scoped_config and scoped_config["key"]:
                scoped_config["key"] = f"{user_prefix}/{scoped_config['key']}"
            if "prefix" in scoped_config and scoped_config["prefix"]:
                scoped_config["prefix"] = f"{user_prefix}/{scoped_config['prefix']}"

        output_prefix = f"{user_prefix}/run_{task_id}" if user_prefix else f"run_{task_id}"

        ctx_kwargs = {
            "task_id": task_id,
            "node_id": node_id,
            "config": scoped_config,
            "input_bucket": MINIO_INPUT_BUCKET,
            "output_bucket": MINIO_OUTPUT_BUCKET,
            "temp_bucket": MINIO_TEMP_BUCKET,
            "output_prefix": output_prefix,
            "source_key": node_source_key,
        }

        reporter.report(task_id, node_id, int((i / total) * 100), "RUNNING")

        if any_batch_upstream:
            batch_input_idx = next(
                j for j, src in enumerate(input_node_ids) if batch_mode.get(src, False)
            )
            batch_data = resolved_inputs[batch_input_idx]

            if not isinstance(batch_data, list):
                batch_data = [batch_data]

            item_count = len(batch_data)
            logger.info("Batch fan-out: node=%s items=%d", node_id, item_count)

            refs = []
            for idx, item in enumerate(batch_data):
                item_ctx = dict(ctx_kwargs)
                if isinstance(item, dict) and "key" in item:
                    item_ctx["source_key"] = item["key"]

                refs.append(_execute_batch_item.remote(node_type, item, scoped_config, item_ctx))

            try:
                collected = ray.get(refs)
            except Exception as e:
                raise RuntimeError(f"节点 {node_id} 批处理失败: {_extract_friendly_from_ray_error(e)}") from None

            target_fmt = config.get("format", "")
            wrapped = []
            for idx, result in enumerate(collected):
                item = batch_data[idx]
                orig_key = item["key"] if isinstance(item, dict) and "key" in item else f"item_{idx}"
                if isinstance(result, dict) and "key" in result and "data" in result:
                    wrapped.append(result)
                else:
                    if target_fmt:
                        stem = _stem(orig_key)
                        ext = target_fmt.lower().replace("jpeg", "jpg")
                        orig_key = f"{pathlib.PurePosixPath(orig_key).parent}/{stem}.{ext}"
                        if orig_key.startswith("/"):
                            orig_key = orig_key[1:]
                    wrapped.append({"key": orig_key, "data": result})
            results[node_id] = ray.put(wrapped)
            batch_mode[node_id] = True

            reporter.report(
                task_id, node_id,
                int(((i + 1) / total) * 100), "RUNNING",
                f"Processed {item_count} items",
            )
        else:
            ref = _execute_node_remote.remote(node_type, resolved_inputs, scoped_config, ctx_kwargs)
            try:
                output = ray.get(ref)
            except Exception as e:
                raise RuntimeError(f"节点 {node_id} 执行失败: {_extract_friendly_from_ray_error(e)}") from None

            if _is_batch_result(output):
                results[node_id] = ray.put(output)
                batch_mode[node_id] = True
                logger.info("Batch detected: node=%s items=%d", node_id, len(output))
            else:
                results[node_id] = ray.put(output)
                batch_mode[node_id] = False

    last_node_id = ordered[-1]["id"] if ordered else None
    if last_node_id:
        try:
            output = ray.get(results[last_node_id])
        except Exception as e:
            raise RuntimeError(f"最终节点结果获取失败: {_extract_friendly_from_ray_error(e)}") from None

        strip = (user_prefix + "/") if user_prefix else ""
        if isinstance(output, list):
            full = f"{output_prefix}/"
            return full[len(strip):] if strip and full.startswith(strip) else full
        if isinstance(output, str):
            return output[len(strip):] if strip and output.startswith(strip) else output
        return None
    return None
