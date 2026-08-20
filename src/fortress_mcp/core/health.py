"""Basic application health check."""

from typing import Final

SERVICE_NAME: Final[str] = "fortress-mcp"


def health_check() -> dict[str, str]:
    """Return basic service health information."""
    return {
        "service": SERVICE_NAME,
        "status": "ok",
    }
