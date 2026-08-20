"""FORTRESS MCP request and response contracts."""

from pydantic import BaseModel, ConfigDict, Field


class ToolRequest(BaseModel):
    """Request entering the FORTRESS MCP gateway."""

    model_config = ConfigDict(frozen=True)

    agent_id: str = Field(min_length=1, max_length=128)
    credential: str = Field(min_length=1, max_length=256)
    tool_name: str = Field(min_length=1, max_length=128)
    arguments: dict[str, object] = Field(default_factory=dict)


class ToolResponse(BaseModel):
    """Safe response returned by the gateway."""

    success: bool
    tool_name: str
    result: object | None = None
    decision: str
    reason: str
