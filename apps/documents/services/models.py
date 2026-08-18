
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class PageContent:
    page: int
    text: str
    title: str = ""
    metadata: dict = field(default_factory=dict)

@dataclass
class ExtractionResult:
    text: str
    pages: List[PageContent]
    metadata: Dict = field(default_factory=dict)
    statistics: Dict = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    language: str = "unknown"