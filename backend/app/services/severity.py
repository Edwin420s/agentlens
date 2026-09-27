from app.schemas.enums import FailureType, Severity

SEVERITY_MAP: dict[FailureType, Severity] = {
    FailureType.unsupported_success: Severity.critical,
    FailureType.wrong_record: Severity.critical,
    FailureType.no_progress: Severity.high,
    FailureType.incomplete_request: Severity.high,
    FailureType.repeated_question: Severity.medium,
}


SIGNAL_TO_TYPE: dict[str, FailureType] = {
    "unsupported_success": FailureType.unsupported_success,
    "no_progress": FailureType.no_progress,
    "wrong_record": FailureType.wrong_record,
    "repeated_question": FailureType.repeated_question,
    "incomplete_request": FailureType.incomplete_request,
    # extras that map to the closest frozen type
    "silent_failure": FailureType.unsupported_success,
    "pending_operation": FailureType.no_progress,
    "tool_loop": FailureType.no_progress,
    "ambiguous_outcome": FailureType.no_progress,
}


def severity_for(failure_type: FailureType) -> Severity:
    return SEVERITY_MAP.get(failure_type, Severity.medium)
