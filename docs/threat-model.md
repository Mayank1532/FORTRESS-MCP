# FORTRESS-MCP — Threat Model

## 1. Purpose

FORTRESS-MCP is a provider-neutral zero-trust security gateway for AI-agent tool execution.

Core principle:

> An AI agent may request an action, but the agent does not independently authorize or execute privileged actions.

FORTRESS separates:

```text
Agent Intent
    ≠
Security Decision
    ≠
Tool Execution
```

## 2. Security Objectives

FORTRESS-MCP must provide:

1. Zero-trust tool execution.
2. Least-privilege authorization.
3. Default-deny behavior.
4. Explicit policy decisions.
5. Risk classification.
6. Human confirmation for sensitive actions.
7. Argument validation before execution.
8. Prompt-injection containment.
9. Tool identity validation.
10. Safe audit logging.
11. Security-focused automated testing.
12. Reproducible and reviewable engineering controls.

## 3. Threats and Controls

### T1 — Prompt Injection
**Threat:** Untrusted content attempts to manipulate the agent into bypassing security rules.

**Control:** Untrusted content never grants permission. FORTRESS independently evaluates the requested action.

```text
Untrusted Content
       ↓
Agent Request
       ↓
FORTRESS Policy
       ↓
ALLOW / DENY / REQUIRE_CONFIRMATION
```

### T2 — Unauthorized Tool Access
**Threat:** An agent requests a tool outside its assigned permissions.

**Control:** Explicit permission checks with default deny.

Permissions:
```text
READ
WRITE
SENSITIVE
```

### T3 — Privilege Escalation
**Threat:** A low-privilege agent attempts a higher-privilege action.

**Control:** Effective permission comes from authenticated identity and policy, not the agent request.

### T4 — Malicious Tool Arguments
**Threat:** An authorized tool is invoked with invalid or dangerous arguments.

**Control:** Validate arguments before execution. For weather lookup, latitude and longitude remain within valid geographic ranges.

### T5 — Tool Impersonation
**Threat:** An agent requests an unknown or unregistered tool.

**Control:** Explicit tool registry. Unknown tools are rejected.

### T6 — Sensitive Action Without Confirmation
**Threat:** A high-risk action executes without explicit human authorization.

**Control:** Return `REQUIRE_CONFIRMATION`. Confirmation must originate outside the LLM. The model cannot confirm its own request.

### T7 — Credential Leakage
**Threat:** Credentials or secrets appear in requests, responses, or logs.

**Control:** Avoid unnecessary credentials for the selected free live-data API. Never write secrets to audit logs and redact sensitive values where required.

### T8 — Audit-Log Leakage
**Threat:** Sensitive information is unintentionally recorded in security logs.

**Control:** Store safe summaries and security metadata rather than raw secrets.

### T9 — Privileged-Agent Looping
**Threat:** An agent repeatedly attempts privileged operations after denial.

**Control:** Record denied privileged operations as security events so repeated behavior is observable and evaluable.

## 4. Trust Boundaries

1. **Agent → FORTRESS:** Agent requests are untrusted input.
2. **FORTRESS → MCP:** Only policy-approved and validated requests cross the execution boundary.
3. **MCP → External Tool:** External execution is controlled and auditable.
4. **External Data → Agent:** External/live data is untrusted data, never authorization.
5. **Human Confirmation:** Sensitive authorization comes from the actual user interface, not the model.

## 5. Security Invariants

```text
1. Default deny.
2. Agent intent never equals authorization.
3. Untrusted content never grants permission.
4. Unknown tools never execute.
5. Invalid arguments never reach execution.
6. Sensitive actions require explicit confirmation.
7. The LLM cannot self-confirm.
8. Every security decision is auditable.
9. Audit records must not expose secrets.
10. Tool execution occurs only after the security gate.
```

## 6. Known Limitations

FORTRESS does not claim to solve prompt injection perfectly. It demonstrates a security boundary in which prompt injection cannot independently grant authorization.

The project is a focused portfolio-grade security gateway rather than a complete enterprise IAM platform.

Enterprise OAuth/OIDC, Kubernetes, cloud IAM, multi-cloud deployment, and distributed identity infrastructure are outside scope.
