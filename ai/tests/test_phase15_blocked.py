"""Phase 15 tests for the compliant blocked-by-data path."""

from __future__ import annotations

import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Phase15BlockedPathTests(unittest.TestCase):
    def test_phase15_blocker_documents_missing_gate_requirements(self):
        content = (PROJECT_ROOT / "docs" / "PHASE15_MODEL_IMPLEMENTATION_BLOCKER.md").read_text(encoding="utf-8")
        self.assertIn("**Outcome:** **BLOCKED**", content)
        self.assertIn("no approved dataset", content.lower())
        self.assertIn("final algorithm", content.lower())
        self.assertIn("training authorization", content.lower())

    def test_no_phase15_model_or_dataset_artifact_exists(self):
        forbidden_suffixes = {".pkl", ".joblib", ".onnx", ".pt", ".h5", ".model", ".csv", ".tsv", ".jsonl", ".parquet"}
        approved_phase17 = {
            "ai/data/processed/uci_heart_disease_cleveland_processed.csv",
            "ai/evaluation/logistic_coefficients.csv",
            "ai/evaluation/test_predictions.csv",
            "ai/models/artifacts/uci-heart-disease-logreg-v1.0.0.joblib",
        }
        found_unapproved = []
        for path in PROJECT_ROOT.rglob("*"):
            if "backend/venv" in path.as_posix() or "__pycache__" in path.as_posix():
                continue
            relative = path.relative_to(PROJECT_ROOT).as_posix()
            if path.is_file() and path.suffix.lower() in forbidden_suffixes and relative not in approved_phase17:
                found_unapproved.append(relative)
        self.assertEqual(found_unapproved, [])

    def test_phase15_does_not_expose_unapproved_prediction_endpoints(self):
        urls = (PROJECT_ROOT / "backend" / "config" / "urls.py").read_text(encoding="utf-8")
        self.assertIn("api/ai/", urls)
        self.assertIn("apps.ai_api.urls", urls)
        self.assertNotIn("api/chat/", urls)
        ai_urls = (PROJECT_ROOT / "backend" / "apps" / "ai_api" / "urls.py").read_text(encoding="utf-8")
        self.assertEqual(ai_urls.count("path("), 1)
        self.assertIn("heart-risk/predict/", ai_urls)
        self.assertNotIn("training", ai_urls)
        self.assertNotIn("upload", ai_urls)
