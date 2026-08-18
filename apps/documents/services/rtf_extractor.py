
"""
RTF document extractor.

Supports:
    *.rtf

Converts Rich Text Format into plain text suitable for
chunking and embedding.

Returns:
    ExtractionResult
"""

from __future__ import annotations
from pathlib import Path
from striprtf.striprtf import rtf_to_text

from .models import ExtractionResult, PageContent
from .utils import build_result

def extract(path: str) -> ExtractionResult:
    """
    Extract text from an RTF document.

    Parameters
    ----------
    path : str
        Absolute path to the RTF file.

    Returns
    -------
    ExtractionResult
    """

    warnings = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as file:
            raw_rtf = file.read()
    except Exception as ex:
        raise RuntimeError(f"Unable to read RTF file: {ex}")

    try:
        text = rtf_to_text(raw_rtf)
    except Exception as ex:
        raise RuntimeError(f"Unable to parse RTF: {ex}")

    text = text.strip()
    pages = [
        PageContent(page=1, text=text)
    ]

    metadata = {
        "filename": Path(path).name,
        "extension": ".rtf",
        "pages": 1,
        "title": Path(path).stem,
        "author": "",
        "language": "",
        "created": "",
        "modified": "",
        "document_type": "RTF"
    }

    return build_result(text=text, pages=pages,
                        metadata=metadata, warnings=warnings)