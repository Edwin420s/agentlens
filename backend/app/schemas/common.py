from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AgentLensBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )


class APIError(AgentLensBaseModel):
    code: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=1000)
    details: list[Any] = Field(default_factory=list)


class APIResponse[T](AgentLensBaseModel):
    success: bool
    data: T | None = None
    error: APIError | None = None


class TimestampedModel(AgentLensBaseModel):
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("Timestamp must be timezone-aware.")
        return value
