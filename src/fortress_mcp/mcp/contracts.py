"""FORTRESS tool contracts and execution boundary."""

from collections.abc import Callable, Mapping
from typing import Protocol

from pydantic import BaseModel


class Tool(Protocol):
    """Protocol implemented by every registered FORTRESS tool."""

    name: str
    permission: object

    def execute(self, arguments: Mapping[str, object]) -> object:
        """Execute validated tool arguments."""
        ...


ToolHandler = Callable[[Mapping[str, object]], object]


class ToolDefinition(BaseModel):
    """Metadata describing a registered tool."""

    name: str
    description: str
    input_schema: dict[str, object]
