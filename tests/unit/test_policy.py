"""Authorization and policy tests."""

from fortress_mcp.identity.models import AgentIdentity
from fortress_mcp.policy import (
    AuthorizationRequest,
    Permission,
    PolicyDecision,
    PolicyEngine,
)


def principal(agent_id: str = "agent-demo", role: str = "reader") -> AgentIdentity:
    """Create a test principal."""
    return AgentIdentity(
        agent_id=agent_id,
        role=role,
        session_id="session-test",
    )


def test_reader_can_use_read_tool() -> None:
    """A reader may use a read-only tool."""
    engine = PolicyEngine()

    result = engine.evaluate(
        AuthorizationRequest(
            principal=principal(),
            tool_name="calculator_read",
            permission=Permission.READ,
        )
    )

    assert result.decision == PolicyDecision.ALLOW


def test_reader_can_use_weather_lookup() -> None:
    """A reader may use the read-only weather tool."""
    engine = PolicyEngine()

    result = engine.evaluate(
        AuthorizationRequest(
            principal=principal(),
            tool_name="weather_lookup",
            permission=Permission.READ,
        )
    )

    assert result.decision == PolicyDecision.ALLOW


def test_reader_cannot_write() -> None:
    """A reader cannot use a write operation."""
    engine = PolicyEngine()

    result = engine.evaluate(
        AuthorizationRequest(
            principal=principal(),
            tool_name="update_record",
            permission=Permission.WRITE,
        )
    )

    assert result.decision == PolicyDecision.DENY
    assert result.reason == "Principal does not have the required permission."


def test_writer_requires_confirmation_for_update() -> None:
    """A writer may reach the confirmation boundary for writes."""
    engine = PolicyEngine()

    result = engine.evaluate(
        AuthorizationRequest(
            principal=principal(role="writer"),
                    session_id="session-test",
            tool_name="update_record",
            permission=Permission.WRITE,
        )
    )

    assert result.decision == PolicyDecision.REQUIRE_CONFIRMATION
    assert result.required_permission == Permission.WRITE


def test_admin_reaches_sensitive_confirmation_boundary() -> None:
    """An admin can reach, but not bypass, sensitive confirmation."""
    engine = PolicyEngine()

    result = engine.evaluate(
        AuthorizationRequest(
            principal=principal(role="admin"),
        session_id="session-test",
            tool_name="sensitive_action",
            permission=Permission.SENSITIVE,
        )
    )

    assert result.decision == PolicyDecision.REQUIRE_CONFIRMATION


def test_unknown_tool_is_denied() -> None:
    """Unknown tools fail closed."""
    engine = PolicyEngine()

    result = engine.evaluate(
        AuthorizationRequest(
            principal=principal(role="admin"),
            tool_name="unknown_tool",
            permission=Permission.READ,
        )
    )

    assert result.decision == PolicyDecision.DENY
    assert result.reason == "Unknown tool."


def test_permission_mismatch_is_denied() -> None:
    """The requested permission must match the registered tool policy."""
    engine = PolicyEngine()

    result = engine.evaluate(
        AuthorizationRequest(
            principal=principal(role="admin"),
            tool_name="calculator_read",
            permission=Permission.WRITE,
        )
    )

    assert result.decision == PolicyDecision.DENY
    assert result.reason == (
        "Requested permission does not match tool policy."
    )


def test_unknown_role_is_denied() -> None:
    """Unknown roles receive no implicit permissions."""
    engine = PolicyEngine()

    result = engine.evaluate(
        AuthorizationRequest(
            principal=principal(role="unknown"),
            tool_name="calculator_read",
            permission=Permission.READ,
        )
    )

    assert result.decision == PolicyDecision.DENY


def test_custom_policy_can_be_injected() -> None:
    """Policy configuration can be replaced through dependency injection."""
    from fortress_mcp.policy.config import ToolPolicy

    engine = PolicyEngine(
        tool_policies={
            "custom_read": ToolPolicy(permission=Permission.READ),
        }
    )

    result = engine.evaluate(
        AuthorizationRequest(
            principal=principal(),
            tool_name="custom_read",
            permission=Permission.READ,
        )
    )

    assert result.decision == PolicyDecision.ALLOW
