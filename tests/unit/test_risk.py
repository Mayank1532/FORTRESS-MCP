"""Risk classification and human confirmation tests."""

from fortress_mcp.policy.models import PolicyDecision
from fortress_mcp.risk import (
    ConfirmationDecision,
    ConfirmationRequest,
    ConfirmationService,
    DeterministicConfirmationProvider,
    RiskAssessmentRequest,
    RiskClassifier,
    RiskLevel,
)


def test_low_risk_operation_does_not_require_confirmation() -> None:
    """Low-risk allowed operations can proceed without confirmation."""
    classifier = RiskClassifier()

    result = classifier.assess(
        RiskAssessmentRequest(
            tool_name="calculator_read",
            policy_decision=PolicyDecision.ALLOW,
        )
    )

    assert result.risk_level == RiskLevel.LOW
    assert result.requires_confirmation is False


def test_medium_risk_operation_is_classified_correctly() -> None:
    """Weather lookup is classified as medium risk."""
    classifier = RiskClassifier()

    result = classifier.assess(
        RiskAssessmentRequest(
            tool_name="weather_lookup",
            policy_decision=PolicyDecision.ALLOW,
        )
    )

    assert result.risk_level == RiskLevel.MEDIUM
    assert result.requires_confirmation is False


def test_high_risk_operation_requires_confirmation() -> None:
    """High-risk operations require explicit human confirmation."""
    classifier = RiskClassifier()

    result = classifier.assess(
        RiskAssessmentRequest(
            tool_name="update_record",
            policy_decision=PolicyDecision.REQUIRE_CONFIRMATION,
        )
    )

    assert result.risk_level == RiskLevel.HIGH
    assert result.requires_confirmation is True


def test_sensitive_operation_is_high_risk() -> None:
    """Sensitive operations are classified as high risk."""
    classifier = RiskClassifier()

    result = classifier.assess(
        RiskAssessmentRequest(
            tool_name="sensitive_action",
            policy_decision=PolicyDecision.REQUIRE_CONFIRMATION,
        )
    )

    assert result.risk_level == RiskLevel.HIGH
    assert result.requires_confirmation is True


def test_denied_operation_never_requires_confirmation() -> None:
    """A denied operation remains blocked rather than becoming confirmable."""
    classifier = RiskClassifier()

    result = classifier.assess(
        RiskAssessmentRequest(
            tool_name="update_record",
            policy_decision=PolicyDecision.DENY,
        )
    )

    assert result.risk_level == RiskLevel.HIGH
    assert result.requires_confirmation is False


def test_unknown_tool_fails_closed_to_high_risk() -> None:
    """Unknown tools receive the safest risk classification."""
    classifier = RiskClassifier()

    result = classifier.assess(
        RiskAssessmentRequest(
            tool_name="unknown_tool",
            policy_decision=PolicyDecision.ALLOW,
        )
    )

    assert result.risk_level == RiskLevel.HIGH
    assert result.requires_confirmation is True


def test_confirmation_can_be_approved() -> None:
    """An injected confirmation provider can approve an operation."""
    provider = DeterministicConfirmationProvider(
        decisions={
            "update_record": ConfirmationDecision.APPROVED,
        }
    )
    service = ConfirmationService(provider)

    response = service.confirm(
        ConfirmationRequest(
            agent_id="agent-writer",
            tool_name="update_record",
            risk_level=RiskLevel.HIGH,
            reason="Write operation requires human confirmation.",
        )
    )

    assert response.decision == ConfirmationDecision.APPROVED


def test_confirmation_defaults_to_rejected() -> None:
    """Missing confirmation must fail closed."""
    provider = DeterministicConfirmationProvider()
    service = ConfirmationService(provider)

    response = service.confirm(
        ConfirmationRequest(
            agent_id="agent-writer",
            tool_name="update_record",
            risk_level=RiskLevel.HIGH,
            reason="Write operation requires human confirmation.",
        )
    )

    assert response.decision == ConfirmationDecision.REJECTED


def test_confirmation_can_be_explicitly_rejected() -> None:
    """An explicit rejection blocks the operation."""
    provider = DeterministicConfirmationProvider(
        decisions={
            "update_record": ConfirmationDecision.REJECTED,
        }
    )
    service = ConfirmationService(provider)

    response = service.confirm(
        ConfirmationRequest(
            agent_id="agent-writer",
            tool_name="update_record",
            risk_level=RiskLevel.HIGH,
            reason="Write operation requires human confirmation.",
        )
    )

    assert response.decision == ConfirmationDecision.REJECTED


def test_confirmation_service_uses_injected_provider() -> None:
    """Confirmation is replaceable through dependency injection."""
    class StubProvider:
        def request_confirmation(
            self,
            request: ConfirmationRequest,
        ) -> object:
            return type(
                "StubResponse",
                (),
                {
                    "decision": ConfirmationDecision.APPROVED,
                    "reason": "Stub approval.",
                },
            )()

    service = ConfirmationService(StubProvider())

    response = service.confirm(
        ConfirmationRequest(
            agent_id="agent-demo",
            tool_name="custom_sensitive",
            risk_level=RiskLevel.HIGH,
            reason="Test confirmation.",
        )
    )

    assert response.decision == ConfirmationDecision.APPROVED
