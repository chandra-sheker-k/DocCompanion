from types import SimpleNamespace
from unittest.mock import MagicMock

from django.test import SimpleTestCase

from apps.embeddings.services.search_service import SearchService


class KeywordSearchTests(SimpleTestCase):
    def test_short_acronym_is_kept_as_meaningful_term(self):
        self.assertEqual(SearchService._keyword_terms("What is ELT?"), ["elt"])

    def test_exact_acronym_does_not_match_inside_another_word(self):
        chunks = [
            SimpleNamespace(pk=1, text="Delta Lake provides ACID transactions."),
            SimpleNamespace(pk=2, text="ELT loads data before transforming it."),
        ]
        queryset = MagicMock()
        queryset.filter.return_value.__getitem__.return_value = chunks

        matches = SearchService._keyword_search(queryset, "ELT", k=5)

        self.assertEqual([chunk.pk for chunk in matches], [2])
        self.assertEqual(matches[0].score, 1.0)

    def test_multiple_acronyms_prioritize_chunk_containing_both(self):
        chunks = [
            SimpleNamespace(pk=1, text="ETL transforms data before loading."),
            SimpleNamespace(pk=2, text="ETL and ELT use different transform stages."),
        ]
        queryset = MagicMock()
        queryset.filter.return_value.__getitem__.return_value = chunks

        matches = SearchService._keyword_search(
            queryset,
            "Compare ETL and ELT",
            k=5,
        )

        self.assertEqual(matches[0].pk, 2)
