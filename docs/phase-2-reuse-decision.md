# FORTRESS-MCP — Phase 2 Reuse Decision

## Audit Result

Phase 2 verified the local portfolio infrastructure available for reuse.

## Primary Source — TOOLFORGE

Reuse/adapt concepts from TOOLFORGE:

- MCP package structure.
- Tool contracts.
- MCP registry concepts.
- MCP client/server boundary.
- Tool execution boundary.
- Live API adapter pattern.
- Pydantic-based contracts.
- UV project layout.

Do not copy TOOLFORGE project-specific agent/provider logic.

## Secondary Source — NEXUS-SHIELD

Reuse/adapt:

- Python 3.12 constraint.
- UV project configuration.
- dependency groups.
- Ruff configuration.
- Mypy configuration.
- Pytest configuration.
- GitHub Actions quality workflow.
- Docker build pattern.
- SonarQube project configuration.

## Supporting Source — WEBPULSE

Use only as a reference for:

- HTTP/API patterns.
- Pydantic usage.
- testing patterns.

## Deliberately Not Reused

- project-specific business logic;
- project-specific agent behavior;
- provider-specific integrations;
- existing evaluation logic;
- existing README content;
- unnecessary infrastructure;
- unrelated application modules.

## FORTRESS-Specific Logic

The following will be implemented specifically for FORTRESS:

- identity;
- authentication;
- authorization;
- policy engine;
- risk classification;
- confirmation;
- security validation;
- prompt-injection boundary;
- audit events;
- security-focused evaluation.

## Phase 2 Decision

The foundation is **adapted rather than cloned**.

The project now has a clean UV/Python/MCP/API/Streamlit/quality foundation while preserving the security gateway as the original engineering contribution.
