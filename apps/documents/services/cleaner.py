
from __future__ import annotations

import re
import unicodedata


class TextCleaner:
    def clean_text(self, text: str) -> str:
        if not text:
            return ""

        text = unicodedata.normalize("NFKC", text)

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Remove zero-width characters
        text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)

        # Replace tabs
        text = re.sub(r"\t+", " ", text)

        # Collapse spaces
        text = re.sub(r"[ ]{2,}", " ", text)

        # Collapse blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        text = re.sub(r"\u200b", "", text)

        return text.strip()
