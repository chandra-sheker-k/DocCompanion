from pathlib import Path

from . import pdf_extractor
from . import docx_extractor
from . import txt_extractor
from . import csv_extractor
from . import excel_extractor
from . import markdown_extractor
from . import html_extractor
from . import pptx_extractor
from . import image_extractor
from . import json_extractor
from . import xml_extractor
from . import yaml_extractor
from . import epub_extractor
from . import rtf_extractor
from . import odt_extractor
from .cleaner import TextCleaner
from .language import LanguageDetector
from .models import ExtractionResult
from .exceptions import UnsupportedDocument

EXTRACTORS = {
    ".pdf": pdf_extractor.extract,
    ".docx": docx_extractor.extract,
    ".txt": txt_extractor.extract,
    ".csv": csv_extractor.extract,
    ".xlsx": excel_extractor.extract,
    ".xls": excel_extractor.extract,

    ".md": markdown_extractor.extract,
    ".html": html_extractor.extract,
    ".htm": html_extractor.extract,

    ".pptx": pptx_extractor.extract,
    ".json": json_extractor.extract,
    ".xml": xml_extractor.extract,
    ".yaml": yaml_extractor.extract,
    ".yml": yaml_extractor.extract,
    ".rtf": rtf_extractor.extract,
    ".odt": odt_extractor.extract,
    ".epub": epub_extractor.extract,

    ".png": image_extractor.extract,
    ".jpg": image_extractor.extract,
    ".jpeg": image_extractor.extract,
    ".bmp": image_extractor.extract,
    ".tiff": image_extractor.extract,
}

#def extract_text(path: str) -> ExtractionResult:
def extract_text(path):
    extension = Path(path).suffix.lower()
    extractor = EXTRACTORS.get(extension)
    if extractor is None:
        raise UnsupportedDocument(extension)
    result = extractor(path)
    cleaner = TextCleaner()
    result.text = cleaner.clean_text(result.text)
    result.language = LanguageDetector.detect(result.text)
    for page in result.pages:
        page.text = cleaner.clean_text(page.text)
    return result

