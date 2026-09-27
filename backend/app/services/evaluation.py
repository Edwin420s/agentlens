import logging

from app.db import mongo

logger = logging.getLogger(__name__)


async def evaluate_investigation(investigation_id: str) -> dict:
    db = mongo.get_database()

    # ground truth from isolated collection
    gt_cursor = db["evaluation_labels"].find({"investigation_id": investigation_id})
    gt_by_session = {g["session_id"]: g async for g in gt_cursor}

    # detected results from sessions
    s_cursor = db["sessions"].find({"investigation_id": investigation_id})
    sessions = [s async for s in s_cursor]

    tp = fp = fn = tn = 0
    per_type = {
        "unsupported_success": {"tp": 0, "fp": 0, "fn": 0},
        "no_progress": {"tp": 0, "fp": 0, "fn": 0},
        "wrong_record": {"tp": 0, "fp": 0, "fn": 0},
        "repeated_question": {"tp": 0, "fp": 0, "fn": 0},
        "incomplete_request": {"tp": 0, "fp": 0, "fn": 0},
    }

    for s in sessions:
        gt = gt_by_session.get(s["session_id"])
        if gt is None:
            continue

        gt_failure = gt.get("status") == "failure"
        detected_signals = s.get("detected_signals", [])
        detected_failure = bool(detected_signals)

        if gt_failure and detected_failure:
            tp += 1
        elif gt_failure and not detected_failure:
            fn += 1
        elif not gt_failure and detected_failure:
            fp += 1
        else:
            tn += 1

        gt_type = gt.get("failure_type")
        if gt_failure and gt_type and gt_type in per_type:
            if detected_failure:
                per_type[gt_type]["tp"] += 1
            else:
                per_type[gt_type]["fn"] += 1

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return {
        "investigation_id": investigation_id,
        "confusion": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "per_failure_type": per_type,
        "sessions_evaluated": len(sessions),
    }
