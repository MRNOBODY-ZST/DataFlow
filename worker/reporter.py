import json
import logging
import os

from kafka import KafkaProducer

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_PROGRESS = "task.progress"

_producer: KafkaProducer | None = None


def _get_producer() -> KafkaProducer:
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v).encode(),
            key_serializer=lambda k: str(k).encode(),
        )
    return _producer


def report(task_id: str, node_id: str | None, progress: int, status: str, message: str = "", output_key: str | None = None) -> None:
    payload = {
        "taskId": task_id,
        "nodeId": node_id,
        "progress": max(0, min(100, progress)),
        "status": status,
        "message": message,
        "outputKey": output_key,
    }
    try:
        _get_producer().send(TOPIC_PROGRESS, key=task_id, value=payload)
        _get_producer().flush()
        logger.debug("Reported progress: %s", payload)
    except Exception as e:
        logger.error("Failed to report progress: %s", e)
