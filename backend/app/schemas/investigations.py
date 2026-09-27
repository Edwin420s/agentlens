from datetime import datetime

from pydantic import Field, field_validator

from .common import AgentLensBaseModel
from .enums import InvestigationStatus


class CreateInvestigationRequest(AgentLensBaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    dataset_name: str = Field(min_length=1, max_length=150)


class InvestigationStats(AgentLensBaseModel):
    total_sessions: int = Field(default=0, ge=0)
    successful_sessions: int = Field(default=0, ge=0)
    failed_sessions: int = Field(default=0, ge=0)
    ambiguous_sessions: int = Field(default=0, ge=0)
    failure_count: int = Field(default=0, ge=0)
    failure_group_count: int = Field(default=0, ge=0)


class InvestigationResponse(AgentLensBaseModel):
    investigation_id: str = Field(
        pattern=r"^INV-[0-9]{4,}$"
    )
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None

    dataset_name: str
    dataset_version: str

    status: InvestigationStatus

    total_sessions: int = Field(default=0, ge=0)
    successful_sessions: int = Field(default=0, ge=0)
    failed_sessions: int = Field(default=0, ge=0)
    ambiguous_sessions: int = Field(default=0, ge=0)
    failure_count: int = Field(default=0, ge=0)
    failure_group_count: int = Field(default=0, ge=0)

    created_at: datetime
    completed_at: datetime | None = None

    @field_validator("created_at", "completed_at")
    @classmethod
    def validate_timezone(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("Timestamp must be timezone-aware.")
        return value
