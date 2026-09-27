import logging

from app.schemas.enums import ActionStatus, SessionStatus
from app.services.rule_engine import analyze_session
from app.services.severity import SIGNAL_TO_TYPE

logger = logging.getLogger(__name__)


def classify_session(user_request: str, events: list[dict]) -> dict:
    """Returns dict {status, signals, actions_taken, notes}."""
    result = analyze_session(user_request, events)

    # Map signals -> session status
    negative_signals = {
        s for s in result.signals
        if s in SIGNAL_TO_TYPE
    }
    has_success = any(
        a["status"] == ActionStatus.success.value for a in result.actions_taken
    )

    if not negative_signals and has_success:
        status = SessionStatus.success.value
    elif "ambiguous_outcome" in result.signals:
        status = SessionStatus.ambiguous.value
    elif negative_signals:
        status = SessionStatus.failure.value
    elif not result.actions_taken:
        status = SessionStatus.ambiguous.value
    else:
        status = SessionStatus.success.value if has_success else SessionStatus.ambiguous.value

    return {
        "status": status,
        "signals": result.signals,
        "actions_taken": result.actions_taken,
        "notes": result.notes,
    }
