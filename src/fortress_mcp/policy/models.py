"""Authorization and policy domain models."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from fortress_mcp.identity.models import AgentIdentity


class Permission(StrEnum):
    """Permissions understood by the FORTRESS policy engine."""

    READ = "read"
    WRITE = "write"
    SENSITIVE = "sensitive"


class PolicyDecision(StrEnum):
    """Possible policy outcomes."""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_CONFIRMATION = "require_confirmation"


class AuthorizationRequest(BaseModel):
    """Request evaluated by the authorization policy."""

    model_config = ConfigDict(frozen=True)

    principal: AgentIdentity
    tool_name: str = Field(min_length=1, max_length=128)
    permission: Permission


class AuthorizationResult(BaseModel):
    """Deterministic result returned by the policy engine."""

    decision: PolicyDecision
    reason: str
    required_permission: Permission
