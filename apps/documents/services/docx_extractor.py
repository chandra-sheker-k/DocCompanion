import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

import fitz
from docx import Document
from docx.oxml.ns import qn

from .metadata import build_metadata
from .models import PageContent
from .utils import build_result


logger = logging.getLogger(__name__)


def extract(path):
    pages = _extract_rendered_pages(path) or _extract_word_page_breaks(path)
    text = "\n\n".join(page.text for page in pages if page.text)
    metadata = build_metadata(path)
    metadata.update({
        "pages": len(pages),
        "page_number_source": (
            "rendered_layout" if len(pages) > 1 else "document_default"
        ),
    })

    return build_result(text=text, pages=pages, metadata=metadata)


def _extract_rendered_pages(path):
    """Render DOCX locally so citations use the document's real pagination."""
    office = shutil.which("libreoffice") or shutil.which("soffice")
    if office is None:
        return None

    try:
        with tempfile.TemporaryDirectory(prefix="doccompanion-docx-") as temp_dir:
            output_dir = Path(temp_dir)
            profile_dir = output_dir / "office-profile"
            command = [
                office,
                "--headless",
                f"-env:UserInstallation={profile_dir.as_uri()}",
                "--convert-to",
                "pdf",
                "--outdir",
                str(output_dir),
                str(Path(path).resolve()),
            ]
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )

            pdf_path = output_dir / f"{Path(path).stem}.pdf"
            if not pdf_path.exists():
                return None

            pages = []
            with fitz.open(pdf_path) as rendered_document:
                for page in rendered_document:
                    pages.append(
                        PageContent(
                            page=page.number + 1,
                            text=page.get_text().strip(),
                        )
                    )

            return pages or None
    except (OSError, subprocess.SubprocessError, fitz.FileDataError) as exc:
        logger.warning("Unable to render DOCX pagination for %s: %s", path, exc)
        return None


def _extract_word_page_breaks(path):
    """Fallback to page boundaries saved by Word in the DOCX XML."""
    document = Document(path)
    page_buffers = [[]]

    for paragraph in document.paragraphs:
        for node in paragraph._p.iter():
            if node.tag == qn("w:t") and node.text:
                page_buffers[-1].append(node.text)
            elif node.tag == qn("w:tab"):
                page_buffers[-1].append("\t")
            elif node.tag == qn("w:lastRenderedPageBreak"):
                _start_page(page_buffers)
            elif node.tag == qn("w:br"):
                if node.get(qn("w:type")) == "page":
                    _start_page(page_buffers)
                else:
                    page_buffers[-1].append("\n")

        page_buffers[-1].append("\n")

    return [
        PageContent(page=page_number, text="".join(buffer).strip())
        for page_number, buffer in enumerate(page_buffers, start=1)
    ]


def _start_page(page_buffers):
    # Avoid duplicate empty pages when explicit and rendered break markers are
    # adjacent in the XML.
    if "".join(page_buffers[-1]).strip():
        page_buffers.append([])
