"""FORTRESS-MCP HTTP API."""

from os import getenv

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from fortress_mcp.core.health import health_check
from fortress_mcp.identity import (
    AuthenticationService,
    DeterministicAuthenticator,
)
from fortress_mcp.mcp.gateway import FortressGateway
from fortress_mcp.mcp.models import ToolRequest
from fortress_mcp.policy import PolicyEngine
from fortress_mcp.risk import (
    ConfirmationService,
    DeterministicConfirmationProvider,
    RiskClassifier,
)
from fortress_mcp.tools import build_tool_registry


class SecurityExecuteRequest(BaseModel):
    """HTTP request for protected FORTRESS tool execution."""

    agent_id: str = Field(min_length=1, max_length=128)
    credential: str = Field(min_length=1, max_length=256)
    session_id: str = Field(min_length=1, max_length=128)
    tool_name: str = Field(min_length=1, max_length=128)
    arguments: dict[str, object] = Field(default_factory=dict)


class SecurityExecuteResponse(BaseModel):
    """Stable HTTP response for a FORTRESS security decision."""

    status: str
    tool_name: str
    result: object | None = None
    reason: str | None = None
    risk_level: str | None = None
    confirmation_required: bool = False
    audit_event_id: str | None = None


app = FastAPI(
    title="FORTRESS-MCP",
    description="Zero-trust security gateway for AI-agent tool execution.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Return service health."""
    return health_check()


def _build_gateway() -> FortressGateway:
    """Build the application's deterministic security gateway."""
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

    authenticator = DeterministicAuthenticator(credentials)

    return FortressGateway(
        AuthenticationService(authenticator),
        PolicyEngine(),
        RiskClassifier(),
        ConfirmationService(
            DeterministicConfirmationProvider()
        ),
        build_tool_registry(),
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

    return SecurityExecuteResponse(
        status=response.decision,
        tool_name=response.tool_name,
        result=response.result,
        reason=response.reason,
        risk_level=None,
        confirmation_required=False,
        audit_event_id=None,
    )
