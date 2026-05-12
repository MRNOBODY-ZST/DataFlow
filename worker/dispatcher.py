"""Kafka consumer — listens for task.dispatch, runs pipeline via Ray."""
import json
import logging
import os

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


def fetch_graph(graph_id: str) -> dict:
    client = MongoClient(MONGO_URI)
    db = client["dataflow"]
    doc = db["pipeline_graphs"].find_one({"_id": graph_id})
    client.close()
    if doc is None:
        raise ValueError(f"Graph not found: {graph_id}")
    return doc


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

    for msg in consumer:
        task = msg.value
        task_id = str(task["taskId"])
        graph_id = task["graphId"]
        input_key = task.get("inputKey", "")

        logger.info("Received task %s (graph=%s)", task_id, graph_id)
        reporter.report(task_id, None, 0, "RUNNING", "Pipeline started")

        try:
            graph = fetch_graph(graph_id)
            output_key = run_pipeline(graph, task_id, input_key, reporter)
            logger.info("Task %s completed. output=%s", task_id, output_key)
        except Exception as e:
            logger.exception("Task %s failed", task_id)
            reporter.report(task_id, None, 0, "FAILED", str(e))


if __name__ == "__main__":
    main()
