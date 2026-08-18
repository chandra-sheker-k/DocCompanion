
import uuid
from uuid import uuid4
from django.db import models

from apps.documents.models import Document, DocumentChunk

class Conversation(models.Model):
    # One chat session.
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    conversation_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255, blank=True)
    system_prompt = models.TextField(blank=True)
    llm_model = models.CharField(max_length=100, default="qwen3:8b")
    embedding_model = models.CharField(max_length=100, default="bge-base-en-v1.5")
    temperature = models.FloatField(default=0.2)
    top_k = models.PositiveIntegerField(default=5)
    metadata = models.JSONField(default=dict, blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
    def __str__(self):
        return self.title or str(self.conversation_uuid)

class ChatMessage(models.Model):
    """
    Stores every user/assistant message.
    """

    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"
        SYSTEM = "system", "System"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    message_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField()
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    response_time_ms = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    latency_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=["conversation", "created_at"]
            ),
        ]
    def __str__(self):
        return f"{self.role}"


class Citation(models.Model):
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="citations")
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    chunk = models.ForeignKey(DocumentChunk, on_delete=models.CASCADE)
    #page_number = models.PositiveIntegerField()
    similarity_score = models.FloatField()
    quoted_text = models.TextField()
    order = models.PositiveIntegerField()
    class Meta:
        ordering = ["order"]
        indexes = [
            models.Index(
                fields=["chat_message"]
            ),
            models.Index(
                fields=["document"]
            ),
        ]

class PromptHistory(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="prompt_history", on_delete=models.CASCADE)
    user_question = models.TextField()
    final_prompt = models.TextField()
    retrieved_context = models.TextField()
    llm_response = models.TextField()
    model_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class MessageSource(models.Model):
    # Stores which document chunks
    # were used to answer a message.

    message = models.ForeignKey(ChatMessage, related_name="sources", on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    chunk_index = models.IntegerField()
    score = models.FloatField()
    page = models.IntegerField(default=0)

    class Meta:
        ordering = ["-score"]

    def __str__(self):
        return self.document.name

class ConversationSettings(models.Model):
    conversation = models.OneToOneField(Conversation, related_name="settings", on_delete=models.CASCADE)
    llm_model = models.CharField(max_length=100)
    embedding_model = models.CharField(max_length=100)
    temperature = models.FloatField(default=0.2)
    top_k = models.IntegerField(default=5)
    top_p = models.FloatField(default=0.95)
    max_tokens = models.IntegerField(default=1024)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMetrics(models.Model):
    message = models.OneToOneField(ChatMessage, on_delete=models.CASCADE, related_name="metrics")
    retrieval_time_ms = models.PositiveIntegerField(default=0)
    prompt_build_time_ms = models.PositiveIntegerField(default=0)
    llm_time_ms = models.PositiveIntegerField(default=0)
    total_time_ms = models.PositiveIntegerField(default=0)
    retrieved_chunks = models.PositiveIntegerField(default=0)
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)