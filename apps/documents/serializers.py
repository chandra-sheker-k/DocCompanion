
from rest_framework import serializers

from .models import UploadedDocument

class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedDocument
        fields = "__all__"