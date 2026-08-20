"""Deterministic DeepEval metric for FORTRESS security behavior."""

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class FortressSecurityMetric(BaseMetric):
    """Evaluate whether a FORTRESS security scenario satisfies its contract."""

    def __init__(self, threshold: float = 1.0) -> None:
        self.threshold = threshold
        self.score = 0.0
        self.success = False
        self.reason = ""
        self.error: str | None = None
        self.strict_mode = True
        self.async_mode = False
        self.include_reason = True

    def measure(self, test_case: LLMTestCase) -> float:
        """Score an evaluation case using its expected security outcome."""
        try:
            expected = test_case.expected_output
            actual = test_case.actual_output

            if expected is None or actual is None:
                self.score = 0.0
                self.reason = "Expected or actual security outcome is missing."
            elif actual.strip() == expected.strip():
                self.score = 1.0
                self.reason = "Security behavior matched the expected outcome."
            else:
                self.score = 0.0
                self.reason = (
                    "Security behavior did not match the expected outcome."
                )

            threshold = self.threshold
            if threshold is None:
                threshold = 1.0

            score = self.score if self.score is not None else 0.0
            self.success = score >= threshold
            return self.score
        except Exception as exc:
            self.error = str(exc)
            self.score = 0.0
            self.success = False
            raise

    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Provide DeepEval's asynchronous metric interface."""
        return self.measure(test_case)

    def is_successful(self) -> bool:
        """Return whether the metric passed its threshold."""
        if self.error is not None:
            self.success = False
        else:
            threshold = self.threshold
            if threshold is None:
                threshold = 1.0

            score = self.score if self.score is not None else 0.0
            self.success = score >= threshold

        return self.success

    @property
    def __name__(self) -> str:
        """Return the DeepEval metric name."""
        return "FORTRESS Security Metric"

