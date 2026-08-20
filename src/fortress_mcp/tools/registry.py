"""Registered FORTRESS tool set."""

from fortress_mcp.mcp.contracts import ToolDefinition
from fortress_mcp.mcp.registry import ToolRegistry
from fortress_mcp.policy.models import Permission
from fortress_mcp.tools.calculator import CalculatorTool
from fortress_mcp.tools.sensitive_action import SensitiveActionTool
from fortress_mcp.tools.update_record import UpdateRecordTool
from fortress_mcp.tools.weather import WeatherTool


def build_tool_registry() -> ToolRegistry:
    """Build the explicit FORTRESS tool registry."""
    calculator = CalculatorTool()
    weather = WeatherTool()
    update_record = UpdateRecordTool()
    sensitive_action = SensitiveActionTool()

    return ToolRegistry(
        {
            "calculator_read": (
                ToolDefinition(
                    name="calculator_read",
                    description="Evaluate a safe arithmetic expression.",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string"},
                        },
                        "required": ["expression"],
                    },
                ),
                calculator.execute,
            ),
            "weather_lookup": (
                ToolDefinition(
                    name="weather_lookup",
                    description="Get current weather from Open-Meteo.",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"},
                        },
                        "required": ["latitude", "longitude"],
                    },
                ),
                weather.execute,
            ),
            "update_record": (
                ToolDefinition(
                    name="update_record",
                    description="Perform a controlled record update.",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "record_id": {"type": "string"},
                            "value": {"type": "string"},
                        },
                        "required": ["record_id", "value"],
                    },
                ),
                update_record.execute,
            ),
            "sensitive_action": (
                ToolDefinition(
                    name="sensitive_action",
                    description="Perform a simulated sensitive action.",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "action": {"type": "string"},
                        },
                        "required": ["action"],
                    },
                ),
                sensitive_action.execute,
            ),
        }
    )


TOOL_PERMISSIONS = {
    "calculator_read": Permission.READ,
    "weather_lookup": Permission.READ,
    "update_record": Permission.WRITE,
    "sensitive_action": Permission.SENSITIVE,
}
