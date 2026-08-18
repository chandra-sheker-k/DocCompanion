
import logging
import ollama
from django.conf import settings

from apps.core.exceptions import ModelUnavailableError


logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self, *, model: str | None = None):
        self.model = model or settings.OLLAMA_MODEL
        self.client = ollama.Client(host=settings.OLLAMA_HOST)

    def _unavailable_error(self, exc: Exception) -> ModelUnavailableError:
        """Convert Ollama transport errors into safe, actionable messages."""
        detail = str(exc).lower()

        if "connection refused" in detail or "could not connect" in detail:
            message = ("The local AI service is not running. Start Ollama, then try again.")
        elif "not found" in detail or "pull model" in detail:
            message = (f"The local AI model '{self.model}' is not installed. Install it with: ollama pull {self.model}")
        else:
            message = "The local AI service is temporarily unavailable. Please try again."

        logger.warning(
            "Ollama request failed (host=%s, model=%s): %s",
            settings.OLLAMA_HOST,
            self.model,
            exc,
        )
        return ModelUnavailableError(message)

    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            )
            return response["message"]["content"].strip()
        except ModelUnavailableError:
            raise
        except Exception as exc:
            raise self._unavailable_error(exc) from exc

    def stream(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.2,
    ):
        try:
            stream = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
                stream=True,
            )

            for chunk in stream:
                content = chunk["message"]["content"]
                if content:
                    yield content
        except ModelUnavailableError:
            raise
        except Exception as exc:
            raise self._unavailable_error(exc) from exc
