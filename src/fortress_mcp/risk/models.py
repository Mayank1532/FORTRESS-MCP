"""Risk classification domain models."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from fortress_mcp.policy.models import PolicyDecision


class RiskLevel(StrEnum):
    """Risk levels assigned to authorized operations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskAssessmentRequest(BaseModel):
    """Input to the risk classification boundary."""

    model_config = ConfigDict(frozen=True)

    tool_name: str = Field(min_length=1, max_length=128)
    policy_decision: PolicyDecision


class RiskAssessmentResult(BaseModel):
    """Deterministic risk classification result."""

    risk_level: RiskLevel
    requires_confirmation: bool
    reason: str
