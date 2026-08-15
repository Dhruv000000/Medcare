from __future__ import annotations

from pathlib import Path

MODEL_VERSION = "uci-heart-disease-logreg-v1.0.0"
PREPROCESSING_VERSION = "phase17_numeric_median_scaler_categorical_mode_onehot_v1"
ARTIFACT_FILENAME = f"{MODEL_VERSION}.joblib"
ARTIFACT_CHECKSUM_FILENAME = f"{ARTIFACT_FILENAME}.sha256"
FEATURE_ORDER = (
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
)
NUMERIC_FEATURES = ("age", "trestbps", "chol", "thalach", "oldpeak")
CATEGORICAL_FEATURES = ("sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal")
CATEGORICAL_DOMAINS = {
    "sex": {0, 1},
    "cp": {1, 2, 3, 4},
    "fbs": {0, 1},
    "restecg": {0, 1, 2},
    "exang": {0, 1},
    "slope": {1, 2, 3},
    "ca": {0, 1, 2, 3},
    "thal": {3, 6, 7},
}
# These are observed support-domain bounds in the verified Phase 17 Cleveland
# training file, not clinical reference intervals or diagnostic thresholds.
NUMERIC_SUPPORT_DOMAINS = {
    "age": (29.0, 77.0),
    "trestbps": (94.0, 200.0),
    "chol": (126.0, 564.0),
    "thalach": (71.0, 202.0),
    "oldpeak": (0.0, 6.2),
}
MAX_REQUEST_BYTES = 8192
ACADEMIC_DISCLAIMER = (
    "This output comes from an academic development-only model trained on the UCI "
    "Heart Disease dataset. It is not clinically validated, is not a diagnosis or "
    "medical advice, and must not replace a qualified healthcare professional."
)


def artifact_path(project_root: Path) -> Path:
    """Return the only approved internal artifact path; never use request input."""

    return project_root / "ai" / "models" / "artifacts" / ARTIFACT_FILENAME


def artifact_checksum_path(project_root: Path) -> Path:
    return project_root / "ai" / "models" / "artifacts" / ARTIFACT_CHECKSUM_FILENAME
