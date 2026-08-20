"""FORTRESS security gateway for MCP tool execution."""

from fortress_mcp.identity import (
    AuthenticationRequest,
    AuthenticationService,
)
from fortress_mcp.mcp.models import ToolRequest, ToolResponse
from fortress_mcp.mcp.registry import ToolRegistry
from fortress_mcp.policy import (
    AuthorizationRequest,
    PolicyDecision,
    PolicyEngine,
)
from fortress_mcp.risk import (
    ConfirmationDecision,
    ConfirmationRequest,
    ConfirmationService,
    RiskAssessmentRequest,
    RiskClassifier,
)
from fortress_mcp.tools.registry import TOOL_PERMISSIONS


class FortressGateway:
    """Enforce FORTRESS security controls before tool execution."""

    def __init__(
        self,
        authentication: AuthenticationService,
        policy: PolicyEngine,
        risk: RiskClassifier,
        confirmation: ConfirmationService,
        registry: ToolRegistry,
    ) -> None:
        self._authentication = authentication
        self._policy = policy
        self._risk = risk
        self._confirmation = confirmation
        self._registry = registry

    def execute(self, request: ToolRequest) -> ToolResponse:
        """Authenticate, authorize, assess risk, confirm, then execute."""
        authentication = self._authentication.authenticate(
            AuthenticationRequest(
                agent_id=request.agent_id,
                credential=request.credential,
            )
        )

        if authentication.principal is None:
            return ToolResponse(
                success=False,
                tool_name=request.tool_name,
                decision="unauthenticated",
                reason=authentication.reason,
            )

        if not self._registry.contains(request.tool_name):
            return ToolResponse(
                success=False,
                tool_name=request.tool_name,
                decision="deny",
                reason="Unknown tool.",
            )

        permission = TOOL_PERMISSIONS.get(request.tool_name)

        if permission is None:
            return ToolResponse(
                success=False,
                tool_name=request.tool_name,
                decision="deny",
                reason="Tool permission is not registered.",
            )

        authorization = self._policy.evaluate(
            AuthorizationRequest(
                principal=authentication.principal,
                tool_name=request.tool_name,
                permission=permission,
            )
        )

        risk = self._risk.assess(
            RiskAssessmentRequest(
                tool_name=request.tool_name,
                policy_decision=authorization.decision,
            )
        )

        if authorization.decision == PolicyDecision.DENY:
            return ToolResponse(
                success=False,
                tool_name=request.tool_name,
                decision=authorization.decision.value,
                reason=authorization.reason,
            )

        if risk.requires_confirmation:
            confirmation = self._confirmation.confirm(
                ConfirmationRequest(
                    agent_id=authentication.principal.agent_id,
                    tool_name=request.tool_name,
                    risk_level=risk.risk_level,
                    reason=risk.reason,
                )
            )

            if confirmation.decision != ConfirmationDecision.APPROVED:
                return ToolResponse(
                    success=False,
                    tool_name=request.tool_name,
                    decision="deny",
                    reason=confirmation.reason,
                )

        registered = self._registry.get(request.tool_name)

        if registered is None:
            return ToolResponse(
                success=False,
                tool_name=request.tool_name,
                decision="deny",
                reason="Tool disappeared from registry.",
            )

        _definition, handler = registered

        try:
            result = handler(request.arguments)
        except (ValueError, TypeError) as exc:
            return ToolResponse(
                success=False,
                tool_name=request.tool_name,
                decision="validation_error",
                reason=str(exc),
            )
        except RuntimeError as exc:
            return ToolResponse(
                success=False,
                tool_name=request.tool_name,
                decision="execution_error",
                reason=str(exc),
            )

        return ToolResponse(
            success=True,
            tool_name=request.tool_name,
            result=result,
            decision=PolicyDecision.ALLOW.value,
            reason="Security checks passed and tool executed.",
        )
