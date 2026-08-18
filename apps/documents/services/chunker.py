
"""
Enterprise page-aware chunker.
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import List

from .models import PageContent
from ...settings.services import SettingsService

@dataclass
class Chunk:
    chunk_id: int
    chunk_uuid: uuid.UUID
    page: int
    text: str
    words: int
    start_word: int
    end_word: int

class TextChunker:
    def __init__(self):
        self.settings = SettingsService.get()
        self.chunk_size = self.settings.chunk_size
        self.overlap = self.settings.chunk_overlap

    def chunk(self, pages: List[PageContent]) -> List[Chunk]:
        chunks = []
        chunk_id = 1
        chunk_uuid: uuid.UUID = field(default_factory=uuid.uuid4)
        for page in pages:
            words = page.text.split()
            start = 0
            while start < len(words):
                end = start + self.chunk_size
                piece = words[start:end]
                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        chunk_uuid=chunk_uuid,
                        page=page.page,
                        text=" ".join(piece),
                        words=len(piece),
                        start_word=start,
                        end_word=min(end, len(words))
                    )
                )
                chunk_id += 1
                start += self.chunk_size - self.overlap
        return chunks
'''
from dataclasses import dataclass
from config.settings import CHUNK_SIZE, OVERLAP

@dataclass
class Chunk:

    index: int
    text: str
    word_count: int
    character_count: int
    page_number: int
    section_title: str
    start_char: int
    end_char: int
    token_count: int


class TextChunker:

    def __init__(self, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text):
        words = text.split()
        chunks = []
        start = 0
        index = 0

        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            chunks.append(
                Chunk(
                    index = index,
                    text = chunk_text,
                    word_count = len(chunk_words),
                    character_count = len(chunk_text),
                    token_count = int(len(chunk_words) * 1.3)
                )
            )
            index += 1
            start += self.chunk_size - self.overlap
        return chunks

'''