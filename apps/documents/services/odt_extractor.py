
"""
OpenDocument Text (.odt) extractor.

Supports:
    *.odt

Returns:
    ExtractionResult
"""

from __future__ import annotations

from pathlib import Path
from typing import List
from odf import text
from odf.opendocument import load

from .models import ExtractionResult, PageContent
from .utils import build_result

def _extract_paragraphs(document) -> List[str]:
    # Extract all paragraphs from an ODT document.

    paragraphs = []
    for paragraph in document.getElementsByType(text.P):
        value = ""
        for node in paragraph.childNodes:
            if hasattr(node, "data"):
                value += node.data
        value = value.strip()
        if value:
            paragraphs.append(value)
    return paragraphs

def _extract_headings(document) -> List[str]:
    # Extract headings.
    headings = []

    for heading in document.getElementsByType(text.H):
        value = ""
        for node in heading.childNodes:
            if hasattr(node, "data"):
                value += node.data
        value = value.strip()
        if value:
            headings.append(value)
    return headings

def extract(path: str) -> ExtractionResult:
    #Extract text from an ODT document.

    warnings = []

    try:
        document = load(path)
    except Exception as ex:
        raise RuntimeError(f"Unable to open ODT document: {ex}")

    headings = _extract_headings(document)
    paragraphs = _extract_paragraphs(document)
    content = []

    if headings:
        content.append("===== HEADINGS =====")
        content.extend(headings)
        content.append("")

    content.append("===== CONTENT =====")
    content.extend(paragraphs)
    full_text = "\n".join(content)
    pages = [
        PageContent(page=1, text=full_text)
    ]

    metadata = {
        "filename": Path(path).name,
        "extension": ".odt",
        "pages": 1,
        "title": Path(path).stem,
        "author": "",
        "language": "",
        "created": "",
        "modified": "",
        "document_type": "OpenDocument Text"
    }

    return build_result(text=full_text, pages=pages
                        , metadata=metadata, warnings=warnings)