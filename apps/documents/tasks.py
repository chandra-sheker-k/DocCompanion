
from apps.documents.models import Document
from apps.documents.document_service import DocumentService

def process_document(document_uuid):
    document = Document.objects.filter(document_uuid=document_uuid).first()

    # A user can delete an uploaded document before its queued processing task
    # starts. In that case the task should exit quietly and must not recreate it.
    if document is None:
        return None

    return DocumentService.process(document)
