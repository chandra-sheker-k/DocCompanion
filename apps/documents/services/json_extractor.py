
"""
JSON document extractor.

Converts JSON into readable text suitable for
chunking and embedding.

Returns:
    ExtractionResult
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List

from .models import ExtractionResult, PageContent
from .utils import build_result

def _flatten_json(obj: Any, prefix: str = "", lines: List[str] | None = None) -> List[str]:
    """
    Recursively flatten JSON into key-value lines.
    Example
    {
      "person": {
          "name": "John"
      }
    }
    becomes
    person.name : John
    """

    if lines is None:
        lines = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            _flatten_json(value, new_prefix, lines)
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            new_prefix = f"{prefix}[{index}]"
            _flatten_json(value, new_prefix, lines)
    else:
        lines.append(f"{prefix}: {obj}")
    return lines

def extract(path: str) -> ExtractionResult:
    # Extract text from a JSON document.

    warnings = []
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except UnicodeDecodeError:
        with open(path, "r", encoding="latin-1") as file:
            data = json.load(file)
        warnings.append("UTF-8 decoding failed. File read using latin-1.")

    pretty_json = json.dumps(data, indent=2, ensure_ascii=False)

    flattened = _flatten_json(data)
    flattened_text = "\n".join(flattened)

    full_text = (
        "===== JSON =====\n\n"
        + pretty_json
        + "\n\n===== FLATTENED VIEW =====\n\n"
        + flattened_text
    )

    pages = [
        PageContent(page=1, text=full_text)
    ]

    metadata = {
        "filename": Path(path).name,
        "extension": ".json",
        "pages": 1,
        "title": Path(path).stem,
        "author": "",
        "language": "",
        "created": "",
        "modified": "",
        "document_type": "JSON",
    }

    return build_result(text=full_text, pages=pages,
        metadata=metadata, warnings=warnings)