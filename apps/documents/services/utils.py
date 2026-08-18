
from .models import ExtractionResult, PageContent

def build_result(text: str, pages: list, metadata: dict, warnings=None):
    warnings = warnings or []

    return ExtractionResult(
        text=text,
        pages=pages,
        metadata=metadata,
        statistics={
            "characters": len(text),
            "words": len(text.split()),
            "paragraphs": len(
                [p for p in text.split("\n\n") if p.strip()]
            ),
        },
        warnings=warnings,
    )