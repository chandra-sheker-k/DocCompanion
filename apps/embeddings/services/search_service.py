
import re
import numpy as np
from django.db.models import Q

from apps.documents.models import DocumentChunk
from .embedding_provider import EmbeddingProvider
from .index_loader import IndexLoader
from apps.embeddings.services.index_manager import IndexManager
from apps.core.exceptions import NoDocumentsError, NoSearchResultsError

class SearchService:
    KEYWORD_STOP_WORDS = frozenset({
        "a", "about", "an", "and", "are", "as", "at", "be", "between",
        "can", "compare", "define", "difference", "do", "does", "explain",
        "for", "from", "give", "how", "i", "in", "is", "it", "me", "of",
        "on", "or", "please", "should", "summarize", "tell", "the", "to",
        "use", "versus", "vs", "what", "when", "where", "which", "with",
    })

    def __init__(self):
        self.embedding = EmbeddingProvider()
        #self.index = IndexLoader().load()
        self.faiss = IndexManager().faiss
        if self.faiss is None:
            raise RuntimeError(
                "No search index found. Upload and index at least one document first."
            )

    def search(self, query, k=5):
        vector = self.embedding.encode(query)
        searchable_chunks = DocumentChunk.objects.filter(
            document__status="ready",
            is_indexed=True,
            faiss_index__isnull=False,
        )

        if not searchable_chunks.exists():
            raise NoDocumentsError("No documents have been indexed.")

        keyword_chunks = self._keyword_search(searchable_chunks, query, k)

        scores, ids = self.faiss.search(
            np.asarray([vector], dtype=np.float32),
            k
        )
        if len(ids[0]) == 0:
            raise NoSearchResultsError("No relevant documents found.")
        '''
        chunks = []
        for idx in ids[0]:
            if idx == -1:
                continue

            chunk = DocumentChunk.objects.get(faiss_index=idx)
            chunks.append(chunk)
        '''
        result_pairs = [
            (int(index_id), float(score))
            for index_id, score in zip(ids[0], scores[0])
            if index_id != -1
        ]
        result_ids = [index_id for index_id, _ in result_pairs]
        chunk_map = {
            c.faiss_index: c
            for c in searchable_chunks.filter(faiss_index__in=result_ids)
        }

        semantic_chunks = []
        for index_id, score in result_pairs:
            chunk = chunk_map.get(index_id)
            if chunk is not None:
                chunk.score = score
                semantic_chunks.append(chunk)

        # Exact terms are especially important for acronyms, identifiers, and
        # product names. Merge them ahead of semantic results, without returning
        # the same chunk twice.
        chunks = []
        seen_chunk_ids = set()
        for chunk in [*keyword_chunks, *semantic_chunks]:
            if chunk.pk in seen_chunk_ids:
                continue
            seen_chunk_ids.add(chunk.pk)
            chunks.append(chunk)
            if len(chunks) == k:
                break

        if not chunks:
            raise NoSearchResultsError("No relevant documents found.")

        return chunks

    @classmethod
    def _keyword_terms(cls, query):
        terms = re.findall(r"[a-z0-9][a-z0-9_+.#-]*", query.casefold())
        meaningful_terms = [
            term
            for term in terms
            if len(term) > 1 and term not in cls.KEYWORD_STOP_WORDS
        ]
        # Preserve order and keep the database query bounded.
        return list(dict.fromkeys(meaningful_terms))[:8]

    @classmethod
    def _keyword_search(cls, searchable_chunks, query, k):
        terms = cls._keyword_terms(query)
        if not terms:
            return []

        keyword_filter = Q(text__icontains=terms[0])
        for term in terms[1:]:
            keyword_filter |= Q(text__icontains=term)

        candidates = list(searchable_chunks.filter(keyword_filter)[:max(40, k * 12)])
        ranked = []

        for chunk in candidates:
            normalized_text = chunk.text.casefold()
            frequencies = [
                len(re.findall(rf"(?<!\w){re.escape(term)}(?!\w)", normalized_text))
                for term in terms
            ]
            matched_terms = sum(frequency > 0 for frequency in frequencies)
            if matched_terms == 0:
                continue

            # Prefer chunks covering more query terms, then chunks repeating the
            # exact terms. Short terms receive a small acronym/identifier bonus.
            acronym_bonus = sum(
                1 for term, frequency in zip(terms, frequencies)
                if frequency and len(term) <= 5
            )
            rank = (
                matched_terms,
                acronym_bonus,
                sum(frequencies)
            )
            ranked.append((rank, chunk))

        ranked.sort(key=lambda item: item[0], reverse=True)

        # Two exact chunks normally provide enough grounded context while still
        # leaving room for semantically related results.
        keyword_limit = k if len(terms) == 1 else min(2, k)
        matches = [chunk for _, chunk in ranked[:keyword_limit]]
        for chunk in matches:
            chunk.score = 1.0

        return matches
