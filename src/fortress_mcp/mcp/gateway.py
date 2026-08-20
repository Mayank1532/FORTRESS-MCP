"""FORTRESS security gateway for MCP tool execution."""

from fortress_mcp.audit import (
    AuditEvent,
    AuditEventType,
    AuditRecorder,
    redact_mapping,
)
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
    RiskLevel,
)
from fortress_mcp.security.injection import PromptInjectionDetector
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
        injection_detector: PromptInjectionDetector | None = None,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._authentication = authentication
        self._policy = policy
        self._risk = risk
        self._confirmation = confirmation
        self._registry = registry
        self._injection_detector = injection_detector or PromptInjectionDetector()
        self._audit = audit_recorder or AuditRecorder()

    @property
    def audit(self) -> AuditRecorder:
        """Return the gateway audit recorder."""
        return self._audit

    def _record(
        self,
        *,
        event_type: AuditEventType,
        request: ToolRequest,
        decision: str,
        reason: str,
        metadata: dict[str, object] | None = None,
    ) -> str:
        """Record a redacted security event and return its ID."""
        safe_metadata = redact_mapping(metadata or {})

        event = AuditEvent(
            event_type=event_type,
            agent_id=request.agent_id,
            tool_name=request.tool_name,
            decision=decision,
            reason=reason,
            metadata=safe_metadata,
        )

        self._audit.record(event)
        return event.event_id

    def execute(self, request: ToolRequest) -> ToolResponse:
        """Inspect, authenticate, authorize, assess, confirm, then execute."""
        untrusted_content = request.arguments.get("content")

        if isinstance(untrusted_content, str):
            injection = self._injection_detector.assess(untrusted_content)

            if injection.blocked:
                audit_event_id = self._record(
                    event_type=AuditEventType.INJECTION,
                    request=request,
                    decision="deny",
                    reason=injection.reason,
                    metadata={
                        "matched_patterns": injection.matched_patterns,
                    },
                )

                return ToolResponse(
                    success=False,
                    tool_name=request.tool_name,
                    decision="deny",
                    reason=injection.reason,
                    risk_level=RiskLevel.HIGH,
                    confirmation_required=False,
                    audit_event_id=audit_event_id,
                )

        authentication = self._authentication.authenticate(
            AuthenticationRequest(
                agent_id=request.agent_id,
                credential=request.credential,
                session_id=request.session_id,
            )
        )

        if authentication.principal is None:
            audit_event_id = self._record(
                event_type=AuditEventType.AUTHENTICATION,
                request=request,
                decision="unauthenticated",
                reason=authentication.reason,
            )

            return ToolResponse(
                success=False,
                tool_name=request.tool_name,
                decision="unauthenticated",
                reason=authentication.reason,
                audit_event_id=audit_event_id,
            )

        if not self._registry.contains(request.tool_name):
            audit_event_id = self._record(
                event_type=AuditEventType.AUTHORIZATION,
                request=request,
                decision="deny",
                reason="Unknown tool.",
            )

            return ToolResponse(
                success=False,
                tool_name=request.tool_name,
                decision="deny",
                reason="Unknown tool.",
                audit_event_id=audit_event_id,
            )

        permission = TOOL_PERMISSIONS.get(request.tool_name)

        if permission is None:
            audit_event_id = self._record(
                event_type=AuditEventType.AUTHORIZATION,
                request=request,
                decision="deny",
                reason="Tool permission is not registered.",
            )

            return ToolResponse(
                success=False,
                tool_name=request.tool_name,
                decision="deny",
                reason="Tool permission is not registered.",
                audit_event_id=audit_event_id,
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
            audit_event_id = self._record(
                event_type=AuditEventType.AUTHORIZATION,
                request=request,
                decision=authorization.decision.value,
                reason=authorization.reason,
            )

            return ToolResponse(
                success=False,
                tool_name=request.tool_name,
                decision=authorization.decision.value,
                reason=authorization.reason,
                risk_level=risk.risk_level,
                confirmation_required=risk.requires_confirmation,
                audit_event_id=audit_event_id,
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

            audit_event_id = self._record(
                event_type=AuditEventType.CONFIRMATION,
                request=request,
                decision=confirmation.decision.value,
                reason=confirmation.reason,
                metadata={
                    "risk_level": risk.risk_level.value,
                    "confirmation_required": True,
                },
            )

            if confirmation.decision != ConfirmationDecision.APPROVED:
                return ToolResponse(
                    success=False,
                    tool_name=request.tool_name,
                    decision="deny",
                    reason=confirmation.reason,
                    risk_level=risk.risk_level,
                    confirmation_required=True,
                    audit_event_id=audit_event_id,
                )

            reauthorization = self._policy.evaluate(
                AuthorizationRequest(
                    principal=authentication.principal,
                    tool_name=request.tool_name,
                    permission=permission,
                ),
                confirmation_granted=True,
            )

            if reauthorization.decision != PolicyDecision.ALLOW:
                return ToolResponse(
                    success=False,
                    tool_name=request.tool_name,
                    decision=reauthorization.decision.value,
                    reason=(
                        "Authorization re-evaluation failed after "
                        "human confirmation: "
                        f"{reauthorization.reason}"
                    ),
                    risk_level=risk.risk_level,
                    confirmation_required=True,
                    audit_event_id=audit_event_id,
                )

        registered = self._registry.get(request.tool_name)

        if registered is None:
            audit_event_id = self._record(
                event_type=AuditEventType.AUTHORIZATION,
                request=request,
                decision="deny",
                reason="Tool disappeared from registry.",
            )

            return ToolResponse(
                success=False,
                tool_name=request.tool_name,
                decision="deny",
                reason="Tool disappeared from registry.",
                risk_level=risk.risk_level,
                confirmation_required=risk.requires_confirmation,
                audit_event_id=audit_event_id,
            )

        _definition, handler = registered

        try:
            result = handler(request.arguments)
        except (ValueError, TypeError) as exc:
            reason = str(exc)

            audit_event_id = self._record(
                event_type=AuditEventType.TOOL_FAILURE,
                request=request,
                decision="validation_error",
                reason=reason,
            )

            return ToolResponse(
                success=False,
                tool_name=request.tool_name,
                decision="validation_error",
                reason=reason,
                risk_level=risk.risk_level,
                confirmation_required=risk.requires_confirmation,
                audit_event_id=audit_event_id,
            )
        except RuntimeError as exc:
            reason = str(exc)

            audit_event_id = self._record(
                event_type=AuditEventType.TOOL_FAILURE,
                request=request,
                decision="execution_error",
                reason=reason,
            )

            return ToolResponse(
                success=False,
                tool_name=request.tool_name,
                decision="execution_error",
                reason=reason,
                risk_level=risk.risk_level,
                confirmation_required=risk.requires_confirmation,
                audit_event_id=audit_event_id,
            )

        audit_event_id = self._record(
            event_type=AuditEventType.TOOL_EXECUTION,
            request=request,
            decision=PolicyDecision.ALLOW.value,
            reason="Security checks passed and tool executed.",
            metadata={
                "risk_level": risk.risk_level.value,
                "confirmation_required": risk.requires_confirmation,
            },
        )

        return ToolResponse(
            success=True,
            tool_name=request.tool_name,
            result=result,
            decision=PolicyDecision.ALLOW.value,
            reason="Security checks passed and tool executed.",
            risk_level=risk.risk_level,
            confirmation_required=risk.requires_confirmation,
            audit_event_id=audit_event_id,
        )
