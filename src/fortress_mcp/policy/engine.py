"""Deterministic authorization policy engine."""

from collections.abc import Mapping

from fortress_mcp.policy.config import DEFAULT_TOOL_POLICIES, ToolPolicy
from fortress_mcp.policy.models import (
    AuthorizationRequest,
    AuthorizationResult,
    Permission,
    PolicyDecision,
)


class PolicyEngine:
    """Evaluates authorization requests using deterministic policies."""

    def __init__(
        self,
        tool_policies: Mapping[str, ToolPolicy] | None = None,
    ) -> None:
        self._tool_policies = dict(
            DEFAULT_TOOL_POLICIES
            if tool_policies is None
            else tool_policies
        )

    def evaluate(
        self,
        request: AuthorizationRequest,
    ) -> AuthorizationResult:
        """Evaluate an authorization request using default-deny semantics."""
        policy = self._tool_policies.get(request.tool_name)

        if policy is None:
            return AuthorizationResult(
                decision=PolicyDecision.DENY,
                reason="Unknown tool.",
                required_permission=request.permission,
            )

        if policy.permission != request.permission:
            return AuthorizationResult(
                decision=PolicyDecision.DENY,
                reason="Requested permission does not match tool policy.",
                required_permission=policy.permission,
            )

        if not self._principal_has_permission(
            request.principal,
            policy.permission,
        ):
            return AuthorizationResult(
                decision=PolicyDecision.DENY,
                reason="Principal does not have the required permission.",
                required_permission=policy.permission,
            )

        if policy.requires_confirmation:
            return AuthorizationResult(
                decision=PolicyDecision.REQUIRE_CONFIRMATION,
                reason="Tool requires explicit human confirmation.",
                required_permission=policy.permission,
            )

        return AuthorizationResult(
            decision=PolicyDecision.ALLOW,
            reason="Authorization policy satisfied.",
            required_permission=policy.permission,
        )

    @staticmethod
    def _principal_has_permission(
        principal: object,
        required_permission: Permission,
    ) -> bool:
        """Determine whether a principal has a permission.

        The current Phase 4 identity model intentionally keeps role
        information simple. Role-to-permission mapping is centralized
        here so that it can be replaced without changing callers.
        """
        role = getattr(principal, "role", "")

        role_permissions: dict[str, frozenset[Permission]] = {
            "reader": frozenset({Permission.READ}),
            "writer": frozenset({Permission.READ, Permission.WRITE}),
            "admin": frozenset(
                {
                    Permission.READ,
                    Permission.WRITE,
                    Permission.SENSITIVE,
                }
            ),
        }

        permissions = role_permissions.get(role, frozenset())

        return required_permission in permissions
