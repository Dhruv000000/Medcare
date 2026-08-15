"""Django-independent AI service boundary for future MediCare capabilities."""

from __future__ import annotations

from typing import Any, Mapping

from ai.core_errors import UnsupportedAIRequestError
from ai.explainability.contracts import validate_response as validate_explainability_response
from ai.models.contracts import AIRequest, AIResponse, DeferredModel, ModelAdapter
from ai.preprocessing.contracts import InputSchema, Preprocessor
from ai.safety.contracts import validate_output, validate_request


class AIService:
    """Orchestrate a future task without bypassing authorization or safety."""

    def __init__(
        self,
        *,
        supported_tasks: set[str] | frozenset[str] = frozenset(),
        preprocessor: Preprocessor | None = None,
        model: ModelAdapter | None = None,
    ):
        self.supported_tasks = frozenset(supported_tasks)
        self.preprocessor = preprocessor
        self.model = model or DeferredModel()

    def handle(self, request: AIRequest) -> AIResponse:
        validate_request(request)
        if request.task not in self.supported_tasks:
            raise UnsupportedAIRequestError("This AI task is not enabled in the current release.")
        if self.preprocessor is None:
            raise UnsupportedAIRequestError("No approved preprocessing pipeline is configured.")
        prepared = self.preprocessor.transform(request.inputs, task=request.task)
        response = self.model.predict(prepared.features)
        response = validate_explainability_response(response)
        return validate_output(response)


def deferred_service() -> AIService:
    """Return the default service, which deliberately supports no task."""

    return AIService()
