"""Human confirmation service."""

from typing import Protocol

from fortress_mcp.risk.confirmation_models import (
    ConfirmationDecision,
    ConfirmationRequest,
    ConfirmationResponse,
)


class ConfirmationProvider(Protocol):
    """Protocol for a human confirmation mechanism."""

    def request_confirmation(
        self,
        request: ConfirmationRequest,
    ) -> ConfirmationResponse:
        """Return the human decision."""
        ...


class DeterministicConfirmationProvider:
    """Small local confirmation provider for testing.

    The provider is intentionally injectable so that Streamlit or another
    user interface can supply the real human decision later.
    """

    def __init__(
        self,
        decisions: dict[str, ConfirmationDecision] | None = None,
    ) -> None:
        self._decisions = decisions or {}

    def request_confirmation(
        self,
        request: ConfirmationRequest,
    ) -> ConfirmationResponse:
        """Return a deterministic decision for the requested tool."""
        decision = self._decisions.get(
            request.tool_name,
            ConfirmationDecision.REJECTED,
        )

        if decision == ConfirmationDecision.APPROVED:
            return ConfirmationResponse(
                decision=decision,
                reason="Human confirmation approved the operation.",
            )

        return ConfirmationResponse(
            decision=ConfirmationDecision.REJECTED,
            reason="Human confirmation was not granted.",
        )


class ConfirmationService:
    """Coordinates explicit human confirmation."""

    def __init__(
        self,
        provider: ConfirmationProvider,
    ) -> None:
        self._provider = provider

    def confirm(
        self,
        request: ConfirmationRequest,
    ) -> ConfirmationResponse:
        """Obtain a human confirmation decision."""
        return self._provider.request_confirmation(request)
