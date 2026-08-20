"""In-memory security audit recorder."""

from collections.abc import Sequence

from fortress_mcp.audit.models import AuditEvent


class AuditRecorder:
    """Store structured security events for the current process."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def record(self, event: AuditEvent) -> None:
        """Record one security event."""
        self._events.append(event)

    def events(self) -> tuple[AuditEvent, ...]:
        """Return an immutable snapshot of recorded events."""
        return tuple(self._events)

    def recent(self, limit: int = 50) -> Sequence[AuditEvent]:
        """Return the most recent events."""
        if limit < 1:
            return ()

        return tuple(self._events[-limit:])

    def clear(self) -> None:
        """Clear recorded events."""
        self._events.clear()
