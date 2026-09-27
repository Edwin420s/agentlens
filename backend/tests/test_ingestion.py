import pytest
from app.schemas.datasets import DatasetImport
from app.services.session_analyzer import classify_session


def test_classify_success():
    events = [
        {"event_id": "EVT-1", "sequence": 1, "event_type": "tool_call", "actor": "agent", "tool_name": "t", "tool_input": {}},
        {"event_id": "EVT-2", "sequence": 2, "event_type": "tool_result", "actor": "tool", "tool_name": "t", "tool_output": {"success": True}},
    ]
    out = classify_session("do it", events)
    assert out["status"] == "success"
