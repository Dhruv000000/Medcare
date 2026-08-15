from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

import pandas as pd

from .constants import FEATURE_ORDER, PREPROCESSING_VERSION

EXPLANATION_METHOD = "logistic_regression_native_coefficient_contribution"
EXPLANATION_DISCLAIMER = (
    "Feature contributions describe this model's behavior for the submitted values. "
    "They do not establish biological causation, clinical importance, diagnosis, "
    "treatment advice, or medical certainty."
)


class ExplanationServiceError(Exception):
    """Raised when a safe model-tied explanation cannot be produced."""


def _original_feature_name(transformed_name: str) -> str:
    """Map the fitted preprocessor's transformed name to one source feature."""

    prefix, separator, remainder = transformed_name.partition("__")
    if not separator or prefix not in {"numeric", "categorical"}:
        raise ExplanationServiceError("Unexpected fitted feature name.")
    if prefix == "numeric":
        if remainder not in FEATURE_ORDER:
            raise ExplanationServiceError("Unexpected fitted numeric feature.")
        return remainder

    matches = [
        feature
        for feature in FEATURE_ORDER
        if remainder == feature or remainder.startswith(f"{feature}_")
    ]
    if len(matches) != 1:
        raise ExplanationServiceError("Unexpected fitted categorical feature.")
    return matches[0]


def _direction(contribution: float, prediction: int) -> str:
    if math.isclose(contribution, 0.0, abs_tol=1e-12):
        return "neutral"
    supports_present = contribution > 0
    supports_prediction = supports_present if prediction == 1 else not supports_present
    return "supports_predicted_class" if supports_prediction else "opposes_predicted_class"


def build_explanation(bundle: dict[str, Any], features: dict[str, Any], prediction: int) -> dict[str, Any]:
    """Build deterministic local contributions from the immutable fitted pipeline."""

    if prediction not in {0, 1}:
        raise ExplanationServiceError("Prediction is outside the approved binary target.")
    pipeline = bundle.get("pipeline")
    if pipeline is None:
        raise ExplanationServiceError("Approved pipeline is unavailable.")
    try:
        preprocessor = pipeline.named_steps["preprocess"]
        classifier = pipeline.named_steps["model"]
        frame = pd.DataFrame(
            [[features[field] for field in FEATURE_ORDER]],
            columns=list(FEATURE_ORDER),
        )
        transformed = preprocessor.transform(frame)
        transformed_names = list(preprocessor.get_feature_names_out())
        coefficients = classifier.coef_[0]
        intercept = float(classifier.intercept_[0])
    except Exception as exc:
        raise ExplanationServiceError("Fitted pipeline cannot produce an explanation.") from exc

    if transformed.shape[0] != 1 or transformed.shape[1] != len(transformed_names):
        raise ExplanationServiceError("Fitted preprocessing output has an unexpected shape.")
    if len(coefficients) != len(transformed_names) or not math.isfinite(intercept):
        raise ExplanationServiceError("Fitted classifier coefficients are incompatible.")

    aggregated: dict[str, float] = defaultdict(float)
    for transformed_name, transformed_value, coefficient in zip(
        transformed_names,
        transformed[0],
        coefficients,
        strict=True,
    ):
        value = float(transformed_value)
        coefficient_value = float(coefficient)
        contribution = value * coefficient_value
        if not all(math.isfinite(item) for item in (value, coefficient_value, contribution)):
            raise ExplanationServiceError("Fitted model produced a non-finite contribution.")
        aggregated[_original_feature_name(transformed_name)] += contribution

    if set(aggregated) != set(FEATURE_ORDER):
        raise ExplanationServiceError("Explanation does not cover the approved feature schema.")

    feature_rows = []
    for feature in FEATURE_ORDER:
        contribution = float(aggregated[feature])
        if not math.isfinite(contribution):
            raise ExplanationServiceError("Explanation contains a non-finite contribution.")
        feature_rows.append(
            {
                "feature": feature,
                "value": float(features[feature]),
                "contribution": contribution,
                "direction": _direction(contribution, prediction),
            }
        )

    decision_from_components = intercept + sum(row["contribution"] for row in feature_rows)
    if not math.isfinite(decision_from_components):
        raise ExplanationServiceError("Explanation decision value is non-finite.")
    if (prediction == 1 and decision_from_components < 0) or (prediction == 0 and decision_from_components > 0):
        raise ExplanationServiceError("Explanation does not agree with the model prediction boundary.")

    return {
        "method": EXPLANATION_METHOD,
        "preprocessing": PREPROCESSING_VERSION,
        "output_space": "logit",
        "base_value": intercept,
        "features": feature_rows,
        "disclaimer": EXPLANATION_DISCLAIMER,
    }
