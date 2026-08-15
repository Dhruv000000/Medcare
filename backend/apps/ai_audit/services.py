from __future__ import annotations

import math
from typing import Any

from apps.ai_api.constants import MODEL_VERSION, PREPROCESSING_VERSION

from .models import AiPredictionEvent


def _safe_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def minimize_explanation(explanation: dict[str, Any] | None) -> dict[str, Any]:
    """Persist model explanation metadata without raw feature values."""
    if not isinstance(explanation, dict):
        return {}
    features = []
    for item in explanation.get("features", []):
        if not isinstance(item, dict):
            continue
        contribution = _safe_float(item.get("contribution"))
        feature = item.get("feature")
        direction = item.get("direction")
        if not isinstance(feature, str) or not isinstance(direction, str) or contribution is None:
            continue
        features.append(
            {
                "feature": feature,
                "contribution": contribution,
                "direction": direction,
            }
        )
    return {
        "method": str(explanation.get("method", "")),
        "preprocessing": str(explanation.get("preprocessing", PREPROCESSING_VERSION)),
        "output_space": str(explanation.get("output_space", "")),
        "base_value": _safe_float(explanation.get("base_value")),
        "features": features,
    }


def record_prediction_event(request, status: str, result: dict[str, Any] | None = None) -> AiPredictionEvent | None:
    """Write a best-effort immutable event without changing inference behavior."""
    try:
        result = result or {}
        return AiPredictionEvent.objects.create(
            requesting_user=request.user,
            requesting_role=request.user.role,
            model_version=str(result.get("model", MODEL_VERSION)),
            preprocessing_version=str(
                result.get("explanation", {}).get("preprocessing", PREPROCESSING_VERSION)
                if isinstance(result.get("explanation"), dict)
                else PREPROCESSING_VERSION
            ),
            status=status,
            prediction_label=str(result.get("prediction", "")) if status == AiPredictionEvent.Status.COMPLETED else "",
            model_probability=_safe_float(result.get("model_probability")) if status == AiPredictionEvent.Status.COMPLETED else None,
            explanation=minimize_explanation(result.get("explanation")) if status == AiPredictionEvent.Status.COMPLETED else {},
        )
    except Exception:
        return None
