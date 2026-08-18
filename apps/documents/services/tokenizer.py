
"""
Simple tokenizer.

Provides approximate token counts without
requiring a model tokenizer.
"""

import re

class Tokenizer:

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return len(re.findall(r"\S+", text))

    @staticmethod
    def word_count(text: str) -> int:
        return len(text.split())

    @staticmethod
    def character_count(text: str) -> int:
        return len(text)