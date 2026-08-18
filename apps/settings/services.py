
from django.db import OperationalError, ProgrammingError

from apps.settings.models import AgentSettings

class SettingsService:

    @staticmethod
    def get():
        try:
            settings = AgentSettings.objects.filter(is_active=True).first()

            if settings:
                return settings
        except (OperationalError, ProgrammingError):
            # Database/table doesn't exist yet (during makemigrations/migrate)
            pass
        return AgentSettings(
            llm_provider="ollama",
            llm_model="qwen3:8b",
            temperature=0.2,
            top_p=0.95,
            max_output_tokens=2048,
            context_window=8192,

            embedding_model="BAAI/bge-base-en-v1.5",
            embedding_dimension=768,
            normalize_embeddings=True,

            chunk_size=400,
            chunk_overlap=80,
            preserve_paragraphs=True,
            preserve_sentences=True,

            top_k=5,
            similarity_threshold=0.65,
            enable_reranker=False,
            hybrid_search=False,

            enable_ocr=True,
            ocr_language="eng",

            stream_response=True,
            show_sources=True,
            show_similarity_score=False,

            save_chat_history=True,
            save_prompts=True,
            enable_metrics=True,

            is_active=True,
        )