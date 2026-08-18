from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import StreamingHttpResponse

from apps.chat.models import Conversation
from apps.chat.services.chat_service import ChatService
from apps.chat.services.rag_service import RAGService

def index(request):
    """
    Chat UI.
    """
    return render(request, "chat/index.html")

@require_POST
@csrf_exempt
def new_chat(request):
    conversation = ChatService.create_conversation()
    return JsonResponse({"conversation_id": str(conversation.conversation_uuid),
            "title": conversation.title}
    )

@require_GET
def history(request):
    conversations = ChatService.list_conversations()
    data = [
        ChatService.serialize_conversation(conversation)
        for conversation in conversations
    ]
    return JsonResponse(data, safe=False)

@require_GET
def conversation(request, conversation_uuid):
    conversation = get_object_or_404( Conversation,
                                      conversation_uuid=conversation_uuid,
                                      is_archived=False)

    messages = [
        ChatService.serialize_message(message)
        for message in
        ChatService.get_messages(conversation)
    ]

    return JsonResponse({
            "conversation": ChatService.serialize_conversation(conversation),
            "messages": messages,
        }
    )

@require_http_methods(["DELETE"])
@csrf_exempt
def delete_conversation(request, conversation_uuid):
    conversation = get_object_or_404(
        Conversation,
        conversation_uuid=conversation_uuid
    )

    conversation.is_archived = True
    conversation.save(update_fields=["is_archived", "updated_at"])
    return JsonResponse({"success": True})

@require_POST
@csrf_exempt
def send_message(request):
    body = json.loads(request.body)
    prompt = body.get("prompt", "").strip()
    conversation_uuid = body.get("conversation_id")

    if not prompt:
        return JsonResponse({"error": "Prompt required."}, status=400)

    if conversation_uuid:
        conversation = ChatService.get_conversation(conversation_uuid)
    else:
        conversation = ChatService.create_conversation()

    ChatService.add_user_message(conversation, prompt)

    #
    # Phase 5.4
    # Replace this with RAGService.ask(...)
    #
    rag = RAGService()
    result = rag.answer(
        question=prompt,
        conversation=conversation,
        user_message=prompt,
    )
    ChatService.add_assistant_message(conversation, result["answer"])

    return JsonResponse(request)

@require_POST
@csrf_exempt
def stream_message(request):
    body = json.loads(request.body)
    prompt = body.get("prompt", "").strip()
    conversation_uuid = body.get("conversation_id")

    if not prompt:
        return JsonResponse({"error": "Prompt required."}, status=400)

    if conversation_uuid:
        conversation = ChatService.get_conversation(conversation_uuid)
    else:
        conversation = ChatService.create_conversation()

    ChatService._update_title(conversation, prompt)

    response = StreamingHttpResponse(
        ChatService.stream_message(
            prompt=prompt,
            conversation_uuid=conversation.conversation_uuid,
        ),
        content_type="text/plain",
    )
    response["X-Conversation-ID"] = str(conversation.conversation_uuid)
    return response
