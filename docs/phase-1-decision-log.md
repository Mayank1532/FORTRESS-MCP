# FORTRESS-MCP — Phase 1 Decision Log

## Status

**Phase:** 1 — Threat Model + Security Architecture

**Status:** Architecture locked pending validation and Git checkpoint.

**Project Timebox:** 6 focused hours.

## Decision 1 — Product Positioning

FORTRESS-MCP is a:

> Provider-neutral zero-trust security gateway for AI-agent tool execution.

The project is intentionally industry-style, security-focused, portfolio-impactful, interview-friendly, and simple enough to understand and complete without unnecessary complexity.

## Decision 2 — Zero-Trust Boundary

```text
Agent
  ↓
FORTRESS
  ↓
MCP
  ↓
Tool
```

The AI agent does not directly control tool execution.

## Decision 3 — Deterministic Security

Authentication, authorization, policy, risk, validation, confirmation, and audit remain deterministic application logic.

The LLM is not the security authority.

## Decision 4 — Default Deny

```text
Explicitly allowed → ALLOW
Explicitly denied  → DENY
Unknown/insufficient permission → DENY
```

## Decision 5 — Permissions

```text
READ
WRITE
SENSITIVE
```

This demonstrates least privilege without unnecessary RBAC complexity.

## Decision 6 — Policy Decisions

```text
ALLOW
DENY
REQUIRE_CONFIRMATION
```

## Decision 7 — Risk

```text
LOW
MEDIUM
HIGH
```

Risk classification remains deterministic.

## Decision 8 — Human Confirmation

HIGH-risk sensitive operations require explicit user confirmation.

The model cannot generate or simulate that confirmation.

Authorization is re-evaluated after confirmation.

## Decision 9 — MCP

MCP is the standardized tool interaction layer.

FORTRESS is the security boundary around MCP execution.

The project will reuse MCP foundations where appropriate rather than rebuilding MCP.

## Decision 10 — Tool Count

Maximum four core tools:

1. `calculator_read`
2. `weather_lookup`
3. `update_record`
4. `sensitive_action`

## Decision 11 — Live Data API

Open-Meteo is the selected free live-data API for weather lookup.

Reasons:

- live external data;
- simple HTTP/JSON interface;
- no API-key dependency for the selected free usage model;
- useful for demonstrating external-tool security;
- suitable for the six-hour timebox.

The external provider remains replaceable.

## Decision 12 — Streamlit

Streamlit is required as the FORTRESS Security Control Center.

It displays security decisions and results but does not implement authorization.

## Decision 13 — HTTP API

A small HTTP API boundary supports:

- Streamlit;
- Bruno;
- future clients.

## Decision 14 — Bruno

Bruno is required for independent HTTP/API security testing.

The collection will cover:

- authentication;
- authorized requests;
- unauthorized requests;
- invalid arguments;
- confirmation-required requests;
- security failure cases.

## Decision 15 — DeepEval

DeepEval is required for security-relevant agent behavior evaluation.

DeepEval evaluates behavior; it does not make authorization decisions.

## Decision 16 — SonarQube

SonarQube Free/Community is required for static analysis and security-quality review.

Focus on meaningful findings rather than extensive configuration.

## Decision 17 — Testing

Pytest is the deterministic security-test framework.

Expensive model/external integration behavior is isolated from fast deterministic tests.

## Decision 18 — Engineering Quality

The project uses:

- UV;
- Python 3.12;
- Ruff;
- Mypy;
- Docker;
- GitHub Actions.

Clean Git history and milestone checkpoints are required.

## Decision 19 — Provider Neutrality

No mandatory commercial LLM provider is required.

The agent/model boundary remains provider-neutral.

## Decision 20 — Secrets

No API keys or credentials will be committed.

Any future credential-based integration must use secure environment/configuration mechanisms.

## Decision 21 — Audit

Every security decision produces a safe audit event.

Audit records must not expose secrets.

## Decision 22 — Prompt Injection

The project demonstrates that prompt injection cannot independently grant tool permission.

It does not claim perfect prompt-injection prevention.

## Decision 23 — Scope Protection

Out of scope:

- enterprise OAuth/OIDC;
- enterprise IAM;
- Kubernetes;
- multi-cloud;
- cloud deployment;
- advanced RAG;
- multi-agent orchestration;
- complex database;
- complex frontend;
- excessive tool count;
- advanced risk mathematics.

Optional improvements are documented rather than implemented if they threaten the timebox.

## Decision 24 — Developer Experience

The project must remain interesting, understandable, and fun to build.

Each phase should produce visible progress.

Priority:

```text
High learning value
+
High interview value
+
High portfolio value
+
Low unnecessary complexity
```

## Phase 1 Completion Criteria

Phase 1 is complete when:

- threat model exists;
- architecture exists;
- decisions are documented;
- tool set is locked;
- authentication boundary is defined;
- authorization boundary is defined;
- policy contract is defined;
- risk model is defined;
- confirmation boundary is defined;
- audit model is defined;
- Streamlit role is defined;
- Bruno role is defined;
- DeepEval role is defined;
- SonarQube role is defined;
- live-data provider is defined;
- scope exclusions are explicit.

After validation, Phase 1 receives a Git checkpoint before implementation begins.
