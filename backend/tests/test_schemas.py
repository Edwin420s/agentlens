import pytest
from pydantic import ValidationError

from app.schemas.investigations import InvestigationResponse
from app.schemas.sessions import SessionDocument
from app.schemas.events import AgentEvent


def test_investigation_id_pattern():
    with pytest.raises(ValidationError):
        InvestigationResponse(
            investigation_id="INVALID",
            name="x", description=None,
            dataset_name="d", dataset_version="1",
            status="pending",
            created_at="2025-01-01T00:00:00+00:00",
        )


def test_session_timestamps_must_be_tz_aware():
    with pytest.raises(ValidationError):
        SessionDocument(
            session_id="SES-0001", investigation_id="INV-0001",
            agent_id="a", domain="d",
            started_at="2025-01-01T00:00:00",
            user_request="x",
            session_status="success",
        )


def test_event_structure_message_requires_content():
    with pytest.raises(ValidationError):
        AgentEvent(
            event_id="EVT-00001", session_id="SES-0001",
            sequence=1, timestamp="2025-01-01T00:00:00+00:00",
            event_type="message", actor="user",
        )
