from pydantic import Field

from .common import AgentLensBaseModel
from .enums import FailureStatus, FailureType, Severity


class DashboardSummary(AgentLensBaseModel):
    total_sessions: int = Field(ge=0)
    successful_sessions: int = Field(ge=0)
    failed_sessions: int = Field(ge=0)
    ambiguous_sessions: int = Field(ge=0)

    total_failures: int = Field(ge=0)
    total_groups: int = Field(ge=0)

    critical_failures: int = Field(ge=0)

    average_confidence: float = Field(
        ge=0.0,
        le=1.0,
    )


class FailureDistribution(AgentLensBaseModel):
    failure_type: FailureType
    count: int = Field(ge=0)


class SeverityDistribution(AgentLensBaseModel):
    severity: Severity
    count: int = Field(ge=0)


class FailureGroupSummary(AgentLensBaseModel):
    group_id: str
    title: str
    failure_type: FailureType
    occurrence_count: int = Field(ge=1)
    severity: Severity
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )
    status: FailureStatus


class DashboardResponse(AgentLensBaseModel):
    investigation_id: str

    summary: DashboardSummary

    failure_distribution: list[
        FailureDistribution
    ]

    severity_distribution: list[
        SeverityDistribution
    ]

    groups: list[FailureGroupSummary]

    recent_failures: list[
        dict
    ]
