from __future__ import annotations

import hashlib
import logging
from functools import lru_cache
from pathlib import Path

import pandas as pd
from django.conf import settings
from joblib import load

from .constants import FEATURE_ORDER, MODEL_VERSION, artifact_checksum_path, artifact_path
from .explainability import build_explanation

logger = logging.getLogger(__name__)


class ModelUnavailableError(Exception):
    """Raised when the fixed approved artifact cannot be loaded safely."""


class PredictionServiceError(Exception):
    """Raised when inference cannot be completed safely."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _approved_project_root() -> Path:
    return Path(settings.BASE_DIR).parent


@lru_cache(maxsize=1)
def get_model_bundle() -> dict:
    """Load the one approved, checksum-verified artifact once per process."""

    project_root = _approved_project_root()
    model_file = artifact_path(project_root)
    checksum_file = artifact_checksum_path(project_root)
    try:
        if not model_file.is_file() or not checksum_file.is_file():
            raise ModelUnavailableError("Approved model artifact is unavailable.")
        expected_checksum = checksum_file.read_text(encoding="utf-8").split()[0]
        if _sha256(model_file) != expected_checksum:
            raise ModelUnavailableError("Approved model artifact checksum verification failed.")
        bundle = load(model_file)
        if not isinstance(bundle, dict):
            raise ModelUnavailableError("Approved model artifact has an invalid bundle type.")
        if bundle.get("model_version") != MODEL_VERSION:
            raise ModelUnavailableError("Approved model version is not available.")
        if bundle.get("feature_columns") != list(FEATURE_ORDER):
            raise ModelUnavailableError("Approved model schema is incompatible.")
        pipeline = bundle.get("pipeline")
        if pipeline is None or not callable(getattr(pipeline, "predict", None)):
            raise ModelUnavailableError("Approved model pipeline is incompatible.")
        if not callable(getattr(pipeline, "predict_proba", None)):
            raise ModelUnavailableError("Approved model probability output is unavailable.")
        return bundle
    except ModelUnavailableError as exc:
        logger.error(
            "Phase 18 approved model failed safe loading checks: exception_type=%s",
            type(exc).__name__,
        )
        raise
    except Exception as exc:
        logger.error(
            "Phase 18 approved model load failed safely: exception_type=%s",
            type(exc).__name__,
        )
        raise ModelUnavailableError("Approved model could not be loaded safely.") from exc


def predict(features: dict) -> dict:
    """Run stateless inference on validated feature values only."""

    try:
        bundle = get_model_bundle()
        frame = pd.DataFrame([[features[field] for field in FEATURE_ORDER]], columns=FEATURE_ORDER)
        pipeline = bundle["pipeline"]
        prediction = int(pipeline.predict(frame)[0])
        probability = float(pipeline.predict_proba(frame)[0][1])
        if prediction not in {0, 1} or not 0.0 <= probability <= 1.0:
            raise PredictionServiceError("Approved model returned an invalid output.")
        return {
            "model": MODEL_VERSION,
            "prediction": "label_present" if prediction == 1 else "label_absent",
            "model_probability": probability,
            "status": "academic_development_only",
            "explanation": build_explanation(bundle, features, prediction),
        }
    except ModelUnavailableError:
        raise
    except PredictionServiceError as exc:
        logger.error(
            "Phase 18 approved model returned an invalid output: exception_type=%s",
            type(exc).__name__,
        )
        raise
    except Exception as exc:
        logger.error(
            "Phase 18 inference failed safely: exception_type=%s",
            type(exc).__name__,
        )
        raise PredictionServiceError("Prediction could not be completed safely.") from exc
