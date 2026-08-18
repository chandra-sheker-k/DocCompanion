
"""
Chat business logic.

Handles:

- Conversation lifecycle
- Message persistence
- Conversation history
- Auto title generation

RAG inference is added in Part 2.
"""

from __future__ import annotations

import logging
import re
from typing import Optional
from uuid import UUID
from django.db import transaction
from django.db.models import QuerySet

from apps.chat.models import Conversation, ChatMessage, ConversationSettings
from apps.chat.services.citations import group_citation_locations
from apps.chat.services.rag_service import RAGService
from apps.core.exceptions import DocCompanionError, ModelUnavailableError
from apps.settings.services import SettingsService

logger = logging.getLogger(__name__)

class ChatService:
    #def __init__(self):
    #    rag = RAGService()
    # Conversation

    @staticmethod
    def create_conversation(title: str = "New Chat", *, system_prompt: str = "", llm_model: str = "qwen3:8b"
                            , embedding_model: str = "BAAI/bge-base-en-v1.5") -> Conversation:
        with transaction.atomic():
            conversation = Conversation.objects.create(title=title, system_prompt=system_prompt
                                                       , llm_model=llm_model, embedding_model=embedding_model)
        try:
            print("Conversation created:", conversation.pk)
            ChatService._create_settings_snapshot(conversation)
        except Exception as exc:
            logger.exception("Unable to create settings snapshot: %s", exc)
        logger.info("Conversation created %s", conversation.conversation_uuid)
        return conversation
    # ---------------------------------------------------------

    @staticmethod
    def get_conversation(conversation_uuid: UUID) -> Conversation:
        return Conversation.objects.get( conversation_uuid=conversation_uuid
                                         , is_archived=False)
    # ---------------------------------------------------------

    @staticmethod
    def list_conversations() -> QuerySet[Conversation]:

        return Conversation.objects.filter(is_archived=False).order_by("-updated_at")
    # ---------------------------------------------------------
    # Messages

    @staticmethod
    @transaction.atomic
    def add_user_message(conversation: Conversation, content: str) -> ChatMessage:
        message = ChatMessage.objects.create( conversation=conversation
                                              , role=ChatMessage.Role.USER
                                              , content=content)

        #ChatService._update_title(conversation, content)
        conversation.save(update_fields=["updated_at"])
        return message
    # ---------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def add_assistant_message(conversation: Conversation, content: str, *
                              , prompt_tokens: int = 0, completion_tokens: int = 0
                              , total_tokens: int = 0, latency_ms: int = 0
                              , metadata: Optional[dict] = None) -> ChatMessage:

        message = ChatMessage.objects.create(
            conversation=conversation,
            role=ChatMessage.Role.ASSISTANT,
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            metadata=metadata or {}
        )

        conversation.save(update_fields=["updated_at"])

        return message
    # ---------------------------------------------------------

    @staticmethod
    def get_messages(conversation: Conversation) -> QuerySet[ChatMessage]:

        return (ChatMessage.objects.filter(conversation=conversation)
                .prefetch_related("citations__document", "citations__chunk")
                .order_by("created_at"))
    # ---------------------------------------------------------
    # Serialization

    @staticmethod
    def serialize_conversation(conversation: Conversation) -> dict:
        return {
            "id": str(conversation.conversation_uuid),
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "llm_model": conversation.llm_model
        }
    # ---------------------------------------------------------

    @staticmethod
    def serialize_message(message: ChatMessage) -> dict:
        citations = group_citation_locations([
            {
                "document_id": citation.document_id,
                "document": (
                    citation.document.original_name or citation.document.name
                ),
                "page": citation.chunk.page_number,
                "score": citation.similarity_score,
            }
            for citation in message.citations.all()
        ])

        return {
            "id": str(message.message_uuid),
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at.isoformat(),
            "prompt_tokens": message.prompt_tokens,
            "completion_tokens": message.completion_tokens,
            "total_tokens": message.total_tokens,
            "citations": citations,
        }
    # ---------------------------------------------------------
    # Private

    @staticmethod
    def send_message(*, prompt, conversation_uuid=None):
        # 1
        if conversation_uuid:
            conversation = ChatService.get_conversation(conversation_uuid)
        else:
            conversation = ChatService.create_conversation()

        # 2
        user_message = ChatService.add_user_message(conversation, prompt)

        # 3
        rag = RAGService()

        # 4
        try:
            result = rag.answer(question=prompt, conversation=conversation
                                , user_message=user_message)
            print(result["metrics"])
            ChatService._update_title(conversation, prompt)

            # 5
            return {
                "conversation_id": str(conversation.conversation_uuid),
                "answer": result["answer"],
                "citations": result["citations"],
                "elapsed_ms": result["elapsed_ms"]
            }
        except DocCompanionError as exc:
            return {
                "success": False,
                "error": {"code": exc.code, "message": exc.message}
            }

    @staticmethod
    def stream_message(*, prompt, conversation_uuid):
        if conversation_uuid:
            conversation = ChatService.get_conversation(conversation_uuid)
        else:
            conversation = ChatService.create_conversation()
        user_message = ChatService.add_user_message(conversation, prompt)
        ChatService._update_title(conversation, prompt)
        rag = RAGService()
        streamed_response = False

        try:
            for token in rag.stream(question=prompt,conversation=conversation,user_message=user_message):
                streamed_response = True
                yield token
        except ModelUnavailableError as exc:
            logger.warning("Local model unavailable for conversation %s: %s",
                conversation.conversation_uuid, exc.message
            )
            error_message = f"⚠️ {exc.message}"

            ChatService.add_assistant_message(conversation, error_message,metadata={"error_code": exc.code})

            if streamed_response:
                yield "\n\n"
            yield error_message

    # ---------------------------------------------------------
    @staticmethod
    def _update_title(conversation: Conversation, first_prompt: str) -> None:
        """Set a concise prompt-based title only once."""

        # Already titled
        if conversation.title and conversation.title != "New Chat":
            return

        title = ChatService._generate_title(first_prompt)
        conversation.title = title
        conversation.save(update_fields=["title"])

    # ---------------------------------------------------------
    @staticmethod
    def _generate_title(question: str) -> str:
        """Create a fast, predictable title directly from the first prompt."""
        title = " ".join(question.strip().split())
        title = re.sub(
            r"^(?:please\s+)?(?:can|could|would)\s+you\s+",
            "",
            title,
            flags=re.IGNORECASE,
        )
        title = re.sub(
            r"^(?:please\s+)?(?:tell\s+me\s+about|explain|describe|summarize)\s+",
            "",
            title,
            flags=re.IGNORECASE,
        )
        title = re.sub(
            r"^(?:what|who|where|when|why|how)\s+(?:is|are|was|were|do|does|did|can)\s+",
            "",
            title,
            flags=re.IGNORECASE,
        )
        title = title.strip(" \t\n\r?.!,;:-\"'")

        words = title.split()
        if len(words) > 7:
            title = " ".join(words[:7]).rstrip(".,;:-") + "…"

        title = title[:80].rstrip()
        if len(title.split()) == 1 and title.isalpha() and len(title) <= 5:
            title = title.upper()

        return title or "New Chat"

    @staticmethod
    def _create_settings_snapshot(conversation):
        # Copy the current global AI settings into this conversation.
        settings = SettingsService.get()
        try:
            ConversationSettings.objects.create(
                conversation=conversation,
                llm_model=settings.llm_model,
                embedding_model=settings.embedding_model,
                temperature=settings.temperature,
                top_k=settings.top_k,
                top_p=settings.top_p,
                max_tokens=getattr(settings, 'max_output_tokens', 1024)
            )
        except Exception:
            import traceback
            traceback.print_exc()
            raise
