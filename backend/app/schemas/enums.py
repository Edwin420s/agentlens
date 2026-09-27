from enum import StrEnum


class InvestigationStatus(StrEnum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class SessionStatus(StrEnum):
    success = "success"
    failure = "failure"
    ambiguous = "ambiguous"


class FailureType(StrEnum):
    unsupported_success = "unsupported_success"
    no_progress = "no_progress"
    wrong_record = "wrong_record"
    repeated_question = "repeated_question"
    incomplete_request = "incomplete_request"


class Severity(StrEnum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class FailureStatus(StrEnum):
    new = "new"
    investigating = "investigating"
    reviewed = "reviewed"
    resolved = "resolved"


class AnalysisStatus(StrEnum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class EventType(StrEnum):
    message = "message"
    tool_call = "tool_call"
    tool_result = "tool_result"


class Actor(StrEnum):
    user = "user"
    agent = "agent"
    tool = "tool"
    system = "system"


class ActionStatus(StrEnum):
    success = "success"
    failed = "failed"
    pending = "pending"
    not_found = "not_found"
