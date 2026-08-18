
class DocCompanionError(Exception):
    """Base application exception."""

    code = "UNKNOWN_ERROR"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class NoDocumentsError(DocCompanionError):
    code = "NO_DOCUMENTS"

class NoSearchResultsError(DocCompanionError):
    code = "NO_RESULTS"

class ModelUnavailableError(DocCompanionError):
    code = "MODEL_UNAVAILABLE"

class EmbeddingError(DocCompanionError):
    code = "EMBEDDING_ERROR"

class IndexNotLoadedError(DocCompanionError):
    code = "INDEX_NOT_LOADED"

class InvalidConversationError(DocCompanionError):
    code = "INVALID_CONVERSATION"