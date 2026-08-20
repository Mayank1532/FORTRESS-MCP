"""Controlled write-operation demonstration tool."""

from collections.abc import Mapping


class UpdateRecordTool:
    """Perform a small deterministic record update.

    This is intentionally local and non-persistent. Its purpose is to
    demonstrate FORTRESS authorization and confirmation before a write.
    """

    name = "update_record"

    def execute(self, arguments: Mapping[str, object]) -> object:
        """Validate and return a safe simulated update."""
        record_id = arguments.get("record_id")
        value = arguments.get("value")

        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError("record_id must be a non-empty string")

        if len(record_id) > 128:
            raise ValueError("record_id is too long")

        if not isinstance(value, str) or not value.strip():
            raise ValueError("value must be a non-empty string")

        if len(value) > 512:
            raise ValueError("value is too long")

        return {
            "updated": True,
            "record_id": record_id,
            "value": value,
        }
