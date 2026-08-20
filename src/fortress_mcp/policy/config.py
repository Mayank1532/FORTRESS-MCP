"""Policy configuration for FORTRESS authorization."""

from dataclasses import dataclass

from fortress_mcp.policy.models import Permission


@dataclass(frozen=True)
class ToolPolicy:
    """Security policy assigned to one tool."""

    permission: Permission
    requires_confirmation: bool = False


DEFAULT_TOOL_POLICIES: dict[str, ToolPolicy] = {
    "calculator_read": ToolPolicy(
        permission=Permission.READ,
    ),
    "weather_lookup": ToolPolicy(
        permission=Permission.READ,
    ),
    "update_record": ToolPolicy(
        permission=Permission.WRITE,
        requires_confirmation=True,
    ),
    "sensitive_action": ToolPolicy(
        permission=Permission.SENSITIVE,
        requires_confirmation=True,
    ),
}
