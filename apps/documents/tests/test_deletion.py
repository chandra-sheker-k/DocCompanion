from contextlib import nullcontext
from unittest.mock import Mock, patch
from uuid import uuid4

from django.test import SimpleTestCase

from apps.documents.document_service import DocumentService
from apps.embeddings.services.index_builder import IndexBuilder


class DocumentDeletionTests(SimpleTestCase):
    @patch("apps.documents.document_service.transaction.atomic")
    @patch("apps.documents.document_service.IndexBuilder")
    @patch("apps.documents.document_service.Document.objects.select_for_update")
    def test_delete_removes_record_file_and_rebuilds_index(
        self,
        select_for_update,
        index_builder,
        atomic,
    ):
        atomic.return_value = nullcontext()
        stored_file = Mock(name="stored_file")
        stored_file.name = "documents/example.pdf"
        document = Mock(file=stored_file)
        locked_documents = select_for_update.return_value
        locked_documents.get.return_value = document
        document_uuid = uuid4()

        DocumentService.delete_document(document_uuid)

        select_for_update.assert_called_once_with()
        locked_documents.get.assert_called_once_with(document_uuid=document_uuid)
        document.delete.assert_called_once_with()
        index_builder.return_value.build.assert_called_once_with()
        stored_file.delete.assert_called_once_with(save=False)


class EmptyIndexRebuildTests(SimpleTestCase):
    @patch("apps.embeddings.services.index_builder.os.replace")
    @patch("apps.embeddings.services.index_builder.faiss.write_index")
    @patch("apps.embeddings.services.index_builder.IndexManager")
    @patch("apps.embeddings.services.index_builder.DocumentChunk.objects.filter")
    @patch("apps.embeddings.services.index_builder.DocumentChunk.objects.all")
    def test_rebuild_saves_empty_index_after_last_document_is_deleted(
        self,
        all_chunks,
        filter_chunks,
        index_manager,
        write_index,
        replace_file,
    ):
        all_chunks.return_value.order_by.return_value = []
        stale_mappings = Mock()
        filter_chunks.return_value = stale_mappings

        vector_count = IndexBuilder().build()

        self.assertEqual(vector_count, 0)
        all_chunks.assert_called_once_with()
        filter_chunks.assert_called_once_with(faiss_index__isnull=False)
        stale_mappings.update.assert_called_once_with(
            faiss_index=None,
            is_indexed=False,
        )
        write_index.assert_called_once()
        replace_file.assert_called_once()
        index_manager.return_value.replace.assert_called_once()
