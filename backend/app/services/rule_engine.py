import logging
import re
from dataclasses import dataclass, field

from app.schemas.enums import ActionStatus, Actor, EventType

logger = logging.getLogger(__name__)


@dataclass
class RuleResult:
    signals: list[str] = field(default_factory=list)
    actions_taken: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add(self, signal: str) -> None:
        if signal not in self.signals:
            self.signals.append(signal)


# ---------- helpers ----------

_ENTITY_PATTERNS = [
    (re.compile(r"\bORD-?\d{3,}\b", re.I), "order"),
    (re.compile(r"\bINV-?\d{3,}\b", re.I), "invoice"),
    (re.compile(r"\bACC-?\d{3,}\b", re.I), "account"),
    (re.compile(r"\bTKT-?\d{3,}\b", re.I), "ticket"),
    (re.compile(r"\bCUS-?\d{3,}\b", re.I), "customer"),
    (re.compile(r"\b[A-Z]{3}-?\d{3,}\b"), "generic"),
]

_FAILURE_WORDS = re.compile(
    r"\b(fail|failed|failure|error|could not|couldn't|cannot|can't|unable|"
    r"not found|no results|did not|didn't|not able)\b", re.I,
)
_SUCCESS_WORDS = re.compile(
    r"\b(success|successful|done|complete|completed|created|updated|"
    r"processed|confirmed|resolved)\b", re.I,
)
_PENDING_WORDS = re.compile(
    r"\b(pending|still processing|in progress|will be|shortly|"
    r"in a few|being processed|on its way)\b", re.I,
)


def _extract_entities(text: str) -> set[str]:
    if not text:
        return set()
    found: set[str] = set()
    for pattern, kind in _ENTITY_PATTERNS:
        for m in pattern.findall(text):
            found.add(f"{kind}:{m.upper().replace('-', '')}")
    return found


def _extract_asks(user_request: str) -> list[str]:
    parts = re.split(r"(?:;|\.|\?|\n|\band\b|\bthen\b|\balso\b)", user_request, flags=re.I)
    return [p.strip() for p in parts if len(p.strip()) >= 4]


def _tool_output_is_failure(output: dict | None) -> bool:
    if not output:
        return False
    status = str(output.get("status", "")).lower()
    if status in {"error", "failed", "failure", "not_found"}:
        return True
    if output.get("error"):
        return True
    if output.get("success") is False:
        return True
    return False


def _tool_output_is_success(output: dict | None) -> bool:
    if not output:
        return False
    if output.get("success") is True:
        return True
    status = str(output.get("status", "")).lower()
    return status in {"ok", "success", "succeeded"}


# ---------- main engine ----------

