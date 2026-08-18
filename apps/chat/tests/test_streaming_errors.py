from unittest.mock import Mock, patch

from django.test import RequestFactory, SimpleTestCase, override_settings

from apps.chat import views
from apps.chat.services.chat_service import ChatService
from apps.core.exceptions import ModelUnavailableError
from apps.llm.model_manager import ModelManager


@override_settings(
    OLLAMA_HOST="http://127.0.0.1:11434",
    OLLAMA_MODEL="qwen2.5:7b",
)
class ModelManagerErrorTests(SimpleTestCase):
    @patch("apps.llm.model_manager.ollama.Client")
    def test_connection_error_has_actionable_message(self, client_class):
        client_class.return_value.chat.side_effect = ConnectionError(
            "[Errno 61] Connection refused"
        )

        with self.assertRaisesMessage(
            ModelUnavailableError,
            "The local AI service is not running. Start Ollama, then try again.",
        ):
            ModelManager().generate("Hello")


class StreamingErrorTests(SimpleTestCase):
    @patch("apps.chat.services.chat_service.ChatService.add_assistant_message")
    @patch("apps.chat.services.chat_service.RAGService")
    @patch("apps.chat.services.chat_service.ChatService.add_user_message")
    @patch("apps.chat.services.chat_service.ChatService.create_conversation")
    def test_unavailable_model_returns_readable_stream_message(
        self,
        create_conversation,
        add_user_message,
        rag_service,
        add_assistant_message,
    ):
        conversation = Mock()
        conversation.conversation_uuid = "conversation-id"
        create_conversation.return_value = conversation
        rag_service.return_value.stream.side_effect = ModelUnavailableError(
            "The local AI service is not running. Start Ollama, then try again."
        )

        response = "".join(
            ChatService.stream_message(
                prompt="What is ETL?",
                conversation_uuid=None,
            )
        )

        self.assertIn("The local AI service is not running", response)
        add_user_message.assert_called_once_with(conversation, "What is ETL?")
        add_assistant_message.assert_called_once()
        self.assertEqual(
            add_assistant_message.call_args.kwargs["metadata"],
            {"error_code": "MODEL_UNAVAILABLE"},
        )


class ConversationTitleTests(SimpleTestCase):
    def test_question_prompt_becomes_related_title(self):
        self.assertEqual(ChatService._generate_title("What is ETL?"), "ETL")

    def test_long_prompt_is_limited_to_seven_words(self):
        title = ChatService._generate_title(
            "Please explain modern data lake architecture with governance and security examples"
        )

        self.assertEqual(
            title,
            "modern data lake architecture with governance and…",
        )

    def test_existing_title_is_not_replaced(self):
        conversation = Mock(title="ETL overview")

        ChatService._update_title(conversation, "What is ELT?")

        conversation.save.assert_not_called()


class ConversationMessageSerializationTests(SimpleTestCase):
    def test_saved_message_includes_its_related_citations(self):
        document = Mock()
        document.original_name = "etl-guide.pdf"
        document.name = "ETL Guide"
        citations = []
        for page, score in [(4, 0.9234), (4, 0.88), (7, 0.91)]:
            citation = Mock()
            citation.document_id = "document-id"
            citation.document = document
            citation.chunk.page_number = page
            citation.similarity_score = score
            citations.append(citation)
        message = Mock()
        message.message_uuid = "message-id"
        message.role = "assistant"
        message.content = "ELT loads before transforming."
        message.created_at.isoformat.return_value = "2026-08-06T12:00:00+00:00"
        message.prompt_tokens = 10
        message.completion_tokens = 8
        message.total_tokens = 18
        message.citations.all.return_value = citations

        serialized = ChatService.serialize_message(message)

        self.assertEqual(
            serialized["citations"],
            [{"document": "etl-guide.pdf", "pages": [4, 7], "score": 0.923}],
        )


class StreamingViewConversationTests(SimpleTestCase):
    @patch("apps.chat.views.ChatService._update_title")
    @patch("apps.chat.views.ChatService.stream_message")
    @patch("apps.chat.views.ChatService.create_conversation")
    def test_new_conversation_id_is_returned_and_reused_for_stream(
        self,
        create_conversation,
        stream_message,
        update_title,
    ):
        conversation = Mock()
        conversation.conversation_uuid = "42780e12-99fe-4abc-9bae-2d1b651fe7fa"
        create_conversation.return_value = conversation
        stream_message.return_value = iter(["Answer"])
        request = RequestFactory().post(
            "/chat/stream/",
            data='{"prompt": "What is ETL?"}',
            content_type="application/json",
        )

        response = views.stream_message(request)

        self.assertEqual(
            response["X-Conversation-ID"],
            str(conversation.conversation_uuid),
        )
        update_title.assert_called_once_with(conversation, "What is ETL?")
        stream_message.assert_called_once_with(
            prompt="What is ETL?",
            conversation_uuid=conversation.conversation_uuid,
        )
