"""Identity and authentication tests."""

from fortress_mcp.identity.authenticator import DeterministicAuthenticator
from fortress_mcp.identity.models import (
    AgentIdentity,
    AuthenticationRequest,
    AuthenticationStatus,
)
from fortress_mcp.identity.service import AuthenticationService


def build_service() -> AuthenticationService:
    """Create the deterministic authentication service used by tests."""
    authenticator = DeterministicAuthenticator(
        credentials={
            "agent-demo": ("demo-secret", "reader"),
            "agent-admin": ("admin-secret", "admin"),
        }
    )

    return AuthenticationService(authenticator)


def test_valid_credentials_authenticate_agent() -> None:
    """Valid credentials produce an authenticated principal."""
    service = build_service()

    result = service.authenticate(
        AuthenticationRequest(
            agent_id="agent-demo",
credential="demo-secret",
            session_id="session-test",
        )
    )

    assert result.status == AuthenticationStatus.AUTHENTICATED
    assert result.principal == AgentIdentity(
        agent_id="agent-demo",
        role="reader",
        session_id="session-test",
    )


def test_invalid_credentials_are_rejected() -> None:
    """Invalid credentials produce an unauthenticated result."""
    service = build_service()

    result = service.authenticate(
        AuthenticationRequest(
            agent_id="agent-demo",
credential="wrong-secret",
            session_id="session-test",
        )
    )

    assert result.status == AuthenticationStatus.UNAUTHENTICATED
    assert result.principal is None
    assert result.reason == "Invalid agent credentials."


def test_unknown_agent_is_rejected() -> None:
    """Unknown identities cannot authenticate."""
    service = build_service()

    result = service.authenticate(
        AuthenticationRequest(
            agent_id="unknown-agent",
credential="anything",
            session_id="session-test",
        )
    )

    assert result.status == AuthenticationStatus.UNAUTHENTICATED
    assert result.principal is None


def test_authenticator_is_replaceable() -> None:
    """The service depends on the Authenticator protocol."""
    class StubAuthenticator:
        def authenticate(
            self,
            request: AuthenticationRequest,
        ) -> AgentIdentity:
            return AgentIdentity(
                agent_id=request.agent_id,
                role="stub",
        session_id="session-test",
            )

    service = AuthenticationService(StubAuthenticator())

    result = service.authenticate(
        AuthenticationRequest(
            agent_id="test-agent",
credential="test",
            session_id="session-test",
        )
    )

    assert result.status == AuthenticationStatus.AUTHENTICATED
    assert result.principal is not None
    assert result.principal.role == "stub"
