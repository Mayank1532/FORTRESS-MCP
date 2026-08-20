"""Application service for the authentication boundary."""

from fortress_mcp.identity.authenticator import Authenticator
from fortress_mcp.identity.models import (
    AuthenticationRequest,
    AuthenticationResult,
    AuthenticationStatus,
)


class AuthenticationService:
    """Coordinates authentication without performing authorization."""

    def __init__(self, authenticator: Authenticator) -> None:
        self._authenticator = authenticator

    def authenticate(
        self,
        request: AuthenticationRequest,
    ) -> AuthenticationResult:
        """Authenticate the requester."""
        principal = self._authenticator.authenticate(request)

        if principal is None:
            return AuthenticationResult(
                status=AuthenticationStatus.UNAUTHENTICATED,
                reason="Invalid agent credentials.",
            )

        return AuthenticationResult(
            status=AuthenticationStatus.AUTHENTICATED,
            principal=principal,
            reason="Authentication successful.",
        )
