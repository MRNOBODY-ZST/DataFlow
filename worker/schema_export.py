"""Export all node schemas as JSON.

Usage:
    python schema_export.py              # writes to node_schemas.json
    python schema_export.py --stdout     # prints to stdout
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nodes import NODE_REGISTRY


def export_schemas() -> list[dict]:
    schemas = []
    for node_type, node_cls in NODE_REGISTRY.items():
        s = node_cls.schema()
        if s is not None:
            schemas.append(s.to_dict())
    return schemas


def main():
    schemas = export_schemas()
    output = json.dumps(schemas, ensure_ascii=False, indent=2)

    if "--stdout" in sys.argv:
        print(output)
    else:
        out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "node_schemas.json")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Exported {len(schemas)} node schemas to {out_path}")


if __name__ == "__main__":
    main()
