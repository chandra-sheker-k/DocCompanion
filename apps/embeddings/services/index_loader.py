
import faiss
from pathlib import Path

class IndexLoader:
    INDEX = Path("data/faiss/document.index")
    def load(self):
        if not self.INDEX.exists():
            return None
        return faiss.read_index(str(self.INDEX))