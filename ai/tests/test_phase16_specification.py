"""Phase 16 tests for the final AI specification; no training is performed."""

from __future__ import annotations

import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Phase16SpecificationTests(unittest.TestCase):
    def test_selected_capability_dataset_and_algorithm_are_documented(self):
        spec = (PROJECT_ROOT / "docs" / "PHASE16_AI_SPECIFICATION.md").read_text(encoding="utf-8")
        matrix = (PROJECT_ROOT / "docs" / "AI_CAPABILITY_DECISION_MATRIX.md").read_text(encoding="utf-8")
        self.assertIn("READY FOR PHASE 17 MODEL IMPLEMENTATION", spec)
        self.assertIn("UCI Heart Disease", spec)
        self.assertIn("Logistic Regression", spec)
        self.assertIn("disease_label_present", spec)
        self.assertIn("https://archive.ics.uci.edu/dataset/45/heart+disease", matrix)

    def test_phase16_contracts_remain_and_phase18_integration_is_narrow(self):
        spec = (PROJECT_ROOT / "docs" / "PHASE16_AI_SPECIFICATION.md").read_text(encoding="utf-8").lower()
        urls = (PROJECT_ROOT / "backend" / "config" / "urls.py").read_text(encoding="utf-8")
        ai_urls = (PROJECT_ROOT / "backend" / "apps" / "ai_api" / "urls.py").read_text(encoding="utf-8")
        self.assertIn("not trained", spec)
        self.assertIn("no dataset downloaded", spec)
        self.assertIn("no api is created", spec)
        self.assertIn("api/ai/", urls)
        self.assertIn("heart-risk/predict/", ai_urls)
        self.assertEqual(ai_urls.count("path("), 1)
        self.assertNotIn("api/chat/", urls)

    def test_phase16_decision_log_and_traceability_exist(self):
        decision_log = PROJECT_ROOT / "docs" / "PHASE16_AI_DECISION_LOG.md"
        traceability = (PROJECT_ROOT / "docs" / "AI_SRS_TRACEABILITY.md").read_text(encoding="utf-8")
        self.assertTrue(decision_log.exists())
        self.assertIn("Phase 16 final specification", traceability)
        self.assertIn("READY FOR PHASE 17 MODEL IMPLEMENTATION", traceability)

    def test_no_unapproved_model_or_dataset_artifacts_exist(self):
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
