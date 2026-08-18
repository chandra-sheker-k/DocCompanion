
from django.db import connection
from django.http import JsonResponse

from apps.documents.models import Document, DocumentChunk
from apps.embeddings.services.index_manager import IndexManager
from apps.llm.model_manager import ModelManager

def health(request):
    data = {"status": "healthy"}

    # Database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        data["database"] = "ok"
    except Exception as exc:
        data["database"] = str(exc)
        data["status"] = "unhealthy"

    # FAISS
    try:
        index = IndexManager().faiss
        data["faiss"] = "ok"
        data["index_vectors"] = index.ntotal
    except Exception as exc:
        data["faiss"] = str(exc)
        data["status"] = "unhealthy"

    # LLM
    try:
        model = ModelManager()
        data["llm"] = "ok"
        data["model"] = model.model_name
    except Exception as exc:
        data["llm"] = str(exc)
        data["status"] = "unhealthy"

    # Statistics
    data["documents"] = Document.objects.count()
    data["chunks"] = DocumentChunk.objects.count()
    data["version"] = "1.0.0"
    return JsonResponse(data)