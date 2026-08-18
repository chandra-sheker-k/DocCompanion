
# Remove duplicate paragraphs.

class Deduplicator:
    def deduplicate(self, text: str) -> str:
        seen = set()
        output = []

        for paragraph in text.split("\n\n"):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            if paragraph in seen:
                continue
            seen.add(paragraph)
            output.append(paragraph)
        return "\n\n".join(output)