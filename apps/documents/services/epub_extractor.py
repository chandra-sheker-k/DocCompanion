
"""
EPUB document extractor.

Supports:
    *.epub

Extracts:
    - Chapters
    - Headings
    - Paragraphs
    - Metadata

Returns:
    ExtractionResult
"""

from __future__ import annotations

from pathlib import Path
from typing import List
from bs4 import BeautifulSoup
from ebooklib import epub, ITEM_DOCUMENT

from .models import ExtractionResult, PageContent
from .utils import build_result

def _extract_html(html: bytes) -> str:
    # Convert XHTML content into plain text.
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return text

def extract(path: str) -> ExtractionResult:
    # Extract text from an EPUB document.
    warnings = []
    try:
        book = epub.read_epub(path)
    except Exception as ex:
        raise RuntimeError(f"Unable to open EPUB file: {ex}")

    pages: List[PageContent] = []
    all_text = []
    chapter = 1
    for item in book.get_items():
        if item.get_type() != ITEM_DOCUMENT:
            continue
        text = _extract_html(item.get_content())

        if not text.strip():
            continue

        pages.append(
            PageContent(page=chapter, text=text)
        )
        all_text.append(text)
        chapter += 1

    metadata = {
        "filename": Path(path).name,
        "extension": ".epub",
        "pages": len(pages),
        "title": "",
        "author": "",
        "language": "",
        "publisher": "",
        "identifier": "",
        "created": "",
        "modified": "",
        "document_type": "EPUB",
    }

    # -------- Metadata --------
    title = book.get_metadata("DC", "title")
    if title:
        metadata["title"] = title[0][0]

    creator = book.get_metadata("DC", "creator")
    if creator:
        metadata["author"] = creator[0][0]

    language = book.get_metadata("DC", "language")
    if language:
        metadata["language"] = language[0][0]

    publisher = book.get_metadata("DC", "publisher")
    if publisher:
        metadata["publisher"] = publisher[0][0]

    identifier = book.get_metadata("DC", "identifier")
    if identifier:
        metadata["identifier"] = identifier[0][0]

    full_text = "\n\n".join(all_text)

    return build_result(text=full_text, pages=pages,
                        metadata=metadata, warnings=warnings)