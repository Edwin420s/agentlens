from datetime import datetime
from typing import Any, TYPE_CHECKING

from pydantic import Field, model_validator

from .common import AgentLensBaseModel
from .enums import ActionStatus, SessionStatus

if TYPE_CHECKING:
    from .events import AgentEvent
    from .failures import FailureDocument
    from .ai_analysis import AIAnalysisDocument


class ActionOutcome(AgentLensBaseModel):
    action: str = Field(min_length=1, max_length=200)

    status: ActionStatus

    entity_type: str | None = Field(
        default=None,
        max_length=100,
    )

    entity_id: str | None = Field(
        default=None,
        max_length=200,
    )


class SessionDocument(AgentLensBaseModel):
    session_id: str = Field(
        pattern=r"^SES-[0-9]{4,}$"
    )

    investigation_id: str = Field(
        pattern=r"^INV-[0-9]{4,}$"
    )

    agent_id: str = Field(
        min_length=1,
        max_length=150,
    )

    domain: str = Field(
        min_length=1,
        max_length=150,
    )

    started_at: datetime
    ended_at: datetime | None = None

    user_request: str = Field(
        min_length=1,
        max_length=5000,
    )

    final_response: str | None = Field(
        default=None,
        max_length=5000,
    )

    expected_outcome: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    actual_outcome: list[ActionOutcome] = Field(
        default_factory=list,
        max_length=20,
    )

    session_status: SessionStatus

    detected_signals: list[str] = Field(
        default_factory=list,
        max_length=30,
    )

    failure_ids: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    @model_validator(mode="after")
    def validate_timestamps(self):
        if self.started_at.tzinfo is None:
            raise ValueError(
                "started_at must be timezone-aware."
            )

        if self.ended_at is not None:
            if self.ended_at.tzinfo is None:
                raise ValueError(
                    "ended_at must be timezone-aware."
                )

            if self.ended_at < self.started_at:
                raise ValueError(
                    "ended_at cannot be before started_at."
                )

        return self


class SessionDetailResponse(AgentLensBaseModel):
    session: SessionDocument
    events: list["AgentEvent"]
    failures: list["FailureDocument"]
    ai_analyses: list["AIAnalysisDocument"]
