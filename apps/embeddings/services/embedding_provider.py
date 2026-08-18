
from sentence_transformers import SentenceTransformer

class EmbeddingProvider:
    _model = None

    def __init__(self):
        self.model = self.get_model()

    @classmethod
    def get_model(cls):
        if cls._model is None:
            from sentence_transformers import SentenceTransformer
            cls._model = SentenceTransformer(
                "BAAI/bge-base-en-v1.5"
            )
        return cls._model
    def encode(self, text):
        return self.model.encode(text, normalize_embeddings=True)
