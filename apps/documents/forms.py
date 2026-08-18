
from django import forms

from .validators import validate_document

class UploadDocumentForm(forms.Form):
    file = forms.FileField(validators=[validate_document])