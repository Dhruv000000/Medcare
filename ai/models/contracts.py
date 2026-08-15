"""Contracts shared by future MediCare AI model adapters and services."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol, Sequence
from uuid import UUID, uuid4

from ai.core_errors import ModelUnavailableError


@dataclass(frozen=True)
class AuthorizationContext:
    """Server-derived identity and clinical scope for a future AI request."""

    user_id: int
    role: str
    patient_id: int | None = None
    authorized_patient_ids: frozenset[int] = frozenset()
    request_id: UUID = field(default_factory=uuid4)

    def can_access_patient(self, patient_id: int) -> bool:
        if self.role == "patient":
            return self.patient_id == patient_id
        if self.role == "doctor":
            return patient_id in self.authorized_patient_ids
        return self.role == "administrator"

    def validate_patient_scope(self, patient_id: int) -> None:
        from ai.core_errors import UnauthorizedAIRequestError

        if not self.can_access_patient(patient_id):
            raise UnauthorizedAIRequestError("The requested patient is outside the authorized scope.")


@dataclass(frozen=True)
class AIRequest:
    """Validated task request passed from an authorized service boundary."""

    task: str
    patient_id: int
    inputs: Mapping[str, Any]
    authorization: AuthorizationContext


@dataclass(frozen=True)
class AIResponse:
    """Structured future response; no field implies a fabricated clinical result."""

    request_id: UUID
    task: str
    result: Any | None = None
    model_name: str | None = None
    model_version: str | None = None
    confidence: float | None = None
    explanation: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    disclaimer: str = "AI output is informational decision support and requires qualified clinical judgment."
    status: str = "unsupported"

    def as_dict(self) -> dict[str, Any]:
        return {
            "request_id": str(self.request_id),
            "task": self.task,
            "status": self.status,
            "result": self.result,
            "model": self.model_name,
            "model_version": self.model_version,
            "confidence": self.confidence,
            "explanation": list(self.explanation),
            "provenance": list(self.provenance),
            "warnings": list(self.warnings),
            "disclaimer": self.disclaimer,
        }


class ModelAdapter(Protocol):
    """Future model interface used by service orchestration."""

    name: str
    version: str

    def predict(self, features: Mapping[str, Any]) -> AIResponse:
        """Return a validated response or raise a safe foundation error."""
        ...


class DeferredModel:
    """Explicit no-model adapter; it never returns a fake prediction."""

    name = "unavailable"
    version = "not-configured"

    def predict(self, features: Mapping[str, Any]) -> AIResponse:
        del features
        raise ModelUnavailableError("No validated MediCare AI model is available in this phase.")
