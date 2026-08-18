
from django.urls import path
from . import views

app_name = "documents"

urlpatterns = [
    path("upload/", views.upload_document, name="upload"),
    path("list/", views.list_documents, name="list"),
    path("delete/<uuid:document_uuid>/", views.delete_document, name="delete")
]