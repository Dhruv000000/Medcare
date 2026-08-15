"""Explainability and structured-output contracts for future AI adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ai.core_errors import UnsafeAIOutputError
from ai.models.contracts import AIResponse


@dataclass(frozen=True)
class Explanation:
    """A future explanation item tied to a validated feature or evidence source."""

    text: str
    source: str | None = None
    feature: str | None = None


class ExplanationProvider:
    """Future provider boundary; Phase 11 has no selected explainability method."""

    name = "not-configured"

    def explain(self, response: AIResponse, features: Mapping[str, Any]) -> tuple[Explanation, ...]:
        del response, features
        return ()


def validate_response(response: AIResponse) -> AIResponse:
    """Reject structurally unsafe output before a future API serializer uses it."""

    if not response.task or response.status not in {"supported", "unsupported", "abstained"}:
        raise UnsafeAIOutputError("The AI response has an invalid status or task.")
    if not response.disclaimer.strip():
        raise UnsafeAIOutputError("The AI response is missing its safety disclaimer.")
    if response.confidence is not None and not 0 <= response.confidence <= 1:
        raise UnsafeAIOutputError("The AI confidence value is outside the allowed range.")
    if response.status == "supported" and response.result is None:
        raise UnsafeAIOutputError("A supported AI response must contain a validated result.")
    if response.status != "supported" and response.result is not None:
        raise UnsafeAIOutputError("Unsupported or abstained responses cannot contain a result.")
    return response
