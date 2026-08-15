"""Stable, user-safe errors for the MediCare AI foundation."""


class AIFoundationError(Exception):
    """Base class for expected, non-sensitive AI foundation failures."""

    code = "ai_foundation_error"


class InvalidAIInputError(AIFoundationError):
    code = "invalid_input"


class MissingClinicalInformationError(AIFoundationError):
    code = "missing_clinical_information"


class UnauthorizedAIRequestError(AIFoundationError):
    code = "unauthorized_request"


class UnsupportedAIRequestError(AIFoundationError):
    code = "unsupported_request"


class ModelUnavailableError(AIFoundationError):
    code = "model_unavailable"


class UnsafeAIOutputError(AIFoundationError):
    code = "unsafe_output"


class AIServiceUnavailableError(AIFoundationError):
    code = "service_unavailable"
