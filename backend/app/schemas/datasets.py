from datetime import datetime
from typing import Any

from pydantic import Field, model_validator

from .common import AgentLensBaseModel
from .events import AgentEvent
from .sessions import ActionOutcome


class GroundTruth(AgentLensBaseModel):
    status: str = Field(
        pattern=r"^(success|failure|ambiguous)$"
    )

    failure_type: str | None = None


class DatasetSession(AgentLensBaseModel):
    session_id: str = Field(
        pattern=r"^SES-[0-9]{4,}$"
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

    events: list[AgentEvent] = Field(
        min_length=1,
        max_length=1000,
    )

    ground_truth: GroundTruth | None = None

    @model_validator(mode="after")
    def validate_dataset_session(self):
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

        event_ids = set()
        sequences = set()

        for event in self.events:
            if event.session_id != self.session_id:
                raise ValueError(
                    f"Event {event.event_id} belongs to "
                    f"{event.session_id}, not {self.session_id}."
                )

            if event.event_id in event_ids:
                raise ValueError(
                    f"Duplicate event ID: {event.event_id}"
                )

            if event.sequence in sequences:
                raise ValueError(
                    f"Duplicate event sequence: {event.sequence}"
                )

            event_ids.add(event.event_id)
            sequences.add(event.sequence)

        return self


class DatasetImport(AgentLensBaseModel):
    dataset_name: str = Field(
        min_length=1,
        max_length=150,
    )

    dataset_version: str = Field(
        min_length=1,
        max_length=50,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    sessions: list[DatasetSession] = Field(
        min_length=1,
        max_length=10000,
    )

    @model_validator(mode="after")
    def validate_unique_session_ids(self):
        ids = [session.session_id for session in self.sessions]

        if len(ids) != len(set(ids)):
            raise ValueError(
                "Dataset contains duplicate session IDs."
            )

        return self
