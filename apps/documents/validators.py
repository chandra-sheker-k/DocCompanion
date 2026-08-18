
from django.core.exceptions import ValidationError

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
    ".csv",
    ".xlsx",
    ".xls",
}


MAX_SIZE = 100 * 1024 * 1024

def validate_document(file):
    if file.size > MAX_SIZE:
        raise ValidationError("Maximum file size is 100 MB.")

    filename = file.name.lower()

    if not filename.endswith(tuple(ALLOWED_EXTENSIONS)):
        raise ValidationError("Unsupported document type.")