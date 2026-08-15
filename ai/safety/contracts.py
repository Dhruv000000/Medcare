"""Fail-closed safety checks for future MediCare AI service calls."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ai.core_errors import InvalidAIInputError, UnauthorizedAIRequestError, UnsafeAIOutputError
from ai.models.contracts import AIRequest, AIResponse, AuthorizationContext


SAFE_DISCLAIMER = "AI output is informational decision support and requires qualified clinical judgment."
PROHIBITED_CLAIM_TERMS = (
    "you have",
    "diagnosis:",
    "prescribe",
    "take this medication",
    "certain",
    "guaranteed",
)


def validate_authorization(context: AuthorizationContext, patient_id: int) -> None:
    if context.role not in {"patient", "doctor", "administrator"}:
        raise UnauthorizedAIRequestError("The user role is not authorized for AI support.")
    context.validate_patient_scope(patient_id)


def validate_request(request: AIRequest) -> AIRequest:
    if not request.task.strip():
        raise InvalidAIInputError("An AI task is required.")
    if request.patient_id <= 0:
        raise InvalidAIInputError("The patient identifier is invalid.")
    if not isinstance(request.inputs, Mapping):
        raise InvalidAIInputError("AI input must be an object.")
    validate_authorization(request.authorization, request.patient_id)
    return request


def validate_output(response: AIResponse) -> AIResponse:
    if response.disclaimer != SAFE_DISCLAIMER:
        raise UnsafeAIOutputError("The AI response must contain the approved safety disclaimer.")
    result_text = str(response.result or "").lower()
    if any(term in result_text for term in PROHIBITED_CLAIM_TERMS):
        raise UnsafeAIOutputError("The AI response contains a prohibited clinical claim.")
    if response.status == "supported" and response.confidence is None:
        # Supported confidence is optional for the foundation, but a future task must
        # explicitly document calibration before exposing it. No claim is invented here.
        return response
    return response
