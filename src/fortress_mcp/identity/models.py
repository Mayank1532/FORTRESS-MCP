"""Identity and authentication domain models."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class AuthenticationStatus(StrEnum):
    """Possible authentication outcomes."""

    AUTHENTICATED = "authenticated"
    UNAUTHENTICATED = "unauthenticated"


class AgentIdentity(BaseModel):
    """Represents the identity presented by an AI agent."""

    model_config = ConfigDict(frozen=True)

    agent_id: str = Field(min_length=1, max_length=128)
    role: str = Field(min_length=1, max_length=64)


class AuthenticationRequest(BaseModel):
    """Input required to authenticate an agent."""

    agent_id: str = Field(min_length=1, max_length=128)
    credential: str = Field(min_length=1, max_length=256)


class AuthenticationResult(BaseModel):
    """Result returned by the authentication boundary."""

    status: AuthenticationStatus
    principal: AgentIdentity | None = None
    reason: str
