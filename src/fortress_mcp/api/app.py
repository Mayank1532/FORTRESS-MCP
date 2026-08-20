"""FORTRESS-MCP HTTP API."""

from os import getenv

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from fortress_mcp.audit import AuditRecorder
from fortress_mcp.core.health import health_check
from fortress_mcp.identity import (
    AgentIdentity,
    AuthenticationRequest,
    AuthenticationService,
    DeterministicAuthenticator,
)
from fortress_mcp.mcp.gateway import FortressGateway
from fortress_mcp.mcp.models import ToolRequest
from fortress_mcp.policy import Permission, PolicyEngine
from fortress_mcp.risk import (
    ConfirmationService,
    DeterministicConfirmationProvider,
    RiskClassifier,
)
from fortress_mcp.tools import build_tool_registry

ROLE_PERMISSIONS: dict[str, tuple[Permission, ...]] = {
    "reader": (Permission.READ,),
    "writer": (Permission.READ, Permission.WRITE),
    "admin": (
        Permission.READ,
        Permission.WRITE,
        Permission.SENSITIVE,
    ),
}

_AUDIT_RECORDER = AuditRecorder()


class SecurityIdentityRequest(BaseModel):
    """HTTP request for identity authentication."""

    agent_id: str = Field(min_length=1, max_length=128)
    credential: str = Field(min_length=1, max_length=256)
    session_id: str = Field(min_length=1, max_length=128)


class SecurityIdentityResponse(BaseModel):
    """Authenticated identity information for the control center."""

    authenticated: bool
    agent_id: str
    session_id: str
    role: str | None = None
    permissions: list[str] = Field(default_factory=list)
    reason: str


class SecurityExecuteRequest(BaseModel):
    """HTTP request for protected FORTRESS tool execution."""

    agent_id: str = Field(min_length=1, max_length=128)
    credential: str = Field(min_length=1, max_length=256)
    session_id: str = Field(min_length=1, max_length=128)
    tool_name: str = Field(min_length=1, max_length=128)
    arguments: dict[str, object] = Field(default_factory=dict)


class SecurityExecuteResponse(BaseModel):
    """Stable HTTP response for a FORTRESS security decision."""

    success: bool
    status: str
    tool_name: str
    result: object | None = None
    reason: str | None = None
    risk_level: str | None = None
    confirmation_required: bool = False
    audit_event_id: str | None = None


class AuditResponse(BaseModel):
    """Safe audit-event representation for API clients."""

    event_id: str
    event_type: str
    agent_id: str
    tool_name: str
    decision: str
    reason: str
    metadata: dict[str, object]
    timestamp: str


app = FastAPI(
    title="FORTRESS-MCP",
    description="Zero-trust security gateway for AI-agent tool execution.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Return service health."""
    return health_check()


def _credentials_from_environment() -> dict[str, tuple[str, str]]:
    """Build deterministic local credentials from environment variables."""
    credentials: dict[str, tuple[str, str]] = {}

    reader_credential = getenv("FORTRESS_READER_CREDENTIAL")
    writer_credential = getenv("FORTRESS_WRITER_CREDENTIAL")
    admin_credential = getenv("FORTRESS_ADMIN_CREDENTIAL")

    if reader_credential:
        credentials["agent-reader"] = (
            reader_credential,
            "reader",
        )

    if writer_credential:
        credentials["agent-writer"] = (
            writer_credential,
            "writer",
        )

    if admin_credential:
        credentials["agent-admin"] = (
            admin_credential,
            "admin",
        )

    return credentials


def _build_authentication() -> AuthenticationService:
    """Build the deterministic authentication boundary."""
    return AuthenticationService(
        DeterministicAuthenticator(
            _credentials_from_environment()
        )
    )


def _build_gateway() -> FortressGateway:
    """Build the application's deterministic security gateway."""
    return FortressGateway(
        authentication=_build_authentication(),
        policy=PolicyEngine(),
        risk=RiskClassifier(),
        confirmation=ConfirmationService(
            DeterministicConfirmationProvider()
        ),
        registry=build_tool_registry(),
        audit_recorder=_AUDIT_RECORDER,
    )


@app.post(
    "/v1/security/identity",
    response_model=SecurityIdentityResponse,
)
def security_identity(
    request: SecurityIdentityRequest,
) -> SecurityIdentityResponse:
    """Authenticate an agent for the security control center."""
    result = _build_authentication().authenticate(
        AuthenticationRequest(
            agent_id=request.agent_id,
            credential=request.credential,
            session_id=request.session_id,
        )
    )

    if result.principal is None:
        return SecurityIdentityResponse(
            authenticated=False,
            agent_id=request.agent_id,
            session_id=request.session_id,
            reason=result.reason,
        )

    principal: AgentIdentity = result.principal
    permissions = ROLE_PERMISSIONS.get(principal.role, ())

    return SecurityIdentityResponse(
        authenticated=True,
        agent_id=principal.agent_id,
        session_id=principal.session_id,
        role=principal.role,
        permissions=[permission.value for permission in permissions],
        reason=result.reason,
    )


@app.post(
    "/v1/security/execute",
    response_model=SecurityExecuteResponse,
)
def security_execute(
    request: SecurityExecuteRequest,
) -> SecurityExecuteResponse:
    """Execute a tool through the FORTRESS security boundary."""
    gateway = _build_gateway()

    tool_request = ToolRequest(
        agent_id=request.agent_id,
        credential=request.credential,
        session_id=request.session_id,
        tool_name=request.tool_name,
        arguments=request.arguments,
    )

    try:
        response = gateway.execute(tool_request)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="FORTRESS execution failure.",
        ) from exc

    risk_level = (
        response.risk_level.value
        if response.risk_level is not None
        else None
    )

    return SecurityExecuteResponse(
        success=response.success,
        status=response.decision,
        tool_name=response.tool_name,
        result=response.result,
        reason=response.reason,
        risk_level=risk_level,
        confirmation_required=response.confirmation_required,
        audit_event_id=response.audit_event_id,
    )


@app.get(
    "/v1/security/audit",
    response_model=list[AuditResponse],
)
def security_audit(
    limit: int = Query(default=50, ge=1, le=200),
) -> list[AuditResponse]:
    """Return recent safe audit events."""
    events = _AUDIT_RECORDER.recent(limit)

    return [
        AuditResponse(
            event_id=event.event_id,
            event_type=event.event_type.value,
            agent_id=event.agent_id,
            tool_name=event.tool_name,
            decision=event.decision,
            reason=event.reason,
            metadata=event.metadata,
            timestamp=event.timestamp.isoformat(),
        )
        for event in events
    ]


def reset_runtime() -> None:
    """Reset in-memory runtime telemetry for deterministic tests."""
    _AUDIT_RECORDER.clear()
