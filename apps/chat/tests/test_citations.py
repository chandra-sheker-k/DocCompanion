from django.test import SimpleTestCase

from apps.chat.services.citations import group_citation_locations


class CitationGroupingTests(SimpleTestCase):
    def test_same_document_and_page_are_not_duplicated(self):
        grouped = group_citation_locations([
            {"document_id": "doc-1", "document": "guide.pdf", "page": 3, "score": 0.9},
            {"document_id": "doc-1", "document": "guide.pdf", "page": 3, "score": 0.8},
        ])

        self.assertEqual(
            grouped,
            [{"document": "guide.pdf", "pages": [3], "score": 0.9}],
        )

    def test_multiple_pages_share_one_document_name(self):
        grouped = group_citation_locations([
            {"document_id": "doc-1", "document": "guide.pdf", "page": 8, "score": 0.7},
            {"document_id": "doc-1", "document": "guide.pdf", "page": 2, "score": 0.95},
        ])

        self.assertEqual(
            grouped,
            [{"document": "guide.pdf", "pages": [2, 8], "score": 0.95}],
        )
