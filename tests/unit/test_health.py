"""Foundation health tests."""

from fortress_mcp.core.health import health_check


def test_health_check() -> None:
    """Health check returns an operational service state."""
    result = health_check()

    assert result["service"] == "fortress-mcp"
    assert result["status"] == "ok"
