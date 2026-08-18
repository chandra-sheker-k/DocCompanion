
"""
XML document extractor.

Converts XML into a readable hierarchical text format
for chunking and embedding.

Returns:
    ExtractionResult
"""

from __future__ import annotations
from pathlib import Path
from typing import List
from lxml import etree

from .models import ExtractionResult, PageContent
from .utils import build_result

def _walk_node(element, level: int = 0, lines: List[str] | None = None):
    """
    Recursively walk an XML tree.
    Example output:
    <book>
      id = 10
      title : AI
      <author>
        John
    """

    if lines is None:
        lines = []

    indent = "    " * level

    # Opening tag
    lines.append(f"{indent}<{element.tag}>")

    # Attributes
    for key, value in element.attrib.items():
        lines.append(f"{indent}    @{key}: {value}")

    # Text
    if element.text:
        text = element.text.strip()
        if text:
            lines.append(f"{indent}    {text}")

    # Children
    for child in element:
        _walk_node(child, level + 1, lines)
    return lines

def extract(path: str) -> ExtractionResult:
    #Extract text from XML.

    warnings = []
    parser = etree.XMLParser(
        recover=True,
        remove_comments=False,
        remove_blank_text=True,
    )

    try:
        tree = etree.parse(path, parser)

    except Exception as ex:
        raise RuntimeError(f"Unable to parse XML: {ex}")

    root = tree.getroot()
    hierarchy = _walk_node(root)
    hierarchy_text = "\n".join(hierarchy)
    pretty_xml = etree.tostring(root, pretty_print=True, encoding="unicode")

    full_text = (
        "===== XML =====\n\n"
        + pretty_xml
        + "\n\n===== HIERARCHY =====\n\n"
        + hierarchy_text
    )

    pages = [
        PageContent(page=1, text=full_text)
    ]

    metadata = {
        "filename": Path(path).name,
        "extension": ".xml",
        "pages": 1,
        "title": Path(path).stem,
        "author": "",
        "language": "",
        "created": "",
        "modified": "",
        "document_type": "XML",
        "root_element": root.tag
    }

    return build_result(text=full_text, pages=pages,
        metadata=metadata, warnings=warnings)