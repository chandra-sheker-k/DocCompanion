
import faiss
import numpy as np
import os
from pathlib import Path

from apps.documents.models import DocumentChunk
from apps.embeddings.services.embedding_provider import EmbeddingProvider
from apps.embeddings.services.index_manager import IndexManager

class IndexBuilder:

    DIMENSION = 768

    def build(self):
        index = faiss.IndexFlatIP(self.DIMENSION)
        chunks = list(
            DocumentChunk.objects
            .all()
            .order_by("document_id", "chunk_index")
        )

        vectors = []
        embedding_provider = None

        for position, chunk in enumerate(chunks):
            if chunk.embedding:
                vector = np.frombuffer(chunk.embedding, dtype=np.float32)
            else:
                if embedding_provider is None:
                    embedding_provider = EmbeddingProvider()
                vector = np.asarray(embedding_provider.encode(chunk.text),dtype=np.float32)
                chunk.embedding = vector.tobytes()
                chunk.embedding_dimension = vector.shape[0]

            if vector.shape[0] != self.DIMENSION:
                raise ValueError(
                    f"Chunk {chunk.pk} has embedding dimension "
                    f"{vector.shape[0]}; expected {self.DIMENSION}."
                )

            vectors.append(vector)

            chunk.faiss_index = position
            chunk.is_indexed = True

        # Clear the old mapping only after every vector has been prepared.
        # Renumbering rows one at a time can otherwise violate the unique
        # constraint on faiss_index.
        DocumentChunk.objects.filter(faiss_index__isnull=False).update(faiss_index=None,is_indexed=False)

        if chunks:
            DocumentChunk.objects.bulk_update(
                chunks,
                [
                    "embedding",
                    "embedding_dimension",
                    "faiss_index",
                    "is_indexed",
                ],
            )

        if vectors:
            index.add(np.vstack(vectors))

        index_path = Path("data/faiss/document.index")
        temporary_path = index_path.with_suffix(".index.tmp")
        index_path.parent.mkdir(parents=True, exist_ok=True)

        # Replace the index atomically so searches never observe a partially
        # written file. An empty index is intentionally saved when the last
        # document is deleted.
        faiss.write_index(index, str(temporary_path))
        os.replace(temporary_path, index_path)

        IndexManager().replace(index)

        return index.ntotal
