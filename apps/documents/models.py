
import uuid
from uuid import uuid4
from django.db import models

class Document(models.Model):
    class Status(models.TextChoices):
        UPLOADED = "uploaded", "Uploaded"
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    document_uuid = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    file = models.FileField(upload_to="documents/%Y/%m/%d/")
    name = models.CharField(max_length=255, null=True, blank=True)
    original_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20)
    mime_type = models.CharField(max_length=100, blank=True)
    file_size = models.BigIntegerField()
    checksum = models.CharField(max_length=64, unique=True)
    chunk_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPLOADED)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=300, blank=True)
    author = models.CharField(max_length=200, blank=True)
    language = models.CharField(max_length=20, default="unknown")
    page_count = models.PositiveIntegerField(default=0)
    extracted_text = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    processing_time_ms = models.PositiveIntegerField(default=0)
    extraction_version = models.CharField(max_length=20, default="1.0")
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    embedding_model = models.CharField(max_length=100, blank=True)
    indexed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["uploaded_at"]),
            models.Index(fields=["checksum"])
        ]

    def __str__(self):
        return self.original_name

class DocumentChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    chunk_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    chunk_index = models.PositiveIntegerField()
    page_number = models.PositiveIntegerField(default=1)
    section_title = models.CharField(max_length=255, blank=True)
    text = models.TextField()
    character_count = models.PositiveIntegerField()
    word_count = models.PositiveIntegerField()
    token_count = models.PositiveIntegerField()
    start_char = models.PositiveIntegerField()
    end_char = models.PositiveIntegerField()
    embedding_dimension = models.PositiveIntegerField(default=768)
    embedding_model = models.CharField(max_length=100, default="bge-base-en-v1.5")
    embedding = models.BinaryField(null=True, blank=True)
    faiss_index = models.PositiveIntegerField(null=True, blank=True, unique=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_indexed = models.BooleanField(default=False)
    indexed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    retrieval_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["document", "chunk_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["document", "chunk_index"],
                name="unique_chunk_per_document"
            )
        ]
        unique_together = ("document", "chunk_index")
        indexes = [
            models.Index(
                fields=["document", "page_number"]
            ),
            models.Index(
                fields=["is_indexed"]
            ),
        ]

    def __str__(self):
        return f"{self.document.original_name} " f"Chunk {self.chunk_index}"

class DocumentPage(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="pages")
    page_number = models.PositiveIntegerField()
    text = models.TextField()
    character_count = models.PositiveIntegerField()
    word_count = models.PositiveIntegerField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["document", "page_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["document", "page_number"],
                name="unique_document_page",
            )
        ]
        indexes = [
            models.Index(
                fields=["document", "page_number"]
            ),
        ]
    def __str__(self):
        return f"{self.document.original_name} - Page {self.page_number}"
'''
class UploadedDocument(models.Model):
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/")
    extension = models.CharField(max_length=20)
    title = models.CharField(max_length=500, blank=True)
    author = models.CharField(max_length=200, blank=True)
    language = models.CharField(max_length=20, blank=True)
    total_pages = models.IntegerField(default=0)
    status = models.CharField(max_length=30, default="UPLOADED")
    created_at = models.DateTimeField(auto_now_add=True)
'''