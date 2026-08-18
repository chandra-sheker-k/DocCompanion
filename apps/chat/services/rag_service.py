
"""
RAG Service

Responsibilities

1. Retrieve relevant chunks
2. Build prompt
3. Call LLM
4. Return answer + citations
"""

from __future__ import annotations

import logging
import time
from typing import Any

from apps.embeddings.services.search_service import SearchService
from apps.chat.models import ChatMessage, Citation, MessageSource
from apps.chat.services.citations import group_citation_locations
from apps.core.exceptions import DocCompanionError
from apps.llm.model_manager import ModelManager
from apps.chat.models import ChatMetrics

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.search = SearchService()
        self.model = None

    def _model_for(self, conversation):
        """Use the conversation snapshot when it names an installed model.

        Older conversations may contain the historical qwen3:8b default, while
        this project is configured for qwen2.5:7b. The application-level model
        therefore remains the reliable default unless a different model was
        explicitly saved in settings.
        """
        configured_model = getattr(conversation.settings, "llm_model", "")
        default_manager = ModelManager()

        if configured_model and configured_model != "qwen3:8b":
            return ModelManager(model=configured_model)

        return default_manager

    # Public
    def answer(self, *, question: str, conversation, user_message: ChatMessage
               , top_k: int | None = None) -> dict[str, Any]:
        try:
            model = self._model_for(conversation)
            start = time.perf_counter()
            total_start = time.perf_counter()

            # Conversation settings snapshot
            settings = conversation.settings

            retrieval_start = time.perf_counter()
            # Retrieve chunks
            chunks = self.search.search(question, k=top_k or settings.top_k)
            retrieval_time = int(
                (time.perf_counter() - retrieval_start) * 1000
            )
            # Build context
            context = self._build_context(chunks)

            # Build prompt
            prompt_start = time.perf_counter()
            prompt = self._build_prompt(
                context=context,
                question=question,
                system_prompt=conversation.system_prompt,
            )
            prompt_build_time = int(
                (time.perf_counter() - prompt_start) * 1000
            )

            # Call LLM
            llm_start = time.perf_counter()
            answer = model.generate(
                prompt=prompt,
                max_tokens=min(settings.max_tokens, 512),  # Limit to 512 tokens for speed
                temperature=min(settings.temperature, 0.1),  # Lower temperature for faster, more deterministic responses
            )
            llm_time = int((time.perf_counter() - llm_start) * 1000)

            elapsed = int((time.perf_counter() - start) * 1000)

            # Save assistant message
            assistant = ChatMessage.objects.create(
                conversation=conversation,
                role=ChatMessage.Role.ASSISTANT,
                content=answer,
                response_time_ms=elapsed,
            )

            # Save citations
            citations = self._save_sources(assistant, chunks)
            total_time = int((time.perf_counter() - total_start) * 1000)
            ChatMetrics.objects.create(
                message=assistant,
                retrieval_time_ms=retrieval_time,
                prompt_build_time_ms=prompt_build_time,
                llm_time_ms=llm_time,
                total_time_ms=total_time,
                retrieved_chunks=len(chunks),
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(answer.split()),
                total_tokens=(len(prompt.split()) + len(answer.split()))
            )
            return {"message": assistant, "answer": answer, "sources": chunks,
                "citations": citations, "elapsed_ms": elapsed, "elapsed_ms": total_time,
                    "metrics": {"retrieval_ms": retrieval_time, "prompt_ms": prompt_build_time,
                                "llm_ms": llm_time, "total_ms": total_time}}
        except DocCompanionError:
            raise
        except Exception as exc:
            logger.error(f"Error in RAGService.answer: {str(exc)}")
            raise DocCompanionError(str(exc)) from exc
    # -----------------------------------------------------

    def _build_context(self, chunks):
        return "\n\n".join(chunk.text for chunk in chunks)
    # -----------------------------------------------------

    def _build_prompt(self, *, context, question, system_prompt):
        # Use a stronger system prompt if the conversation doesn't have one
        if not system_prompt or system_prompt.strip() == "":
            system_prompt = """You are an AI Document Assistant.

Answer ONLY using the supplied document context.
Do NOT use any external knowledge, internet, or information from your training data.
If the answer cannot be found in the uploaded documents, reply:
'I couldn't find that information in the uploaded documents.'
Be concise and direct."""

        return f"""{system_prompt}

Context from uploaded documents:
{context}

Question: {question}

Answer based ONLY on the above context:"""

    # -----------------------------------------------------
    def _call_llm(self, prompt):

        #
        # Phase 5.5
        #
        return (
            "LLM integration "
            "will be connected "
            "in Phase 5.5."
        )

    # -----------------------------------------------------

    def _save_sources(self, assistant_message, chunks):
        citation_locations = []
        cited_pages = set()

        for chunk in chunks:
            # Save source
            MessageSource.objects.create(
                message=assistant_message,
                document=chunk.document,
                chunk_index=chunk.chunk_index,
                score=chunk.score,
                page=chunk.page_number
            )

            page_key = (chunk.document_id, chunk.page_number)
            if page_key in cited_pages:
                continue

            cited_pages.add(page_key)
            Citation.objects.create(
                chat_message=assistant_message,
                document=chunk.document,
                chunk=chunk,
                similarity_score=chunk.score,
                quoted_text=chunk.text[:300],
                order=len(citation_locations),
            )
            citation_locations.append({
                "document_id": chunk.document_id,
                "document": chunk.document.original_name or chunk.document.name,
                "page": chunk.page_number,
                "score": chunk.score,
            })

        return group_citation_locations(citation_locations)
    # -----------------------------------------------------
    def _save_citations(self, assistant_message, chunks):
        for chunk in chunks:
            Citation.objects.create(
                message=assistant_message,
                document=chunk.document,
                chunk=chunk,
                page_number=chunk.metadata.get("page", 1),
                snippet=chunk.text[:300]
            )

    def stream(self, *, question, conversation, user_message):
        try:
            settings = conversation.settings
            model = self._model_for(conversation)
            chunks = self.search.search(question, k=settings.top_k)
            context = self._build_context(chunks)
            prompt = self._build_prompt(context=context, question=question
                                        , system_prompt=conversation.system_prompt)

            answer = ""
            for token in model.stream(prompt=prompt, max_tokens=min(settings.max_tokens, 512)
                    , temperature=min(settings.temperature, 0.1)):
                answer += token
                yield token

            assistant = ChatMessage.objects.create(
                conversation=conversation,
                role=ChatMessage.Role.ASSISTANT,
                content=answer
            )
            self._save_sources(assistant, chunks)
        except DocCompanionError:
            raise
        except Exception as exc:
            logger.error(f"Error in RAGService.answer: {str(exc)}")
            raise DocCompanionError(str(exc)) from exc
