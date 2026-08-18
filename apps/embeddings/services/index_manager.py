
import faiss
from threading import Lock
from pathlib import Path

from apps.embeddings.services.index_loader import IndexLoader

class IndexManager:
    # Singleton manager for the FAISS index.
    # Loads the index once and shares it across the application.

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._faiss = None
        return cls._instance

    @property
    def faiss(self):
        if self._faiss is None:
            self._faiss = IndexLoader().load()
        return self._faiss

    def reload(self):
        # Reload index from disk.
        self._faiss = IndexLoader().load()

    def save(self):
        # Save current index.
        if self._faiss is not None:
            index_path = Path("data/faiss/document.index")
            index_path.parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self._faiss, str(index_path))

    def clear(self):
        # Reset manager.
        self._faiss = None

    def replace(self, index):
        """Replace the in-memory index after an atomic rebuild."""
        self._faiss = index

    @staticmethod
    def load(path):
        return faiss.read_index(path)
