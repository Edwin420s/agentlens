from app.db.repositories import (
    failure_groups as fg_repo,
    failures as fail_repo,
    sessions as sess_repo,
    investigations as inv_repo,
)
from app.schemas.dashboard import (
    DashboardResponse,
    DashboardSummary,
    FailureDistribution,
    FailureGroupSummary,
    SeverityDistribution,
)


async def build_dashboard(investigation_id: str) -> DashboardResponse | None:
    inv = await inv_repo.get_investigation(investigation_id)
    if not inv:
        return None

    failures = await fail_repo.list_all_failures(investigation_id)
    groups = await fg_repo.list_groups(investigation_id)

    total_failures = len(failures)
    critical = sum(1 for f in failures if f["severity"] == "critical")
    avg_conf = (sum(f["confidence"] for f in failures) / total_failures) if failures else 0.0

    ftype_counts: dict[str, int] = {}
    sev_counts: dict[str, int] = {}
    for f in failures:
        ftype_counts[f["failure_type"]] = ftype_counts.get(f["failure_type"], 0) + 1
        sev_counts[f["severity"]] = sev_counts.get(f["severity"], 0) + 1

    recent = sorted(failures, key=lambda f: f["created_at"], reverse=True)[:10]

    summary = DashboardSummary(
        total_sessions=inv.get("total_sessions", 0),
        successful_sessions=inv.get("successful_sessions", 0),
        failed_sessions=inv.get("failed_sessions", 0),
        ambiguous_sessions=inv.get("ambiguous_sessions", 0),
        total_failures=total_failures,
        total_groups=len(groups),
        critical_failures=critical,
        average_confidence=round(avg_conf, 3),
    )

    failure_distribution = [
        FailureDistribution(failure_type=ft, count=c)
        for ft, c in ftype_counts.items()
    ]
    severity_distribution = [
        SeverityDistribution(severity=s, count=c)
        for s, c in sev_counts.items()
    ]

    group_summaries = [
        FailureGroupSummary(
            group_id=g["group_id"],
            title=g["title"],
            failure_type=g["failure_type"],
            occurrence_count=g["occurrence_count"],
            severity=g["severity"],
            confidence=g["confidence"],
            status=g["status"],
        )
        for g in groups
    ]

    recent_serializable = [
        {
            "failure_id": f["failure_id"],
            "failure_type": f["failure_type"],
            "severity": f["severity"],
            "title": f["title"],
            "session_id": f["session_id"],
        }
        for f in recent
    ]

    return DashboardResponse(
        investigation_id=investigation_id,
        summary=summary,
        failure_distribution=failure_distribution,
        severity_distribution=severity_distribution,
        groups=group_summaries,
        recent_failures=recent_serializable,
    )
