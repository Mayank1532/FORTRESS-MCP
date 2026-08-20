"""Phase 6 MCP gateway and tool tests."""

from fortress_mcp.identity import (
    AuthenticationService,
    DeterministicAuthenticator,
)
from fortress_mcp.mcp.gateway import FortressGateway
from fortress_mcp.mcp.models import ToolRequest
from fortress_mcp.policy import PolicyEngine
from fortress_mcp.risk import (
    ConfirmationDecision,
    ConfirmationService,
    DeterministicConfirmationProvider,
    RiskClassifier,
)
from fortress_mcp.tools import build_tool_registry


def build_gateway(
    decisions: dict[str, ConfirmationDecision] | None = None,
) -> FortressGateway:
    """Build a deterministic gateway for tests."""
    authentication = AuthenticationService(
        DeterministicAuthenticator(
            {
                "agent-reader": ("reader-secret", "reader"),
                "agent-writer": ("writer-secret", "writer"),
                "agent-admin": ("admin-secret", "admin"),
            }
        )
    )

    confirmation = ConfirmationService(
        DeterministicConfirmationProvider(decisions)
    )

    return FortressGateway(
        authentication=authentication,
        policy=PolicyEngine(),
        risk=RiskClassifier(),
        confirmation=confirmation,
        registry=build_tool_registry(),
    )


def test_registered_tools_are_explicit() -> None:
    """Exactly the four locked FORTRESS tools are registered."""
    registry = build_tool_registry()

    assert {
        tool.name
        for tool in registry.list_tools()
    } == {
        "calculator_read",
        "weather_lookup",
        "update_record",
        "sensitive_action",
    }


def test_reader_can_execute_calculator() -> None:
    """A reader can execute the low-risk calculator."""
    gateway = build_gateway()

    response = gateway.execute(
        ToolRequest(
            agent_id="agent-reader",
            credential="reader-secret",
            tool_name="calculator_read",
            arguments={"expression": "2 + 3 * 4"},
        )
    )

    assert response.success is True
    assert response.result == 14
    assert response.decision == "allow"


def test_invalid_credentials_never_execute_tool() -> None:
    """Authentication failure blocks execution."""
    gateway = build_gateway()

    response = gateway.execute(
        ToolRequest(
            agent_id="agent-reader",
            credential="wrong-secret",
            tool_name="calculator_read",
            arguments={"expression": "2 + 2"},
        )
    )

    assert response.success is False
    assert response.decision == "unauthenticated"


def test_unknown_tool_is_denied() -> None:
    """Unknown tools cannot cross the execution boundary."""
    gateway = build_gateway()

    response = gateway.execute(
        ToolRequest(
            agent_id="agent-admin",
            credential="admin-secret",
            tool_name="unknown_tool",
            arguments={},
        )
    )

    assert response.success is False
    assert response.decision == "deny"


def test_reader_cannot_execute_update() -> None:
    """Least privilege blocks a reader from write operations."""
    gateway = build_gateway()

    response = gateway.execute(
        ToolRequest(
            agent_id="agent-reader",
            credential="reader-secret",
            tool_name="update_record",
            arguments={
                "record_id": "demo-1",
                "value": "blocked",
            },
        )
    )

    assert response.success is False
    assert response.decision == "deny"


def test_writer_update_requires_confirmation() -> None:
    """Write operations are blocked without confirmation."""
    gateway = build_gateway()

    response = gateway.execute(
        ToolRequest(
            agent_id="agent-writer",
            credential="writer-secret",
            tool_name="update_record",
            arguments={
                "record_id": "demo-1",
                "value": "blocked",
            },
        )
    )

    assert response.success is False
    assert response.decision == "deny"


def test_writer_update_executes_after_confirmation() -> None:
    """An approved write reaches the tool execution boundary."""
    gateway = build_gateway(
        {
            "update_record": ConfirmationDecision.APPROVED,
        }
    )

    response = gateway.execute(
        ToolRequest(
            agent_id="agent-writer",
            credential="writer-secret",
            tool_name="update_record",
            arguments={
                "record_id": "demo-1",
                "value": "approved",
            },
        )
    )

    assert response.success is True
    assert response.result == {
        "updated": True,
        "record_id": "demo-1",
        "value": "approved",
    }


def test_sensitive_action_requires_confirmation() -> None:
    """Sensitive actions cannot execute without confirmation."""
    gateway = build_gateway()

    response = gateway.execute(
        ToolRequest(
            agent_id="agent-admin",
            credential="admin-secret",
            tool_name="sensitive_action",
            arguments={"action": "rotate-demo-secret"},
        )
    )

    assert response.success is False
    assert response.decision == "deny"


def test_sensitive_action_can_execute_after_approval() -> None:
    """An approved sensitive action executes only after confirmation."""
    gateway = build_gateway(
        {
            "sensitive_action": ConfirmationDecision.APPROVED,
        }
    )

    response = gateway.execute(
        ToolRequest(
            agent_id="agent-admin",
            credential="admin-secret",
            tool_name="sensitive_action",
            arguments={"action": "rotate-demo-secret"},
        )
    )

    assert response.success is True
    assert response.result == {
        "executed": True,
        "action": "rotate-demo-secret",
        "simulated": True,
    }


def test_invalid_calculator_arguments_are_blocked() -> None:
    """Unsafe calculator syntax never reaches execution."""
    gateway = build_gateway()

    response = gateway.execute(
        ToolRequest(
            agent_id="agent-reader",
            credential="reader-secret",
            tool_name="calculator_read",
            arguments={
                "expression": "__import__('os').system('whoami')",
            },
        )
    )

    assert response.success is False
    assert response.decision == "validation_error"


def test_invalid_weather_coordinates_are_blocked() -> None:
    """Invalid geographic coordinates are rejected before the API call."""
    gateway = build_gateway()

    response = gateway.execute(
        ToolRequest(
            agent_id="agent-reader",
            credential="reader-secret",
            tool_name="weather_lookup",
            arguments={
                "latitude": 100,
                "longitude": 20,
            },
        )
    )

    assert response.success is False
    assert response.decision == "validation_error"
