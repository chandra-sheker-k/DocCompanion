from pathlib import Path
import logging

from django.db import transaction
from django.utils import timezone
from django_q.tasks import async_task

from apps.common.utils.checksum import calculate_checksum
from apps.documents.models import Document, DocumentChunk
from apps.documents.services.extractor import extract_text
from apps.documents.services.chunker import TextChunker
from apps.embeddings.services.embedding_service import EmbeddingService
from apps.embeddings.services.index_builder import IndexBuilder

logger = logging.getLogger(__name__)


class DocumentService:

    @staticmethod
    @transaction.atomic
    def process(document):
        """
        Extract text, create chunks and incrementally index
        an already-saved Document.
        """

        # Serialize processing with deletion for this document. Without this
        # lock, a queued worker could save a stale instance after deletion and
        # recreate data that the user already removed.
        try:
            document = Document.objects.select_for_update().get(pk=document.pk)
        except Document.DoesNotExist:
            return None

        result = extract_text(document.file.path)

        document.extracted_text = result.text
        document.page_count = len(result.pages)
        document.language = result.language
        document.metadata = result.metadata
        document.status = Document.Status.PROCESSING
        document.save(
            update_fields=[
                "extracted_text",
                "page_count",
                "language",
                "metadata",
                "status",
            ]
        )

        chunker = TextChunker()
        chunks = chunker.chunk(result.pages)

        DocumentChunk.objects.filter(document=document).delete()

        chunk_rows = []

        for chunk in chunks:
            chunk_rows.append(
                DocumentChunk(
                    document=document,
                    chunk_index=chunk.chunk_id,
                    page_number=chunk.page,
                    text=chunk.text,
                    character_count=len(chunk.text),
                    word_count=chunk.words,
                    token_count=int(chunk.words * 1.3),
                    start_char=chunk.start_word,
                    end_char=chunk.end_word
                )
            )

        try:

            DocumentChunk.objects.bulk_create(chunk_rows)

            document.chunk_count = len(chunk_rows)
            document.status = Document.Status.READY
            document.processed_at = timezone.now()
            document.save(
                update_fields=[
                    "chunk_count",
                    "status",
                    "processed_at",
                ]
            )

            # Incremental indexing
            EmbeddingService().index_document(document)
        except Exception as exc:
            document.error_message = str(exc)

            document.save(
                update_fields=[
                    "status",
                    "error_message",
                ]
            )
        return document

    @staticmethod
    def ingest_document(uploaded_file):

        checksum = calculate_checksum(uploaded_file)

        existing = Document.objects.filter(checksum=checksum).first()
        if existing:
            return existing
            # raise ValueError("Document already exists.")

        document = Document.objects.create(
            file=uploaded_file,
            name=Path(uploaded_file.name).stem,
            original_name=uploaded_file.name,
            file_type=Path(uploaded_file.name).suffix.lower(),
            mime_type=getattr(uploaded_file, "content_type", ""),
            file_size=uploaded_file.size,
            checksum=checksum,
            status=Document.Status.UPLOADED,
        )
        async_task("apps.documents.tasks.process_document", document.document_uuid)
        return document

    @staticmethod
    def list_documents():

        return Document.objects.all()

    @staticmethod
    def delete_document(document_uuid):
        with transaction.atomic():
            document = (Document.objects.select_for_update().get(document_uuid=document_uuid))
            stored_file = document.file

            # Related chunks, pages, citations, and message sources are removed
            # by their database cascade rules.
            document.delete()

            # Rebuild from the remaining chunks. This physically removes the
            # deleted document's vectors and rewrites all FAISS mappings.
            IndexBuilder().build()

        # Django's FileField does not remove the underlying file when its model
        # row is deleted, so clean it up explicitly after the transaction.
        if stored_file and stored_file.name:
            try:
                stored_file.delete(save=False)
            except Exception:
                logger.exception(
                    "Document record was deleted but its stored file could not be removed: %s",
                    stored_file.name
                )
