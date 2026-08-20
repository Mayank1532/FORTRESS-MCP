"""Explicit FORTRESS tool registry."""

from collections.abc import Mapping

from fortress_mcp.mcp.contracts import ToolDefinition, ToolHandler


class ToolRegistry:
    """Explicit registry preventing unknown-tool execution."""

    def __init__(
        self,
        tools: Mapping[str, tuple[ToolDefinition, ToolHandler]],
    ) -> None:
        self._tools = dict(tools)

    def get(self, tool_name: str) -> tuple[ToolDefinition, ToolHandler] | None:
        """Return a registered tool or None."""
        return self._tools.get(tool_name)

    def list_tools(self) -> list[ToolDefinition]:
        """Return registered tool definitions."""
        return [
            definition
            for definition, _handler in self._tools.values()
        ]

    def contains(self, tool_name: str) -> bool:
        """Return whether a tool is explicitly registered."""
        return tool_name in self._tools
