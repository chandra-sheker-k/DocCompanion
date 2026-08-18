
from pathlib import Path

from .metadata import build_metadata
from .models import PageContent
from .utils import build_result

def extract(path):

    text = Path(path).read_text(
        encoding="utf-8",
        errors="ignore",
    )

    pages = [
        PageContent(
            page=1,
            text=text,
        )
    ]

    return build_result(text=text, pages=pages, metadata=build_metadata(path))