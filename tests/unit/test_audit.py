from fortress_mcp.audit import AuditEvent, AuditEventType, AuditRecorder
from fortress_mcp.audit.redaction import redact_mapping


def test_audit_recorder_stores_events() -> None:
    recorder = AuditRecorder()

    recorder.record(
        AuditEvent(
            event_type=AuditEventType.AUTHORIZATION,
            agent_id="agent-1",
            tool_name="calculator",
            decision="allow",
            reason="Policy allowed the operation.",
        )
    )

    events = recorder.events()

    assert len(events) == 1
    assert events[0].event_type == AuditEventType.AUTHORIZATION
    assert events[0].tool_name == "calculator"


def test_audit_recorder_recent_limits_results() -> None:
    recorder = AuditRecorder()

    for index in range(3):
        recorder.record(
            AuditEvent(
                event_type=AuditEventType.TOOL_EXECUTION,
                agent_id="agent-1",
                tool_name=f"tool-{index}",
                decision="allow",
                reason="Executed.",
            )
        )

    recent = recorder.recent(2)

    assert len(recent) == 2
    assert recent[0].tool_name == "tool-1"
    assert recent[1].tool_name == "tool-2"


def test_sensitive_values_are_redacted() -> None:
    result = redact_mapping(
        {
            "credential": "super-secret",
            "api_key": "api-secret",
            "nested": {
                "password": "hidden-password",
                "safe_value": "visible",
            },
        }
    )

    assert result["credential"] == "[REDACTED]"
    assert result["api_key"] == "[REDACTED]"
    assert result["nested"]["password"] == "[REDACTED]"
    assert result["nested"]["safe_value"] == "visible"


def test_non_sensitive_values_are_preserved() -> None:
    result = redact_mapping(
        {
            "tool_name": "calculator",
            "operation": "2 + 2",
        }
    )

    assert result == {
        "tool_name": "calculator",
        "operation": "2 + 2",
    }
