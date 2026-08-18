
#Language detection.

from langdetect import detect

class LanguageDetector:

    @staticmethod
    def detect(text: str) -> str:
        if len(text) < 30:
            return "unknown"
        try:
            return detect(text)
        except Exception:
            return "unknown"