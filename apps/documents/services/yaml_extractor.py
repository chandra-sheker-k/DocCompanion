
"""
YAML document extractor.

Supports:

- .yaml
- .yml

Returns a standardized ExtractionResult.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List
import yaml

from .models import ExtractionResult, PageContent
from .utils import build_result

def _flatten_yaml(obj: Any, prefix: str = "", lines: List[str] | None = None) -> List[str]:
    """
    Recursively flatten YAML.
    Example
    app:
      name: DocCompanion
    becomes
    app.name : DocCompanion
    """

    if lines is None:
        lines = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            new_prefix = (f"{prefix}.{key}" if prefix else str(key))
            _flatten_yaml(value, new_prefix, lines)

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            new_prefix = f"{prefix}[{index}]"
            _flatten_yaml(value, new_prefix, lines)
    else:
        value = "" if obj is None else obj
        lines.append(f"{prefix}: {value}")
    return lines

def extract(path: str) -> ExtractionResult:
    # Extract YAML document.

    warnings = []
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

    except UnicodeDecodeError:
        with open(path, "r", encoding="latin-1") as file:
            data = yaml.safe_load(file)
        warnings.append("UTF-8 decoding failed. File read using latin-1.")

    except yaml.YAMLError as ex:
        raise RuntimeError(f"Unable to parse YAML: {ex}")

    pretty_yaml = yaml.dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False
    )

    flattened = _flatten_yaml(data)
    flattened_text = "\n".join(flattened)
    full_text = (
        "===== YAML =====\n\n"
        + pretty_yaml
        + "\n\n===== FLATTENED VIEW =====\n\n"
        + flattened_text
    )

    pages = [
        PageContent(page=1, text=full_text)
    ]

    metadata = {
        "filename": Path(path).name,
        "extension": ".yaml",
        "pages": 1,
        "title": Path(path).stem,
        "author": "",
        "language": "",
        "created": "",
        "modified": "",
        "document_type": "YAML",
    }

    return build_result(text=full_text, pages=pages,
        metadata=metadata, warnings=warnings)