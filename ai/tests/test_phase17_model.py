from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd
from joblib import load


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET = PROJECT_ROOT / "ai" / "data" / "processed" / "uci_heart_disease_cleveland_processed.csv"
MANIFEST = PROJECT_ROOT / "ai" / "data" / "processed" / "phase17_dataset_inspection.json"
METRICS = PROJECT_ROOT / "ai" / "evaluation" / "phase17_metrics.json"
ARTIFACT = PROJECT_ROOT / "ai" / "models" / "artifacts" / "uci-heart-disease-logreg-v1.0.0.joblib"
ARTIFACT_HASH = PROJECT_ROOT / "ai" / "models" / "artifacts" / "uci-heart-disease-logreg-v1.0.0.joblib.sha256"
FEATURES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach",
    "exang", "oldpeak", "slope", "ca", "thal",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class Phase17DatasetTests(unittest.TestCase):
    def test_dataset_exists_and_has_expected_schema(self):
        self.assertTrue(DATASET.exists())
        frame = pd.read_csv(DATASET)
        self.assertEqual(frame.shape, (303, 15))
        self.assertEqual(frame[FEATURES + ["num", "disease_label_present"]].columns.tolist(), FEATURES + ["num", "disease_label_present"])
        self.assertEqual(sorted(frame["num"].dropna().astype(int).unique().tolist()), [0, 1, 2, 3, 4])

    def test_dataset_manifest_records_actual_inspection(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["records"], 303)
        self.assertEqual(manifest["raw_columns"], 14)
        self.assertEqual(manifest["duplicate_rows"], 0)
        self.assertEqual(manifest["missing_counts"]["ca"], 4)
        self.assertEqual(manifest["missing_counts"]["thal"], 2)
        self.assertEqual(manifest["normalized_target_distribution"], {"0": 164, "1": 139})


class Phase17PreprocessingTests(unittest.TestCase):
    def test_missing_categorical_values_are_supported_by_fitted_pipeline(self):
        bundle = load(ARTIFACT)
        sample = pd.DataFrame([{feature: 0 for feature in FEATURES}])
        sample.loc[0, "age"] = 55
        sample.loc[0, "cp"] = 3
        sample.loc[0, "trestbps"] = 130
        sample.loc[0, "chol"] = 240
        sample.loc[0, "thalach"] = 150
        sample.loc[0, "oldpeak"] = 1.0
        sample.loc[0, "ca"] = pd.NA
        sample.loc[0, "thal"] = pd.NA
        prediction = bundle["pipeline"].predict(sample)
        self.assertEqual(prediction.shape, (1,))
        self.assertIn(int(prediction[0]), {0, 1})


class Phase17ModelTests(unittest.TestCase):
    def test_artifact_hash_and_pipeline_components(self):
        self.assertTrue(ARTIFACT.exists())
        expected = ARTIFACT_HASH.read_text(encoding="utf-8").split()[0]
        self.assertEqual(expected, sha256(ARTIFACT))
        bundle = load(ARTIFACT)
        self.assertEqual(bundle["model_version"], "uci-heart-disease-logreg-v1.0.0")
        self.assertEqual(bundle["feature_columns"], FEATURES)
        self.assertIn("preprocess", bundle["pipeline"].named_steps)
        self.assertIn("model", bundle["pipeline"].named_steps)

    def test_model_accepts_valid_input_and_returns_binary_output(self):
        frame = pd.read_csv(DATASET)
        bundle = load(ARTIFACT)
        prediction = bundle["pipeline"].predict(frame[FEATURES].iloc[[0]])
        self.assertEqual(prediction.shape, (1,))
        self.assertIn(int(prediction[0]), {0, 1})


class Phase17EvaluationTests(unittest.TestCase):
    def test_actual_metrics_and_confusion_matrix_are_recorded(self):
        metrics = json.loads(METRICS.read_text(encoding="utf-8"))
        self.assertEqual(metrics["dataset_records"], 303)
        self.assertEqual(metrics["split"]["train_records"], 242)
        self.assertEqual(metrics["split"]["test_records"], 61)
        self.assertIn("majority_baseline", metrics["test_metrics"])
        self.assertIn("logistic_regression", metrics["test_metrics"])
        matrix = metrics["test_metrics"]["logistic_regression"]["confusion_matrix"]
        self.assertEqual(matrix, [[28, 5], [2, 26]])
        self.assertEqual(sum(sum(row) for row in matrix), 61)
        self.assertGreater(metrics["test_metrics"]["logistic_regression"]["roc_auc"], 0.0)

    def test_alternative_models_are_recorded_on_same_test_size(self):
        metrics = json.loads(METRICS.read_text(encoding="utf-8"))
        for name in ("decision_tree", "random_forest"):
            self.assertEqual(metrics["test_metrics"][name]["n"], 61)
            self.assertIn("roc_auc", metrics["test_metrics"][name])


class Phase17SecurityTests(unittest.TestCase):
    def test_evaluation_script_uses_fixed_artifact_path_and_no_api(self):
        source = (PROJECT_ROOT / "ai" / "phase17_evaluate.py").read_text(encoding="utf-8")
        self.assertIn("ARTIFACT_PATH =", source)
        self.assertNotIn("sys.argv", source)
        self.assertNotIn("api/ai/", source)
        self.assertNotIn("api/chat/", source)
        self.assertNotIn("backend", source.lower())
        self.assertNotIn("postgres", source.lower())

    def test_metadata_has_no_secret_markers(self):
        metadata = (PROJECT_ROOT / "ai" / "evaluation" / "phase17_metadata.json").read_text(encoding="utf-8").lower()
        for marker in ("openai_api_key", "aws_secret_access_key", "private key", "password", "secret"):
            self.assertNotIn(marker, metadata)
