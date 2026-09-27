from typing import Any


class AgentLensError(Exception):
    code = "AGENTLENS_ERROR"
    status_code = 400

    def __init__(self, message: str, details: list[Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or []


class NotFoundError(AgentLensError):
    code = "NOT_FOUND"
    status_code = 404


class ConflictError(AgentLensError):
    code = "CONFLICT"
    status_code = 409


class ValidationError(AgentLensError):
    code = "VALIDATION_ERROR"
    status_code = 422


class IngestionError(AgentLensError):
    code = "INGESTION_ERROR"
    status_code = 400


class AIProviderError(AgentLensError):
    code = "AI_PROVIDER_ERROR"
    status_code = 502
