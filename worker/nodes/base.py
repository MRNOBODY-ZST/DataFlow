from abc import ABC, abstractmethod
from dataclasses import dataclass, field as dc_field
from typing import Any

from minio import Minio


@dataclass
class WidgetConfig:
    key_placeholder: str | None = None
    value_placeholder: str | None = None
    value_type: str | None = None
    value_options: list[str] | None = None

    def to_dict(self) -> dict | None:
        d = {}
        if self.key_placeholder is not None:
            d["keyPlaceholder"] = self.key_placeholder
        if self.value_placeholder is not None:
            d["valuePlaceholder"] = self.value_placeholder
        if self.value_type is not None:
            d["valueType"] = self.value_type
        if self.value_options is not None:
            d["valueOptions"] = self.value_options
        return d or None


@dataclass
class FieldDef:
    key: str
    label: str
    type: str = "text"
    placeholder: str | None = None
    required: bool = False
    auto_filled: bool = False
    options: list[str] | None = None
    widget: str | None = None
    widget_config: WidgetConfig | None = None
    inline: bool = False

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "label": self.label,
            "type": self.type,
            "placeholder": self.placeholder,
            "required": self.required,
            "autoFilled": self.auto_filled,
            "options": self.options,
            "widget": self.widget,
            "widgetConfig": self.widget_config.to_dict() if self.widget_config else None,
            "inline": self.inline,
        }


@dataclass
class NodeSchema:
    type: str
    label: str
    category: str
    icon: str
    fields: list[FieldDef] = dc_field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "label": self.label,
            "category": self.category,
            "icon": self.icon,
            "fields": [f.to_dict() for f in self.fields],
        }


@dataclass
class NodeContext:
    task_id: str
    node_id: str
    config: dict
    minio_client: Minio
    input_bucket: str
    output_bucket: str
    temp_bucket: str
    output_prefix: str = ""
    source_key: str = ""

    def output_key(self, filename: str) -> str:
        if self.output_prefix:
            return f"{self.output_prefix}/{filename}"
        return filename

    @property
    def source_filename(self) -> str:
        if self.source_key:
            import pathlib
            return pathlib.PurePosixPath(self.source_key).name
        return ""


class BaseNode(ABC):
    @classmethod
    def schema(cls) -> NodeSchema | None:
        return None

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
