"""Reproducible, task-neutral preprocessing contracts for future AI work."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ai.core_errors import InvalidAIInputError, MissingClinicalInformationError


@dataclass(frozen=True)
class PreprocessedInput:
    """Validated feature payload with an explicit preprocessing version."""

    task: str
    version: str
    features: Mapping[str, Any]


class InputSchema:
    """Small allow-list schema used before task-specific preprocessing exists."""

    def __init__(self, *, required_fields: set[str] | frozenset[str], allowed_fields: set[str] | frozenset[str] | None = None):
        self.required_fields = frozenset(required_fields)
        self.allowed_fields = frozenset(allowed_fields or required_fields)

    def validate(self, inputs: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(inputs, Mapping):
            raise InvalidAIInputError("AI input must be an object.")
        unknown = set(inputs) - self.allowed_fields
        if unknown:
            raise InvalidAIInputError("The AI request contains unsupported input fields.")
        missing = self.required_fields - set(inputs)
        if missing:
            raise MissingClinicalInformationError("Required clinical information is missing.")
        return dict(inputs)


class Preprocessor:
    """Future task-specific preprocessing interface."""

    version = "not-configured"

    def __init__(self, schema: InputSchema):
        self.schema = schema

    def transform(self, inputs: Mapping[str, Any], *, task: str) -> PreprocessedInput:
        validated = self.schema.validate(inputs)
        # Phase 11 intentionally performs no arbitrary normalization or imputation.
        return PreprocessedInput(task=task, version=self.version, features=validated)
