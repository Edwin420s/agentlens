from datetime import datetime
from typing import Any

from pydantic import Field, model_validator

from .common import AgentLensBaseModel
from .enums import Actor, EventType


class AgentEvent(AgentLensBaseModel):
    event_id: str = Field(
        pattern=r"^EVT-[0-9]{5,}$"
    )

    session_id: str = Field(
        pattern=r"^SES-[0-9]{4,}$"
    )

    sequence: int = Field(ge=1)

    timestamp: datetime

    event_type: EventType
    actor: Actor

    content: str | None = Field(default=None, max_length=10000)

    tool_name: str | None = Field(default=None, max_length=150)

    tool_input: dict[str, Any] | None = None

    tool_output: dict[str, Any] | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_event_structure(self):
        if self.timestamp.tzinfo is None:
            raise ValueError("Timestamp must be timezone-aware.")

        if self.event_type == EventType.message:
            if not self.content:
                raise ValueError(
                    "Message events require content."
                )

        if self.event_type in {
            EventType.tool_call,
            EventType.tool_result,
        }:
            if not self.tool_name:
                raise ValueError(
                    "Tool events require tool_name."
                )

        if self.event_type == EventType.tool_call:
            if self.tool_input is None:
                raise ValueError(
                    "Tool calls require tool_input."
                )

        if self.event_type == EventType.tool_result:
            if self.tool_output is None:
                raise ValueError(
                    "Tool results require tool_output."
                )

        return self
