from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
AI_API = BACKEND / "apps" / "ai_api"
FRONTEND = ROOT / "frontend"


class Phase22HardeningTests(unittest.TestCase):
    def read(self, path):
        return path.read_text(encoding="utf-8")

    def test_production_configuration_fails_closed(self):
        settings = self.read(BACKEND / "config" / "settings.py")
        self.assertIn("DJANGO_ENV", settings)
        self.assertIn("ImproperlyConfigured", settings)
        self.assertIn("DJANGO_SECRET_KEY must be set", settings)
        self.assertIn("DEBUG must be false", settings)
        self.assertIn("ALLOWED_HOSTS must be set", settings)
        self.assertIn("FRONTEND_ALLOWED_ORIGINS must be set", settings)
        self.assertIn("SESSION_COOKIE_SECURE = IS_PRODUCTION", settings)
        self.assertIn("CSRF_COOKIE_SECURE = IS_PRODUCTION", settings)
        self.assertIn("SECURE_SSL_REDIRECT = IS_PRODUCTION", settings)
        self.assertIn("SECURE_HSTS_SECONDS = 31536000 if IS_PRODUCTION else 0", settings)
        self.assertIn("SECURE_CONTENT_TYPE_NOSNIFF = True", settings)
        self.assertIn('SECURE_REFERRER_POLICY = "same-origin"', settings)

    def test_ai_failure_logging_does_not_emit_stack_trace(self):
        service = self.read(AI_API / "services.py")
        self.assertNotIn("logger.exception", service)
        self.assertIn("exception_type=%s", service)

    def test_inference_dependencies_are_pinned(self):
        requirements = self.read(BACKEND / "requirements.txt")
        for package in ("numpy==", "pandas==", "scikit-learn==", "joblib=="):
            self.assertIn(package, requirements)

    def test_fixed_route_and_artifact_boundary_remain_narrow(self):
        urls = self.read(AI_API / "urls.py")
        constants = self.read(AI_API / "constants.py")
        services = self.read(AI_API / "services.py")
        self.assertEqual(urls.count("heart-risk/predict/"), 1)
        self.assertIn("ARTIFACT_FILENAME", constants)
        self.assertIn("artifact_path(project_root)", services)
        self.assertNotIn("request.", services)
        self.assertIn("_sha256(model_file)", services)

    def test_patient_frontend_remains_without_prediction_call(self):
        patient_js = self.read(FRONTEND / "js" / "patient" / "patient-ai-insights.js")
        ai_start = patient_js.index("function showDeferredMessage")
        ai_code = patient_js[ai_start:]
        self.assertNotIn("heart-risk/predict", ai_code)
        self.assertNotIn("localStorage", ai_code)
        self.assertNotIn("sessionStorage", ai_code)

    def test_doctor_ai_wording_remains_nonclinical_and_safe(self):
        doctor_js = self.read(FRONTEND / "js" / "doctor" / "doctor-dashboard.js")
        doctor_html = self.read(FRONTEND / "pages" / "doctor" / "doctor-dashboard.html")
        ai_start = doctor_js.index("const AI_ENDPOINT =")
        ai_code = doctor_js[ai_start:]
        self.assertIn("Doctor decision boundary", ai_code)
        self.assertNotIn("innerHTML", ai_code)
        self.assertNotIn("localStorage", ai_code)
        self.assertIn("not diagnostic confidence", doctor_html)
        self.assertIn("not a diagnosis or medical advice", doctor_html)


if __name__ == "__main__":
    unittest.main()
