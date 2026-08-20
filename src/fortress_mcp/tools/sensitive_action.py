"""High-risk sensitive-action demonstration tool."""

from collections.abc import Mapping


class SensitiveActionTool:
    """Controlled high-risk action requiring FORTRESS confirmation."""

    name = "sensitive_action"

    def execute(self, arguments: Mapping[str, object]) -> object:
        """Validate and return a non-destructive simulated action."""
        action = arguments.get("action")

        if not isinstance(action, str) or not action.strip():
            raise ValueError("action must be a non-empty string")

        if len(action) > 256:
            raise ValueError("action is too long")

        return {
            "executed": True,
            "action": action,
            "simulated": True,
        }
