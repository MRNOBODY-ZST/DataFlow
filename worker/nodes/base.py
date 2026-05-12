from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from minio import Minio


@dataclass
class NodeContext:
    task_id: str
    node_id: str
    config: dict
    minio_client: Minio
    input_bucket: str
    output_bucket: str
    temp_bucket: str


class BaseNode(ABC):
    @abstractmethod
    def execute(self, inputs: list[Any], ctx: NodeContext) -> Any:
        """Execute this node.

        Args:
            inputs: outputs from upstream nodes (in edge order)
            ctx: runtime context with MinIO client and config

        Returns:
            Any value that downstream nodes may consume
        """
        pass
