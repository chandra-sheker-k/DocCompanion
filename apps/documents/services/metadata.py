
from pathlib import Path
import fitz

def build_metadata(path: str) -> dict:

    metadata = {
        "filename": Path(path).name,
        "extension": Path(path).suffix.lower(),
        "title": "",
        "author": "",
        "pages": 0,
    }

    if metadata["extension"] == ".pdf":
        doc = fitz.open(path)
        pdf_meta = doc.metadata
        metadata["pages"] = len(doc)
        metadata["title"] = pdf_meta.get("title", "")
        metadata["author"] = pdf_meta.get("author", "")
    return metadata