from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
from joblib import load
from sklearn.metrics import average_precision_score, balanced_accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score, accuracy_score
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "ai" / "data" / "processed" / "uci_heart_disease_cleveland_processed.csv"
ARTIFACT_PATH = PROJECT_ROOT / "ai" / "models" / "artifacts" / "uci-heart-disease-logreg-v1.0.0.joblib"
HASH_PATH = PROJECT_ROOT / "ai" / "models" / "artifacts" / "uci-heart-disease-logreg-v1.0.0.joblib.sha256"
OUTPUT_PATH = PROJECT_ROOT / "ai" / "evaluation" / "phase17_evaluation_validation.json"
FEATURE_COLUMNS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach",
    "exang", "oldpeak", "slope", "ca", "thal",
]
TARGET_COLUMN = "disease_label_present"
SEED = 42
TEST_SIZE = 0.20


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if ARTIFACT_PATH.parent != PROJECT_ROOT / "ai" / "models" / "artifacts":
        raise RuntimeError("Artifact path escaped the fixed project artifact directory")
    if not ARTIFACT_PATH.exists() or not HASH_PATH.exists():
        raise FileNotFoundError("Expected fixed model artifact or checksum is missing")
    expected_hash = HASH_PATH.read_text(encoding="utf-8").split()[0]
    actual_hash = sha256(ARTIFACT_PATH)
    if expected_hash != actual_hash:
        raise ValueError("Model artifact checksum mismatch")

    bundle = load(ARTIFACT_PATH)
    required = {"artifact_type", "artifact_version", "model_version", "feature_columns", "target_column", "pipeline", "metadata"}
    if not required.issubset(bundle):
        raise ValueError(f"Artifact bundle is missing required keys: {sorted(required - set(bundle))}")
    if bundle["feature_columns"] != FEATURE_COLUMNS or bundle["target_column"] != TARGET_COLUMN:
        raise ValueError("Artifact schema does not match the approved Phase 17 schema")

    df = pd.read_csv(DATA_PATH)
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN].astype(int)
    _, X_test, _, y_test = train_test_split(X, y, test_size=TEST_SIZE, stratify=y, random_state=SEED)
    pipeline = bundle["pipeline"]
    prediction = pipeline.predict(X_test)
    score = pipeline.predict_proba(X_test)[:, 1]
    tn, fp, fn, tp = confusion_matrix(y_test, prediction, labels=[0, 1]).ravel()
    result = {
        "model_version": bundle["model_version"],
        "artifact_sha256": actual_hash,
        "test_records": int(len(y_test)),
        "metrics": {
            "accuracy": float(accuracy_score(y_test, prediction)),
            "balanced_accuracy": float(balanced_accuracy_score(y_test, prediction)),
            "precision": float(precision_score(y_test, prediction, zero_division=0)),
            "recall_sensitivity": float(recall_score(y_test, prediction, zero_division=0)),
            "specificity": float(tn / (tn + fp)) if (tn + fp) else None,
            "f1": float(f1_score(y_test, prediction, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, score)),
            "pr_auc": float(average_precision_score(y_test, score)),
            "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
        },
        "checks": {
            "fixed_artifact_path": True,
            "checksum_verified": True,
            "schema_verified": True,
            "test_split_recreated": True,
            "no_patient_data_access": True,
        },
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
