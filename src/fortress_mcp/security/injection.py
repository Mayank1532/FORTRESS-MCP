"""Deterministic prompt-injection detection boundary."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class InjectionVerdict(StrEnum):
    """Security classification for untrusted input."""

    SAFE = "safe"
    SUSPICIOUS = "suspicious"


class InjectionAssessment(BaseModel):
    """Result of deterministic prompt-injection inspection."""

    model_config = ConfigDict(frozen=True)

    verdict: InjectionVerdict
    reason: str
    matched_patterns: tuple[str, ...] = Field(default_factory=tuple)

    @property
    def blocked(self) -> bool:
        """Return whether the input must be contained."""
        return self.verdict == InjectionVerdict.SUSPICIOUS


class PromptInjectionDetector:
    """Detect common instruction-override patterns without granting authority."""

    _PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
        (
            "ignore_previous_instructions",
            (
                "ignore previous instructions",
                "ignore all previous instructions",
                "disregard previous instructions",
                "disregard all previous instructions",
            ),
        ),
        (
            "override_security",
            (
                "bypass security",
                "bypass authorization",
                "bypass authentication",
                "disable security",
                "disable authorization",
            ),
        ),
        (
            "privilege_escalation",
            (
                "grant me admin",
                "make me admin",
                "elevate my privileges",
                "elevate privileges",
                "give me administrator access",
            ),
        ),
        (
            "instruction_hijacking",
            (
                "system message:",
                "developer message:",
                "new system instruction:",
                "new developer instruction:",
            ),
        ),
    )

    def assess(self, content: str) -> InjectionAssessment:
        """Classify untrusted content deterministically."""
        normalized = " ".join(content.lower().split())

        matches: list[str] = []

        for pattern_name, phrases in self._PATTERNS:
            if any(phrase in normalized for phrase in phrases):
                matches.append(pattern_name)

        if matches:
            return InjectionAssessment(
                verdict=InjectionVerdict.SUSPICIOUS,
                reason="Potential prompt injection detected.",
                matched_patterns=tuple(matches),
            )

        return InjectionAssessment(
            verdict=InjectionVerdict.SAFE,
            reason="No configured prompt-injection pattern detected.",
        )
