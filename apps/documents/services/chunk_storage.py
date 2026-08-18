
from apps.documents.models import DocumentChunk

def save_chunks(document, chunks):
    DocumentChunk.objects.filter(document=document).delete()

    objects = []

    for chunk in chunks:
        objects.append(
            DocumentChunk(
                document=document,
                document_name=document.original_name,
                chunk_index=chunk.index,
                page_number=chunk.page_number,
                section_title=chunk.section_title,
                start_char=chunk.start_char,
                end_char=chunk.end_char,
                token_count=chunk.token_count,
                word_count=chunk.word_count,
                character_count=chunk.character_count,
                text=chunk.text,
                metadata={
                    "file_type": document.file_type,
                    "checksum": document.checksum,
                }
            )
        )

    DocumentChunk.objects.bulk_create(objects)