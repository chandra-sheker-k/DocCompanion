
from apps.documents.models import DocumentChunk
import numpy as np

from .embedding_provider import EmbeddingProvider
from .faiss_service import FaissService
from apps.embeddings.services.index_manager import IndexManager

class EmbeddingService:
    def __init__(self):
        self.embedding = EmbeddingProvider()
        # self.faiss = FaissService()
        self.faiss = IndexManager().faiss

    def build_index(self):
        vectors = []
        for chunk in DocumentChunk.objects.all():
            vector = self.embedding.encode(chunk.text)
            vectors.append(vector)
        self.faiss.add(vectors)

    def index_document(self, document):
        #Incrementally index a single document.

        manager = IndexManager()
        faiss = manager.faiss
        if faiss is None:
            from apps.embeddings.services.faiss_service import FaissService

            faiss_service = FaissService()
            faiss = faiss_service.index
            faiss_service.save()

            manager._faiss = faiss

        chunks = (
            DocumentChunk.objects
            .filter(document=document, is_indexed=False)
            .order_by("chunk_index")
        )

        if not chunks.exists():
            return 0

        vectors = []

        for chunk in chunks:
            vector = np.asarray(self.embedding.encode(chunk.text), dtype=np.float32)
            vectors.append(vector)
            chunk.embedding = vector.tobytes()
            chunk.embedding_dimension = vector.shape[0]

        # Current FAISS size
        start_index = faiss.ntotal

        # Add vectors
        faiss.add(np.asarray(vectors, dtype="float32"))
        manager.save()

        # Save mapping
        for i, chunk in enumerate(chunks):
            chunk.faiss_index = start_index + i
            chunk.is_indexed = True

        DocumentChunk.objects.bulk_update(
            chunks,
            [
                "embedding",
                "embedding_dimension",
                "faiss_index",
                "is_indexed"
            ],
        )

        IndexManager().save()
        return len(chunks)
