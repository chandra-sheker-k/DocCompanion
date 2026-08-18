import fitz

from .metadata import build_metadata
from .ocr import extract_image_text
from .models import PageContent
from .utils import build_result

def extract(path):
    document = fitz.open(path)
    pages = []
    for page in document:
        text = page.get_text().strip()
        if not text:
            pix = page.get_pixmap(dpi=300)
            text = extract_image_text(pix)

        pages.append(
            PageContent(
                page = page.number + 1,
                text = text,
            )
        )

    full_text = "\n\n".join(page.text for page in pages)

    return build_result(text=full_text, pages=pages, metadata=build_metadata(path))
