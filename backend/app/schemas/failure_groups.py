from datetime import datetime

from pydantic import Field, field_validator

from .common import AgentLensBaseModel
from .enums import FailureStatus, FailureType, Severity


class FailureGroupDocument(AgentLensBaseModel):
    group_id: str = Field(
        pattern=r"^GROUP-[0-9]{3,}$"
    )

    investigation_id: str = Field(
        pattern=r"^INV-[0-9]{4,}$"
    )

    failure_type: FailureType

    title: str = Field(
        min_length=1,
        max_length=250,
    )

    description: str = Field(
        min_length=1,
        max_length=3000,
    )

    occurrence_count: int = Field(
        ge=1
    )

    severity: Severity

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    failure_ids: list[str] = Field(
        min_length=1,
        max_length=1000,
    )

    session_ids: list[str] = Field(
        min_length=1,
        max_length=1000,
    )

    common_signals: list[str] = Field(
        default_factory=list,
        max_length=30,
    )

    ai_summary: str = Field(
        min_length=1,
        max_length=3000,
    )

    recommendation: str = Field(
        min_length=1,
        max_length=3000,
    )

    status: FailureStatus = FailureStatus.new

    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def validate_timestamp(cls, value: datetime):
        if value.tzinfo is None:
            raise ValueError(
                "created_at must be timezone-aware."
            )
        return value


from typing import TYPE_CHECKING  # noqa: E402

if TYPE_CHECKING:
    from .failures import FailureDocument


class FailureGroupDetailResponse(AgentLensBaseModel):
    group: FailureGroupDocument
    failures: list["FailureDocument"]
