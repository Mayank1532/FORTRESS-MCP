"""Sensitive-value redaction for security audit records."""

from collections.abc import Mapping

_SENSITIVE_KEYS = frozenset(
    {
        "credential",
        "password",
        "passwd",
        "secret",
        "token",
        "api_key",
        "apikey",
        "authorization",
        "access_token",
        "refresh_token",
    }
)


def redact_value(value: object, *, key: str | None = None) -> object:
    """Return a recursively redacted representation of a value."""
    if key is not None and key.lower() in _SENSITIVE_KEYS:
        return "[REDACTED]"

    if isinstance(value, Mapping):
        return {
            str(item_key): redact_value(item_value, key=str(item_key))
            for item_key, item_value in value.items()
        }

    if isinstance(value, list):
        return [redact_value(item) for item in value]

    if isinstance(value, tuple):
        return tuple(redact_value(item) for item in value)

    return value


def redact_mapping(values: Mapping[str, object]) -> dict[str, object]:
    """Return a recursively redacted mapping."""
    return {
        str(key): redact_value(value, key=str(key))
        for key, value in values.items()
    }
