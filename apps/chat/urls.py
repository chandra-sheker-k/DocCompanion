from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("", views.index, name="index"),
    path("chat/new/", views.new_chat, name="new_chat"),
    path("chat/send/", views.send_message, name="send_message"),
    path("chat/history/", views.history, name="history"),
    path("chat/<uuid:conversation_uuid>/", views.conversation, name="conversation"),
    path("chat/delete/<uuid:conversation_uuid>/", views.delete_conversation, name="delete_conversation"),
    path("chat/stream/", views.stream_message, name="stream_message"),
]