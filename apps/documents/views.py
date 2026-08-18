
import os
from datetime import timezone

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt

from .document_service import DocumentService
# from .services.extractor import extract_text
#from .forms import UploadDocumentForm
from .models import Document
#from .services.storage import calculate_checksum
#from .services.cleaner import TextCleaner
#from .services.chunker import TextChunker
#from .services.chunk_storage import save_chunks

@require_GET
def list_documents(request):
    # Return all indexed documents.

    documents = DocumentService.list_documents()
    data = [
        {
            "id": str(document.document_uuid),
            "name": document.name,
            "file_type": document.file_type,
            "status": document.status,
            "pages": document.page_count,
            "chunks": document.chunk_count,
            "created_at": document.created_at.isoformat(),
        }
        for document in documents
    ]

    return JsonResponse(data, safe=False)

@require_POST
@csrf_exempt
def upload_document(request):
    # Upload one or more files.

    files = request.FILES.getlist("documents")
    if not files:
        return JsonResponse({"error": "No files uploaded."}, status=400)
    uploaded = []
    for uploaded_file in files:
        document = DocumentService.ingest_document(uploaded_file)

        uploaded.append(
            {
                "id": str(document.document_uuid),
                "name": document.name,
                "status": document.status,
            }
        )

    return JsonResponse({ "success": True, "documents": uploaded})

@require_http_methods(["DELETE"])
@csrf_exempt
def delete_document(request, document_uuid):
    # Delete document and its index.

    try:
        DocumentService.delete_document(document_uuid)
    except Document.DoesNotExist as exc:
        raise Http404("Document not found.") from exc

    return JsonResponse({"success": True})

def document_status(request, document_uuid):
    document = Document.objects.get(document_uuid=document_uuid)
    return JsonResponse({"status": document.status, "chunks": document.chunk_count})
