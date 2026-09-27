from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import Field, field_validator

from .common import AgentLensBaseModel
from .enums import FailureStatus, FailureType, Severity

if TYPE_CHECKING:
    from .events import AgentEvent
    from .sessions import SessionDocument
    from .ai_analysis import AIAnalysisDocument


class EvidenceItem(AgentLensBaseModel):
    event_id: str = Field(
        pattern=r"^EVT-[0-9]{5,}$"
    )

    observation: str = Field(
        min_length=1,
        max_length=2000,
    )


class FailureClassification(AgentLensBaseModel):
    status: str = Field(pattern=r"^(success|failure|ambiguous)$")
    failure_type: FailureType | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class FailureDocument(AgentLensBaseModel):
    failure_id: str = Field(
        pattern=r"^FAIL-[0-9]{4,}$"
    )

    investigation_id: str = Field(
        pattern=r"^INV-[0-9]{4,}$"
    )

    session_id: str = Field(
        pattern=r"^SES-[0-9]{4,}$"
    )

    failure_type: FailureType

    severity: Severity

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    title: str = Field(
        min_length=1,
        max_length=250,
    )

    summary: str = Field(
        min_length=1,
        max_length=3000,
    )

    evidence_event_ids: list[str] = Field(
        min_length=1,
        max_length=20,
    )

    impact: str = Field(
        min_length=1,
        max_length=2000,
    )

    signals: list[str] = Field(
        default_factory=list,
        max_length=30,
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


class FailureDetailResponse(AgentLensBaseModel):
    failure: FailureDocument
    session_summary: "SessionDocument"
    evidence_events: list["AgentEvent"]
    ai_analysis: "AIAnalysisDocument | None" = None
    related_failures: list[FailureDocument]


class UpdateFailureStatusRequest(AgentLensBaseModel):
    status: FailureStatus
