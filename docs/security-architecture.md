# FORTRESS-MCP — Security Architecture

## 1. Architecture Goal

FORTRESS-MCP is a provider-neutral zero-trust security gateway between AI-agent intent and MCP tool execution.

```text
Agent Intent
      ↓
Security Decision
      ↓
Tool Execution
```

The agent can request a tool, but cannot independently authorize it.

## 2. High-Level Architecture

```text
                         ┌─────────────────────┐
                         │     STREAMLIT UI     │
                         │  FORTRESS CONTROL    │
                         │       CENTER         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    FORTRESS API     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                 ┌────────────────────────────────┐
                 │       SECURITY GATEWAY          │
                 │                                │
                 │ Identity                       │
                 │ Authentication                 │
                 │ Authorization                  │
                 │ Policy                         │
                 │ Risk Classification            │
                 │ Argument Validation             │
                 │ Confirmation                    │
                 │ Audit                           │
                 └───────────────┬────────────────┘
                                 │
                                 ▼
                          ┌────────────┐
                          │ MCP GATEWAY│
                          └─────┬──────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
      calculator_read    weather_lookup    update_record
                                │
                                ▼
                         ┌─────────────┐
                         │ Open-Meteo  │
                         │  LIVE API   │
                         └─────────────┘
                                │
                                ▼
                              RESULT
                                │
                                ▼
                              AUDIT
```

## 3. Security Decision Pipeline

```text
1. Receive request
2. Authenticate identity
3. Resolve identity and permissions
4. Identify requested tool/action
5. Validate tool existence
6. Validate arguments
7. Evaluate policy
8. Determine risk
9. Determine confirmation requirement
10. Require external human confirmation when necessary
11. Re-evaluate authorization after confirmation
12. Execute through MCP
13. Record audit event
14. Return result
```

## 4. Identity

```text
AgentIdentity
├── agent_id
├── role
├── permissions
├── trust_level
└── session_id
```

Authentication answers: **Who are you?**

Authorization answers: **Are you allowed to perform this action?**

## 5. Permissions and Policy

Permissions:

```text
READ
WRITE
SENSITIVE
```

Policy decisions:

```text
ALLOW
DENY
REQUIRE_CONFIRMATION
```

Default behavior is deny.

The policy engine is deterministic and is never delegated to the LLM.

## 6. Risk

```text
LOW
MEDIUM
HIGH
```

Initial mapping:

```text
calculator_read → LOW
weather_lookup  → MEDIUM
update_record   → HIGH
sensitive_action → HIGH
```

## 7. Confirmation

```text
Agent Request
      ↓
FORTRESS
      ↓
HIGH RISK
      ↓
REQUIRE_CONFIRMATION
      ↓
Actual User Confirmation
      ↓
Policy Re-evaluation
      ↓
ALLOW / DENY
      ↓
MCP Execution
```

The LLM cannot claim that the user confirmed the operation.

## 8. MCP and Tool Registry

Initial tool set:

| Tool | Permission | Risk | Purpose |
|---|---|---|---|
| `calculator_read` | READ | LOW | Deterministic local calculation |
| `weather_lookup` | READ | MEDIUM | Live Open-Meteo weather |
| `update_record` | WRITE | HIGH | Local deterministic write demonstration |
| `sensitive_action` | SENSITIVE | HIGH | Sensitive action requiring confirmation |

The tool count is intentionally capped at four.

## 9. Live Data Boundary

Open-Meteo is the selected free live-data API.

```text
Agent
  ↓
FORTRESS
  ↓
Policy
  ↓
Validation
  ↓
MCP Tool
  ↓
Open-Meteo
```

External data is untrusted data and cannot modify authorization.

The provider remains replaceable.

## 10. Argument Validation

Arguments are validated before execution.

Weather lookup:

```text
latitude:  -90 to +90
longitude: -180 to +180
```

Invalid arguments are rejected before an external request is made.

## 11. Prompt-Injection Boundary

```text
Prompt Injection
      ↓
Agent Request
      ↓
FORTRESS Policy
      ↓
DENY / REQUIRE_CONFIRMATION
```

Prompt injection cannot independently create authorization.

## 12. Audit

Every security decision produces an audit event containing, as applicable:

```text
timestamp
session_id
agent_id
tool
action
risk_level
policy_decision
reason
confirmation_required
execution_status
safe argument summary
```

Audit records must not expose secrets.

The audit trail answers:

```text
WHO
WHAT
WHEN
WHY
RISK
DECISION
EXECUTION
```

## 13. Streamlit

Streamlit is the interactive FORTRESS Security Control Center.

It displays:

- agent identity;
- requested tool/action;
- permissions;
- risk;
- policy decision;
- confirmation controls;
- execution result;
- audit events;
- prompt-injection demonstration.

Streamlit does not own authorization logic.

## 14. HTTP API

A small HTTP API is the shared boundary for clients:

```text
Streamlit ──┐
            ├──→ FORTRESS API → Security Gateway → MCP
Bruno ──────┘
```

Bruno therefore tests the API independently of the UI.

## 15. Evaluation and Quality

- **Pytest:** deterministic security tests.
- **DeepEval:** security-relevant agent behavior evaluation.
- **Bruno:** HTTP/API security testing.
- **SonarQube Free/Community:** static analysis, vulnerabilities, security hotspots, bugs, and code quality.
- **Ruff:** linting.
- **Mypy:** type checking.
- **GitHub Actions:** CI.
- **Docker:** reproducible runtime.

These tools do not replace deterministic authorization.

## 16. Design Principles

- Zero trust.
- Least privilege.
- Default deny.
- Deterministic security decisions.
- Provider neutrality.
- Explicit human boundary.
- Auditability.
- Minimal complexity with high security and interview value.

## 17. Explicitly Out of Scope

- Enterprise OAuth/OIDC server.
- Enterprise IAM platform.
- Kubernetes.
- Multi-cloud deployment.
- Cloud-specific IAM.
- Advanced RAG.
- Multi-agent orchestration.
- Complex persistent database.
- Complex frontend framework.
- Dozens of MCP tools.
- Advanced mathematical risk engine.
- Unnecessary distributed infrastructure.
