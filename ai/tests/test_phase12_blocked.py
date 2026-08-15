"""Phase 12 tests for the legitimate blocked-by-data/model-selection path."""

from __future__ import annotations

import unittest
from pathlib import Path

from ai.core_errors import ModelUnavailableError
from ai.models.contracts import DeferredModel


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Phase12BlockedImplementationTests(unittest.TestCase):
    def test_blocker_documentation_states_exact_training_blocker(self):
        blocker = (PROJECT_ROOT / "docs" / "PHASE12_IMPLEMENTATION_BLOCKER.md").read_text(encoding="utf-8")
        self.assertIn("Actual model training was deferred because", blocker)
        self.assertIn("no approved, licensed dataset", blocker)

    def test_no_unselected_algorithm_module_was_created(self):
        algorithm_files = {
            path.name
            for path in (PROJECT_ROOT / "ai" / "algorithms").glob("*.py")
            if path.name != "__init__.py"
        }
        self.assertEqual(algorithm_files, set())

    def test_deferred_model_fails_closed_for_non_clinical_unit_input(self):
        with self.assertRaises(ModelUnavailableError):
            DeferredModel().predict({"fixture": "non-clinical-unit-test"})


if __name__ == "__main__":
    unittest.main()
