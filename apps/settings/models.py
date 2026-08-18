
import uuid
from django.db.models import Q

from django.db import models

class AgentSettings(models.Model):
    # Global configuration for the AI Document Assistant.
    # Usually only one active record exists.

    settings_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, default="Default Configuration")
    is_active = models.BooleanField(default=True)

    # LLM
    llm_provider = models.CharField(max_length=50, default="ollama")
    llm_model = models.CharField(max_length=100, default="qwen3:8b")
    temperature = models.FloatField(default=0.2)
    top_p = models.FloatField(default=0.95)
    max_output_tokens = models.PositiveIntegerField(default=2048)
    context_window = models.PositiveIntegerField(default=8192)

    # Embeddings
    embedding_model = models.CharField(max_length=100, default="BAAI/bge-base-en-v1.5")
    embedding_dimension = models.PositiveIntegerField(default=768)
    normalize_embeddings = models.BooleanField(default=True)

    # Chunking
    chunk_size = models.PositiveIntegerField(default=400)
    chunk_overlap = models.PositiveIntegerField(default=80)
    preserve_paragraphs = models.BooleanField(default=True)
    preserve_sentences = models.BooleanField(default=True)

    # Retrieval
    top_k = models.PositiveIntegerField(default=5)
    similarity_threshold = models.FloatField(default=0.65)
    enable_reranker = models.BooleanField(default=False)
    reranker_model = models.CharField(max_length=100, blank=True)
    hybrid_search = models.BooleanField(default=False)

    # OCR
    enable_ocr = models.BooleanField(default=True)
    ocr_language = models.CharField(max_length=20, default="eng")

    # Response
    stream_response = models.BooleanField(default=True)
    show_sources = models.BooleanField(default=True)
    show_similarity_score = models.BooleanField(default=False)
    system_prompt = models.TextField(
        default="""
You are an AI Document Assistant.

Answer ONLY using the supplied document context.

If the answer cannot be found in the uploaded documents,
reply:

'I couldn't find that information in the uploaded documents.'

Do not use your own knowledge.
""".strip(),
    )

    # Logging
    save_chat_history = models.BooleanField(default=True)
    save_prompts = models.BooleanField(default=True)
    enable_metrics = models.BooleanField(default=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Agent Settings"
        verbose_name_plural = "Agent Settings"
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=Q(is_active=True),
                name="single_active_agent_settings"
            )
        ]
    def __str__(self):
        return self.name