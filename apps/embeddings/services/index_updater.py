
import faiss
import numpy as np

class IndexUpdater:
    def add_vector(self, index, vector):
        vector = np.asarray([vector], dtype=np.float32)
        index.add(vector)