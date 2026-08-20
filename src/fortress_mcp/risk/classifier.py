"""Deterministic risk classifier."""

from collections.abc import Mapping

from fortress_mcp.policy.models import PolicyDecision
from fortress_mcp.risk.models import (
    RiskAssessmentRequest,
    RiskAssessmentResult,
    RiskLevel,
)


class RiskClassifier:
    """Classifies authorized operations by deterministic risk rules."""

    def __init__(
        self,
        tool_risk_levels: Mapping[str, RiskLevel] | None = None,
    ) -> None:
        self._tool_risk_levels = dict(
            tool_risk_levels
            if tool_risk_levels is not None
            else {
                "calculator_read": RiskLevel.LOW,
                "weather_lookup": RiskLevel.MEDIUM,
                "update_record": RiskLevel.HIGH,
                "sensitive_action": RiskLevel.HIGH,
            }
        )

    def assess(
        self,
        request: RiskAssessmentRequest,
    ) -> RiskAssessmentResult:
        """Return the risk classification for a policy decision."""
        if request.policy_decision == PolicyDecision.DENY:
            return RiskAssessmentResult(
                risk_level=RiskLevel.HIGH,
                requires_confirmation=False,
                reason="Denied operations are blocked before execution.",
            )

        risk_level = self._tool_risk_levels.get(
            request.tool_name,
            RiskLevel.HIGH,
        )

        requires_confirmation = (
            request.policy_decision == PolicyDecision.REQUIRE_CONFIRMATION
            or risk_level == RiskLevel.HIGH
        )

        return RiskAssessmentResult(
            risk_level=risk_level,
            requires_confirmation=requires_confirmation,
            reason=self._reason_for(risk_level, requires_confirmation),
        )

    @staticmethod
    def _reason_for(
        risk_level: RiskLevel,
        requires_confirmation: bool,
    ) -> str:
        """Build an explainable risk reason."""
        if requires_confirmation:
            return f"{risk_level.value} risk operation requires confirmation."

        return f"{risk_level.value} risk operation does not require confirmation."

