"""Authentication implementation boundary."""

from typing import Protocol

from fortress_mcp.identity.models import (
    AgentIdentity,
    AuthenticationRequest,
)


class Authenticator(Protocol):
    """Protocol for replaceable authentication implementations."""

    def authenticate(
        self,
        request: AuthenticationRequest,
    ) -> AgentIdentity | None:
        """Authenticate a request and return its identity if valid."""
        ...


class DeterministicAuthenticator:
    """Small deterministic authenticator for local development and testing.

    This implementation deliberately avoids external identity providers.
    A production deployment can replace it behind the same protocol.
    """

    def __init__(self, credentials: dict[str, tuple[str, str]]) -> None:
        self._credentials = credentials

    def authenticate(
        self,
        request: AuthenticationRequest,
    ) -> AgentIdentity | None:
        """Authenticate using deterministic local credentials."""
        record = self._credentials.get(request.agent_id)

        if record is None:
            return None

        expected_credential, role = record

        if request.credential != expected_credential:
            return None

        return AgentIdentity(
            agent_id=request.agent_id,
            role=role,
            session_id=request.session_id,
        )
