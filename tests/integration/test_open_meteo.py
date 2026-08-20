"""Optional live Open-Meteo integration test."""

import os

import pytest

from fortress_mcp.tools.weather import WeatherTool


@pytest.mark.skipif(
    os.getenv("FORTRESS_LIVE_API_TESTS") != "1",
    reason="Live API tests require FORTRESS_LIVE_API_TESTS=1.",
)
def test_open_meteo_live_weather() -> None:
    """Verify the selected live weather API."""
    result = WeatherTool().execute(
        {
            "latitude": 28.6139,
            "longitude": 77.2090,
        }
    )

    assert isinstance(result, dict)
    assert "current" in result