def analyze_session(user_request: str, events: list[dict]) -> RuleResult:
    result = RuleResult()

    ordered: list[dict] = sorted(events, key=lambda e: e.get("sequence", 0))

    user_entities = _extract_entities(user_request)
    asks = _extract_asks(user_request)

    agent_messages: list[str] = []
    successful_actions = 0
    failed_actions = 0
    request_entities_seen: set[str] = set()
    tool_input_signatures: list[str] = []

    # Track tool calls and pair them with tool results
    tool_calls: list[dict] = []
    call_to_result: dict[str, dict] = {}
    pending_calls: list[dict] = []

    for ev in ordered:
        et = ev.get("event_type")
        if et == EventType.message.value:
            if ev.get("actor") == Actor.agent.value and ev.get("content"):
                agent_messages.append(ev["content"])
        elif et == EventType.tool_call.value:
            tool_calls.append(ev)
            pending_calls.append(ev)
            signature = f"{ev.get('tool_name')}::{sorted((ev.get('tool_input') or {}).items())}"
            tool_input_signatures.append(signature)
            for v in (ev.get("tool_input") or {}).values():
                if isinstance(v, str):
                    request_entities_seen |= _extract_entities(v)
        elif et == EventType.tool_result.value:
            tool_name = ev.get("tool_name")
            matched_call = None
            for i in range(len(pending_calls) - 1, -1, -1):
                if pending_calls[i].get("tool_name") == tool_name:
                    matched_call = pending_calls.pop(i)
                    break
            if matched_call is None and pending_calls:
                matched_call = pending_calls.pop(0)

            if matched_call:
                cid = matched_call.get("event_id", "")
                call_to_result[cid] = ev

            if _tool_output_is_failure(ev.get("tool_output")):
                failed_actions += 1
            elif _tool_output_is_success(ev.get("tool_output")):
                successful_actions += 1

    # ---- signal 2: no_progress (same tool signature failed repeatedly) ----
    sig_counts: dict[str, int] = {}
    for s in tool_input_signatures:
        sig_counts[s] = sig_counts.get(s, 0) + 1
    if any(c >= 2 for c in sig_counts.values()):
        result.add("no_progress")

    # ---- signal 8: tool_loop (same signature >= 3) ----
    if any(c >= 3 for c in sig_counts.values()):
        result.add("tool_loop")

    # ---- signal 7: silent_failure ----
    final_text = " ".join(agent_messages[-3:]) if agent_messages else ""
    if failed_actions > 0 and not _FAILURE_WORDS.search(final_text):
        result.add("silent_failure")

    # ---- signal 1: unsupported_success ----
    claimed_success = any(_SUCCESS_WORDS.search(m) for m in agent_messages[-2:])
    if claimed_success and successful_actions == 0:
        result.add("unsupported_success")

    # ---- signal 6: pending_operation ----
    if _PENDING_WORDS.search(final_text):
        result.add("pending_operation")

    # ---- signal 3: wrong_record ----
    mismatch = False
    for call in tool_calls:
        cid = call.get("event_id", "")
        res = call_to_result.get(cid)
        if res:
            inp = call.get("tool_input") or {}
            out = res.get("tool_output") or {}
            for k in ("order_id", "customer_id", "payment_id", "return_id", "shipment_id", "account_id", "invoice_id"):
                if inp.get(k) and out.get(k) and str(inp[k]).upper().replace("-", "") != str(out[k]).upper().replace("-", ""):
                    mismatch = True
                    break
        if mismatch:
            break

    if not mismatch and user_entities and request_entities_seen:
        for ent in request_entities_seen:
            kind = ent.split(":", 1)[0]
            same_kind_user = {e for e in user_entities if e.startswith(kind + ":")}
            if same_kind_user and ent not in same_kind_user:
                mismatch = True
                break

    if mismatch:
        result.add("wrong_record")

    # ---- signal 4: repeated_question ----
    if len(agent_messages) >= 2:
        normalized = [m.strip().lower() for m in agent_messages]
        if normalized[-1] and normalized[-1] == normalized[-2]:
            result.add("repeated_question")
        elif "?" in normalized[-1] and "?" in normalized[-2]:
            a = set(normalized[-1].split())
            b = set(normalized[-2].split())
            if a and b and len(a & b) / max(len(a | b), 1) >= 0.7:
                result.add("repeated_question")

    # ---- signal 5: incomplete_request ----
    if len(asks) >= 2:
        covered = 0
        for ask in asks:
            tokens = set(re.findall(r"\w+", ask.lower()))
            tokens = {t for t in tokens if len(t) > 3}
            if not tokens:
                continue
            if any(tokens & set(re.findall(r"\w+", m.lower())) for m in agent_messages):
                covered += 1
        if covered < len(asks):
            result.add("incomplete_request")

    # ---- signal 9: ambiguous_outcome ----
    if successful_actions > 0 and failed_actions > 0:
        result.add("ambiguous_outcome")

    # ---- legitimate retry handling ----
    sig_outcomes: dict[str, list[str]] = {}
    for call in tool_calls:
        cid = call.get("event_id", "")
        signature = f"{call.get('tool_name')}::{sorted((call.get('tool_input') or {}).items())}"
        res = call_to_result.get(cid) or {}
        out = res.get("tool_output") or {}
        if _tool_output_is_success(out):
            sig_outcomes.setdefault(signature, []).append("success")
        elif _tool_output_is_failure(out):
            sig_outcomes.setdefault(signature, []).append("failure")

    legit_retry = any(
        "failure" in outcomes and "success" in outcomes
        for outcomes in sig_outcomes.values()
    )
    if legit_retry:
        result.signals = [s for s in result.signals if s not in {"no_progress", "tool_loop"}]
        result.notes.append("legitimate_retry_detected")

        # If all failed tools were successfully recovered, remove silent_failure & ambiguous_outcome
        all_recovered = all(
            outcomes[-1] == "success" for outcomes in sig_outcomes.values() if "failure" in outcomes
        )
        if all_recovered:
            result.signals = [s for s in result.signals if s not in {"silent_failure", "ambiguous_outcome"}]

    # ---- pending_op demotion ----
    if "pending_operation" in result.signals and successful_actions > 0:
        result.notes.append("pending_after_success")

    # ---- build actions_taken ----
    if tool_calls:
        for call in tool_calls:
            cid = call.get("event_id", "")
            res = call_to_result.get(cid) or {}
            out = res.get("tool_output") or {}
            if _tool_output_is_success(out):
                status = ActionStatus.success.value
            elif _tool_output_is_failure(out):
                not_found = "not_found" in str(out).lower() or "not found" in str(out).lower()
                status = ActionStatus.not_found.value if not_found else ActionStatus.failed.value
            else:
                status = ActionStatus.pending.value
            result.actions_taken.append({
                "action": call.get("tool_name") or "unknown_action",
                "status": status,
                "entity_type": None,
                "entity_id": None,
            })
    else:
        for e in ordered:
            if e.get("event_type") == EventType.tool_result.value:
                out = e.get("tool_output") or {}
                if _tool_output_is_success(out):
                    status = ActionStatus.success.value
                elif _tool_output_is_failure(out):
                    status = ActionStatus.failed.value
                else:
                    status = ActionStatus.pending.value
                result.actions_taken.append({
                    "action": e.get("tool_name") or "unknown_action",
                    "status": status,
                    "entity_type": None,
                    "entity_id": None,
                })

    return result
