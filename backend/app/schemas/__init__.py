from .common import AgentLensBaseModel, APIError, APIResponse, TimestampedModel
from .enums import (
    ActionStatus, Actor, AnalysisStatus, EventType, FailureStatus,
    FailureType, InvestigationStatus, SessionStatus, Severity,
)
from .investigations import (
    CreateInvestigationRequest, InvestigationResponse, InvestigationStats,
)
from .datasets import DatasetImport, DatasetSession, GroundTruth
from .events import AgentEvent
from .sessions import ActionOutcome, SessionDocument, SessionDetailResponse
from .failures import (
    EvidenceItem, FailureDocument, FailureDetailResponse, FailureClassification,
)
from .failure_groups import FailureGroupDocument, FailureGroupDetailResponse
from .ai_analysis import (
    AIAnalysisDocument, AIClassification, GroupAIAnalysis,
    InvestigationAssistantRequest, InvestigationAssistantResponse,
    AssistantEvidence,
)
from .dashboard import (
    DashboardSummary, DashboardResponse, FailureDistribution,
    SeverityDistribution, FailureGroupSummary,
)
from .export import ExportResponse

# --- resolve forward references now that all modules are loaded ---
SessionDetailResponse.model_rebuild()
FailureDetailResponse.model_rebuild()
FailureGroupDetailResponse.model_rebuild()

__all__ = [
    "AgentLensBaseModel", "APIError", "APIResponse", "TimestampedModel",
    "ActionStatus", "Actor", "AnalysisStatus", "EventType", "FailureStatus",
    "FailureType", "InvestigationStatus", "SessionStatus", "Severity",
    "CreateInvestigationRequest", "InvestigationResponse", "InvestigationStats",
    "DatasetImport", "DatasetSession", "GroundTruth",
    "ActionOutcome", "SessionDocument", "SessionDetailResponse",
    "AgentEvent", "EvidenceItem", "FailureDocument", "FailureDetailResponse",
    "FailureClassification", "FailureGroupDocument",
    "AIAnalysisDocument", "AIClassification", "GroupAIAnalysis",
    "InvestigationAssistantRequest", "InvestigationAssistantResponse",
    "AssistantEvidence",
    "DashboardSummary", "DashboardResponse", "FailureDistribution",
    "SeverityDistribution", "FailureGroupSummary",
    "ExportResponse",
]
