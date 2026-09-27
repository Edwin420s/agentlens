from app.services.rule_engine import analyze_session


def test_unsupported_success():
    events = [
        {"event_id": "EVT-1", "sequence": 1, "event_type": "message", "actor": "user", "content": "do x"},
        {"event_id": "EVT-2", "sequence": 2, "event_type": "message", "actor": "agent", "content": "success!"},
    ]
    result = analyze_session("do x", events)
    assert "unsupported_success" in result.signals


def test_no_progress_legitimate_retry_suppressed():
    events = [
        {"event_id": "EVT-1", "sequence": 1, "event_type": "tool_call", "actor": "agent", "tool_name": "t", "tool_input": {"a": 1}},
        {"event_id": "EVT-2", "sequence": 2, "event_type": "tool_result", "actor": "tool", "tool_name": "t", "tool_output": {"error": "x"}},
        {"event_id": "EVT-3", "sequence": 3, "event_type": "tool_call", "actor": "agent", "tool_name": "t", "tool_input": {"a": 1}},
        {"event_id": "EVT-4", "sequence": 4, "event_type": "tool_result", "actor": "tool", "tool_name": "t", "tool_output": {"success": True}},
    ]
    result = analyze_session("do x", events)
    assert "no_progress" not in result.signals


def test_wrong_record():
    events = [
        {"event_id": "EVT-1", "sequence": 1, "event_type": "message", "actor": "user", "content": "cancel ORD-11111"},
        {"event_id": "EVT-2", "sequence": 2, "event_type": "tool_call", "actor": "agent", "tool_name": "cancel", "tool_input": {"order_id": "ORD-22222"}},
        {"event_id": "EVT-3", "sequence": 3, "event_type": "tool_result", "actor": "tool", "tool_name": "cancel", "tool_output": {"success": True}},
    ]
    result = analyze_session("cancel ORD-11111", events)
    assert "wrong_record" in result.signals
