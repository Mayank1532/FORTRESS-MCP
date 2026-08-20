"""FORTRESS-MCP HTTP API."""

from fastapi import FastAPI

from fortress_mcp.core.health import health_check

app = FastAPI(
    title="FORTRESS-MCP",
    description="Zero-trust security gateway for AI-agent tool execution.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Return service health."""
    return health_check()
