from datetime import datetime

from pydantic import Field, field_validator

from .common import AgentLensBaseModel
from .enums import AnalysisStatus, FailureType
from .failures import EvidenceItem


class AIClassification(AgentLensBaseModel):
    status: str = Field(
        pattern=r"^(success|failure|ambiguous)$"
    )

    failure_type: FailureType | None = None

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )


class AIAnalysisDocument(AgentLensBaseModel):
    analysis_id: str = Field(
        pattern=r"^AI-[0-9]{5,}$"
    )

    investigation_id: str = Field(
        pattern=r"^INV-[0-9]{4,}$"
    )

    session_id: str = Field(
        pattern=r"^SES-[0-9]{4,}$"
    )

    failure_id: str | None = Field(
        default=None,
        pattern=r"^FAIL-[0-9]{4,}$",
    )

    model: str = Field(
        min_length=1,
        max_length=150,
    )

    analysis_version: str = Field(
        min_length=1,
        max_length=50,
    )

    status: AnalysisStatus

    classification: AIClassification

    summary: str = Field(
        min_length=1,
        max_length=3000,
    )

    evidence: list[dict] = Field(
        default_factory=list,
        max_length=20,
    )

    impact: str = Field(
        min_length=1,
        max_length=2000,
    )

    recommendation: str = Field(
        min_length=1,
        max_length=3000,
    )

    alternative_interpretations: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    needs_human_review: bool

    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def validate_timestamp(cls, value: datetime):
        if value.tzinfo is None:
            raise ValueError(
                "created_at must be timezone-aware."
            )
        return value


class GroupAIAnalysis(AgentLensBaseModel):
    analysis_id: str = Field(
        pattern=r"^AI-[0-9]{5,}$"
    )

    group_id: str = Field(
        pattern=r"^GROUP-[0-9]{3,}$"
    )

    model: str = Field(
        min_length=1,
        max_length=150,
    )

    analysis_version: str = Field(
        min_length=1,
        max_length=50,
    )

    pattern: str = Field(
        min_length=1,
        max_length=3000,
    )

    common_signals: list[str] = Field(
        default_factory=list,
        max_length=30,
    )

    affected_workflows: list[str] = Field(
        default_factory=list,
        max_length=30,
    )

    investigation_area: str = Field(
        min_length=1,
        max_length=2000,
    )

    recommendation: str = Field(
        min_length=1,
        max_length=3000,
    )

    evidence: list[EvidenceItem] = Field(
        default_factory=list,
        max_length=50,
    )

    alternative_explanations: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    needs_human_review: bool

    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def validate_timestamp(cls, value: datetime):
        if value.tzinfo is None:
            raise ValueError(
                "created_at must be timezone-aware."
            )
        return value


class InvestigationAssistantRequest(AgentLensBaseModel):
    question: str = Field(
        min_length=3,
        max_length=2000,
    )


class AssistantEvidence(AgentLensBaseModel):
    failure_id: str = Field(
        pattern=r"^FAIL-[0-9]{4,}$"
    )

    event_ids: list[str] = Field(
        min_length=1,
        max_length=20,
    )


class InvestigationAssistantResponse(AgentLensBaseModel):
    answer: str = Field(
        min_length=1,
        max_length=5000,
    )

    evidence: list[AssistantEvidence] = Field(
        default_factory=list,
        max_length=50,
    )

    uncertainty: str = Field(
        min_length=1,
        max_length=2000,
    )

    recommendations: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    observed_facts: list[str] = Field(
        default_factory=list,
        max_length=50,
    )

    recommendation: list[str] = Field(
        default_factory=list,
        max_length=20,
    )
