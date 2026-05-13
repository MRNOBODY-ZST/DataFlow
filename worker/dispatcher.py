"""Kafka consumer — listens for task.dispatch, runs pipeline via Ray."""
import json
import logging
import os
import signal
import sys

import ray
from kafka import KafkaConsumer
from pymongo import MongoClient

import reporter
from executor import run_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("dispatcher")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://dataflow:dataflow123@localhost:27017/dataflow?authSource=admin")
TOPIC_DISPATCH = "task.dispatch"


def _normalize_graph(doc: dict) -> dict:
    nodes = []
    for node in doc.get("nodes", []):
        node_id = node.get("id") or node.get("_id")
        if node_id is None:
            raise ValueError("Graph node missing id")
        nodes.append({
            "id": node_id,
            "type": node.get("type"),
            "position": node.get("position", {}),
            "data": node.get("data", {}),
        })

    edges = []
    for i, edge in enumerate(doc.get("edges", [])):
        source = edge.get("source")
        target = edge.get("target")
        if source is None or target is None:
            raise ValueError("Graph edge missing source or target")
        edges.append({
            "id": edge.get("id") or edge.get("_id") or f"edge_{i}",
            "source": source,
            "target": target,
            "sourceHandle": edge.get("sourceHandle"),
            "targetHandle": edge.get("targetHandle"),
        })

    return {
        "_id": doc.get("_id"),
        "nodes": nodes,
        "edges": edges,
        "version": doc.get("version", 1),
        "updatedAt": doc.get("updatedAt"),
    }


def fetch_graph(graph_id: str) -> dict:
    client = MongoClient(MONGO_URI)
    db = client["dataflow"]
    doc = db["pipeline_graphs"].find_one({"_id": graph_id})
    client.close()
    if doc is None:
        raise ValueError(f"Graph not found: {graph_id}")
    return _normalize_graph(doc)


def main():
    ray.init(ignore_reinit_error=True)
    logger.info("Ray initialised. Connecting to Kafka %s ...", KAFKA_BOOTSTRAP)

    consumer = KafkaConsumer(
        TOPIC_DISPATCH,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id="dataflow-worker",
        value_deserializer=lambda m: json.loads(m.decode()),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )
    logger.info("Listening on topic: %s", TOPIC_DISPATCH)

    def shutdown(signum, frame):
        logger.info("Received signal %s, shutting down worker.", signum)
        consumer.close()
        ray.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    for msg in consumer:
        task = msg.value
        task_id = str(task["taskId"])
        graph_id = task["graphId"]

        logger.info("Received task %s (graph=%s)", task_id, graph_id)
        reporter.report(task_id, None, 0, "RUNNING", "Pipeline started")

        try:
            graph = fetch_graph(graph_id)
            output_key = run_pipeline(graph, task_id, reporter)
            reporter.report(task_id, None, 100, "SUCCESS", "Pipeline completed", output_key=output_key)
            logger.info("Task %s completed. output=%s", task_id, output_key)
        except Exception as e:
            logger.exception("Task %s failed", task_id)
            reporter.report(task_id, None, 0, "FAILED", str(e))


if __name__ == "__main__":
    main()
