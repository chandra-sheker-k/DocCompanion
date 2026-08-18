
import faiss
import numpy as np
from pathlib import Path

class FaissService:
    def __init__(self, dimension=768,):
        self.index = faiss.IndexFlatIP(dimension)
        self.index_path = Path("data/faiss/document.index")

    def add(self, vectors):
        vectors = np.asarray(vectors, dtype="float32")
        self.index.add(vectors)

    def search(self, vector, k=5):
        vector = np.asarray([vector], dtype="float32")
        scores, ids = self.index.search(vector, k)
        return scores, ids

    def save(self):
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))