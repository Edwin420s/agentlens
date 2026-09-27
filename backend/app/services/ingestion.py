import logging
from datetime import datetime, timezone

from app.db import mongo
from app.db.repositories import (
    datasets as ds_repo,
    events as ev_repo,
    failures as fail_repo,
    investigations as inv_repo,
    sessions as sess_repo,
)
from app.schemas.datasets import DatasetImport
from app.services.session_analyzer import classify_session
from app.services.failure_builder import build_failures
from app.services.failure_grouper import group_failures

logger = logging.getLogger(__name__)


async def import_dataset(dataset: DatasetImport, target_investigation_id: str | None = None) -> dict:
    await ds_repo.save_dataset_record(
        dataset.dataset_name,
        dataset.dataset_version,
        dataset.description,
        len(dataset.sessions),
    )

    if target_investigation_id:
        inv_id = target_investigation_id
        await inv_repo.update_investigation(inv_id, {
            "dataset_name": dataset.dataset_name,
            "dataset_version": dataset.dataset_version,
            "status": "running",
        })
    else:
        inv = await inv_repo.create_investigation(
            name=f"Ingestion: {dataset.dataset_name} v{dataset.dataset_version}",
            description=dataset.description,
            dataset_name=dataset.dataset_name,
            dataset_version=dataset.dataset_version,
        )
        inv_id = inv["investigation_id"]
        await inv_repo.update_investigation(inv_id, {"status": "running"})

    session_docs: list[dict] = []
    event_docs: list[dict] = []
    session_raw_events: dict[str, list[dict]] = {}
    session_evidence_ids: dict[str, list[str]] = {}

    for ds_session in dataset.sessions:
        raw_events = [e.model_dump() for e in ds_session.events]

        analysis = classify_session(ds_session.user_request, raw_events)
        evidence_ids = [e.event_id for e in ds_session.events][:5]

        session_doc = {
            "session_id": ds_session.session_id,
            "investigation_id": inv_id,
            "agent_id": ds_session.agent_id,
            "domain": ds_session.domain,
            "started_at": ds_session.started_at,
            "ended_at": ds_session.ended_at,
            "user_request": ds_session.user_request,
            "final_response": None,
            "expected_outcome": [],
            "actual_outcome": analysis["actions_taken"],
            "session_status": analysis["status"],
            "detected_signals": analysis["signals"],
            "failure_ids": [],
        }
        session_docs.append(session_doc)
        session_raw_events[ds_session.session_id] = raw_events
        session_evidence_ids[ds_session.session_id] = evidence_ids

        for e in ds_session.events:
            ev_doc = e.model_dump()
            event_docs.append(ev_doc)

    await sess_repo.bulk_insert_sessions(session_docs)
    await ev_repo.bulk_insert_events(event_docs)

    # --- AI session analysis ---
    from app.ai.analyzer import analyze_session_ai
    from app.db.repositories import ai_analysis as ai_repo

    all_failures: list[dict] = []
    ai_failures_by_session: dict[str, str] = {}

    for s in session_docs:
        raw_events = session_raw_events[s["session_id"]]
        try:
            ai_doc = await analyze_session_ai(s, raw_events)
        except Exception as exc:
            logger.warning("AI session analysis failed for %s: %s", s["session_id"], exc)
            ai_doc = None

        analysis = {
            "signals": s["detected_signals"],
            "actions_taken": s["actual_outcome"],
        }
        s_for_build = {
            "session_id": s["session_id"],
            "evidence_event_ids": session_evidence_ids.get(s["session_id"], []),
        }
        failures = await build_failures(inv_id, s_for_build, analysis)
        all_failures.extend(failures)

        if ai_doc is not None:
            payload = ai_doc.model_dump()
            if failures:
                payload["failure_id"] = failures[0]["failure_id"]
                ai_failures_by_session[s["session_id"]] = failures[0]["failure_id"]
            await ai_repo.insert_analysis(payload)

    if all_failures:
        await fail_repo.bulk_insert_failures(all_failures)

        by_session: dict[str, list[str]] = {}
        for f in all_failures:
            by_session.setdefault(f["session_id"], []).append(f["failure_id"])
        for sid, fids in by_session.items():
            await sess_repo.update_session(sid, {"failure_ids": fids})

    groups = await group_failures(inv_id, all_failures)

    from app.ai.group_analyzer import analyze_group_ai
    for g in groups:
        try:
            gf = [f for f in all_failures if f["failure_id"] in g["failure_ids"]]
            await analyze_group_ai(g, gf)
        except Exception as exc:
            logger.warning("Group AI analysis failed for %s: %s", g["group_id"], exc)

    # --- evaluation labels (isolated collection) ---
    gt_docs = [
        {
            "session_id": ds.session_id,
            "investigation_id": inv_id,
            "status": ds.ground_truth.status,
            "failure_type": ds.ground_truth.failure_type,
        }
        for ds in dataset.sessions
        if ds.ground_truth is not None
    ]
    if gt_docs:
        await mongo.get_database()["evaluation_labels"].insert_many(gt_docs, ordered=False)

    success = sum(1 for s in session_docs if s["session_status"] == "success")
    failure = sum(1 for s in session_docs if s["session_status"] == "failure")
    ambiguous = sum(1 for s in session_docs if s["session_status"] == "ambiguous")

    await inv_repo.update_investigation(inv_id, {
        "status": "completed",
        "total_sessions": len(session_docs),
        "successful_sessions": success,
        "failed_sessions": failure,
        "ambiguous_sessions": ambiguous,
        "failure_count": len(all_failures),
        "failure_group_count": len(groups),
        "completed_at": datetime.now(timezone.utc),
    })

    return {
        "investigation_id": inv_id,
        "sessions_ingested": len(session_docs),
        "failures_detected": len(all_failures),
        "groups_created": len(groups),
    }
