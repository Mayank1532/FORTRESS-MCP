"""Human confirmation domain models."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from fortress_mcp.risk.models import RiskLevel


class ConfirmationDecision(StrEnum):
    """Possible human confirmation outcomes."""

    APPROVED = "approved"
    REJECTED = "rejected"


class ConfirmationRequest(BaseModel):
    """Request presented to the human confirmation boundary."""

    model_config = ConfigDict(frozen=True)

    agent_id: str = Field(min_length=1, max_length=128)
    tool_name: str = Field(min_length=1, max_length=128)
    risk_level: RiskLevel
    reason: str = Field(min_length=1, max_length=512)


class ConfirmationResponse(BaseModel):
    """Human response to a confirmation request."""

    decision: ConfirmationDecision
    reason: str = Field(min_length=1, max_length=512)
