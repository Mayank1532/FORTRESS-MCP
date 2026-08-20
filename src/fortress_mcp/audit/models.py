"""Security audit event contracts."""

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class AuditEventType(StrEnum):
    """Security-relevant audit event categories."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    INJECTION = "injection"
    CONFIRMATION = "confirmation"
    TOOL_EXECUTION = "tool_execution"
    TOOL_FAILURE = "tool_failure"


class AuditEvent(BaseModel):
    """Structured security audit event."""

    model_config = ConfigDict(frozen=True)

    event_id: str = Field(
        default_factory=lambda: str(uuid4()),
        min_length=1,
        max_length=64,
    )
    event_type: AuditEventType
    agent_id: str
    tool_name: str
    decision: str
    reason: str
    metadata: dict[str, object] = Field(default_factory=dict)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )
