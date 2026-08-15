from __future__ import annotations

import json
from unittest.mock import patch

import pandas as pd
from django.core.cache import cache
from django.test import Client, TestCase

from apps.accounts.models import DoctorProfile, PatientProfile, User

from .constants import ACADEMIC_DISCLAIMER, FEATURE_ORDER, MODEL_VERSION
from .services import ModelUnavailableError, PredictionServiceError, get_model_bundle, predict


class Phase18AiApiTests(TestCase):
    endpoint = "/api/ai/heart-risk/predict/"

    def setUp(self):
        cache.clear()
        self.client = Client(enforce_csrf_checks=True)
        password = "A-strong-test-password-123"
        self.doctor_user = User.objects.create_user(
            email="phase18.doctor@example.test",
            password=password,
            first_name="Phase",
            last_name="Doctor",
            role=User.Role.DOCTOR,
        )
        DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization="Cardiology",
            license_id="PHASE18-LIC-001",
        )
        self.admin_user = User.objects.create_user(
            email="phase18.admin@example.test",
            password=password,
            first_name="Phase",
            last_name="Admin",
            role=User.Role.ADMINISTRATOR,
        )
        self.patient_user = User.objects.create_user(
            email="phase18.patient@example.test",
            password=password,
            first_name="Phase",
            last_name="Patient",
            role=User.Role.PATIENT,
        )
        PatientProfile.objects.create(user=self.patient_user)

    def csrf_token(self):
        return self.client.get("/api/auth/csrf/").json()["csrfToken"]

    def login_as(self, user):
        self.client.force_login(user)

    def valid_payload(self):
        return {
            "age": 55.0,
            "sex": 1,
            "cp": 3,
            "trestbps": 130.0,
            "chol": 240.0,
            "fbs": 0,
            "restecg": 1,
            "thalach": 150.0,
            "exang": 0,
            "oldpeak": 1.0,
            "slope": 2,
            "ca": 0,
            "thal": 3,
        }

    def post_json(self, payload, csrf=True, content_type="application/json", extra_headers=None):
        headers = {}
        if csrf:
            headers["HTTP_X_CSRFTOKEN"] = self.csrf_token()
        if extra_headers:
            headers.update(extra_headers)
        return self.client.post(
            self.endpoint,
            data=json.dumps(payload),
            content_type=content_type,
            **headers,
        )

    def test_unauthenticated_request_is_rejected(self):
        response = self.post_json(self.valid_payload(), csrf=False)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn("traceback", response.content.decode().lower())

    def test_patient_is_denied_and_doctor_and_admin_are_allowed(self):
        self.login_as(self.patient_user)
        patient_response = self.post_json(self.valid_payload())
        self.assertEqual(patient_response.status_code, 403)

        self.login_as(self.doctor_user)
        doctor_response = self.post_json(self.valid_payload())
        self.assertEqual(doctor_response.status_code, 200)

        self.login_as(self.admin_user)
        admin_response = self.post_json(self.valid_payload())
        self.assertEqual(admin_response.status_code, 200)

    def test_session_authenticated_post_requires_csrf(self):
        self.login_as(self.doctor_user)
        response = self.post_json(self.valid_payload(), csrf=False)
        self.assertEqual(response.status_code, 403)
        self.assertIn("csrf", response.content.decode().lower())

    def test_inactive_doctor_is_denied(self):
        self.doctor_user.is_active = False
        self.doctor_user.save(update_fields=["is_active"])
        self.login_as(self.doctor_user)
        response = self.post_json(self.valid_payload())
        self.assertEqual(response.status_code, 403)
        self.assertNotIn("traceback", response.content.decode().lower())

    def test_only_post_is_a_prediction_method(self):
        self.login_as(self.doctor_user)
        csrf = self.csrf_token()
        for method in ("get", "put", "patch", "delete"):
            if method == "get":
                response = self.client.get(self.endpoint)
            elif method == "delete":
                response = self.client.delete(self.endpoint, HTTP_X_CSRFTOKEN=csrf)
            else:
                response = getattr(self.client, method)(
                    self.endpoint,
                    data=json.dumps(self.valid_payload()),
                    content_type="application/json",
                    HTTP_X_CSRFTOKEN=csrf,
                )
            self.assertEqual(response.status_code, 405, method)

    def test_valid_request_returns_actual_structured_output(self):
        self.login_as(self.doctor_user)
        response = self.post_json(self.valid_payload())
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["model"], MODEL_VERSION)
        self.assertIn(payload["prediction"], {"label_absent", "label_present"})
        self.assertIsInstance(payload["model_probability"], float)
        self.assertGreaterEqual(payload["model_probability"], 0.0)
        self.assertLessEqual(payload["model_probability"], 1.0)
        self.assertEqual(payload["status"], "academic_development_only")
        self.assertEqual(payload["disclaimer"], ACADEMIC_DISCLAIMER)
        serialized = json.dumps(payload).lower()
        for forbidden in ("/home/", "traceback", "password", "secret", "patient_id", "session"):
            self.assertNotIn(forbidden, serialized)

    def test_response_contains_real_model_tied_feature_contributions(self):
        self.login_as(self.doctor_user)
        response = self.post_json(self.valid_payload())
        self.assertEqual(response.status_code, 200)
        explanation = response.json()["explanation"]
        self.assertEqual(explanation["method"], "logistic_regression_native_coefficient_contribution")
        self.assertEqual(explanation["output_space"], "logit")
        self.assertEqual([row["feature"] for row in explanation["features"]], list(FEATURE_ORDER))
        self.assertEqual(len(explanation["features"]), 13)
        self.assertTrue(all(isinstance(row["contribution"], float) for row in explanation["features"]))
        self.assertTrue(all(row["direction"] in {"supports_predicted_class", "opposes_predicted_class", "neutral"} for row in explanation["features"]))
        self.assertIn("model", explanation["disclaimer"].lower())

    def test_explanation_components_match_real_model_decision_function(self):
        features = self.valid_payload()
        result = predict(features)
        bundle = get_model_bundle()
        frame = pd.DataFrame([[features[field] for field in FEATURE_ORDER]], columns=FEATURE_ORDER)
        decision = float(bundle["pipeline"].decision_function(frame)[0])
        explanation = result["explanation"]
        component_sum = explanation["base_value"] + sum(row["contribution"] for row in explanation["features"])
        self.assertAlmostEqual(component_sum, decision, places=10)
        self.assertEqual(result["prediction"], "label_present" if decision >= 0 else "label_absent")

    def test_explanation_is_deterministic_and_changes_with_input(self):
        features = self.valid_payload()
        first = predict(features)["explanation"]
        second = predict(features)["explanation"]
        self.assertEqual(first, second)
        changed = dict(features)
        changed["chol"] = 300.0
        changed_result = predict(changed)["explanation"]
        self.assertTrue(any(
            left["contribution"] != right["contribution"]
            for left, right in zip(first["features"], changed_result["features"], strict=True)
        ))

    def test_missing_input_cannot_reach_explanation_generation(self):
        self.login_as(self.doctor_user)
        payload = self.valid_payload()
        del payload["age"]
        with patch("apps.ai_api.views.predict") as mocked_predict:
            response = self.post_json(payload)
        self.assertEqual(response.status_code, 400)
        mocked_predict.assert_not_called()

    def test_missing_feature_is_rejected(self):
        self.login_as(self.doctor_user)
        payload = self.valid_payload()
        del payload["age"]
        response = self.post_json(payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("age", response.json())

    def test_unknown_fields_model_selection_and_patient_identifier_are_rejected(self):
        self.login_as(self.doctor_user)
        for field in ("model", "model_path", "patient_id", "prediction_id", "upload"):
            payload = self.valid_payload()
            payload[field] = "not-permitted"
            response = self.post_json(payload)
            self.assertEqual(response.status_code, 400, field)
            self.assertIn(field, response.json())

    def test_invalid_types_are_rejected(self):
        self.login_as(self.doctor_user)
        for field, value in (("age", "55"), ("sex", "1"), ("cp", 3.0), ("chol", None)):
            payload = self.valid_payload()
            payload[field] = value
            response = self.post_json(payload)
            self.assertEqual(response.status_code, 400, field)
            self.assertIn(field, response.json())

    def test_nonfinite_values_are_rejected(self):
        self.login_as(self.doctor_user)
        for value in (float("nan"), float("inf"), float("-inf")):
            payload = self.valid_payload()
            payload["oldpeak"] = value
            response = self.post_json(payload)
            self.assertEqual(response.status_code, 400)
            self.assertNotIn("traceback", response.content.decode().lower())
            self.assertNotIn("oldpeak", response.content.decode().lower())

    def test_invalid_ranges_and_categories_are_rejected(self):
        self.login_as(self.doctor_user)
        cases = (("age", 28.0), ("age", 78.0), ("trestbps", 0.0), ("cp", 5), ("thal", 4), ("ca", 4))
        for field, value in cases:
            payload = self.valid_payload()
            payload[field] = value
            response = self.post_json(payload)
            self.assertEqual(response.status_code, 400, field)
            self.assertIn(field, response.json())

    def test_malformed_json_and_wrong_content_type_are_rejected(self):
        self.login_as(self.doctor_user)
        malformed = self.client.post(
            self.endpoint,
            data='{"age":',
            content_type="application/json",
            HTTP_X_CSRFTOKEN=self.csrf_token(),
        )
        self.assertEqual(malformed.status_code, 400)
        self.assertNotIn("traceback", malformed.content.decode().lower())

        wrong_type = self.client.post(
            self.endpoint,
            data=self.valid_payload(),
            content_type="multipart/form-data",
            HTTP_X_CSRFTOKEN=self.csrf_token(),
        )
        self.assertEqual(wrong_type.status_code, 415)

    def test_oversized_request_is_rejected_without_model_execution(self):
        self.login_as(self.doctor_user)
        oversized_body = json.dumps(self.valid_payload()) + (" " * 9000)
        with patch("apps.ai_api.views.predict") as mocked_predict:
            response = self.client.post(
                self.endpoint,
                data=oversized_body,
                content_type="application/json",
                HTTP_X_CSRFTOKEN=self.csrf_token(),
            )
        self.assertEqual(response.status_code, 413)
        mocked_predict.assert_not_called()

    def test_rate_limit_returns_429_after_configured_limit(self):
        cache.clear()
        self.login_as(self.doctor_user)
        with patch("apps.ai_api.views.predict", return_value={
            "model": MODEL_VERSION,
            "prediction": "label_absent",
            "model_probability": 0.25,
            "status": "academic_development_only",
        }):
            statuses = [self.post_json(self.valid_payload()).status_code for _ in range(61)]
        self.assertEqual(statuses[:60], [200] * 60)
        self.assertEqual(statuses[60], 429)

    def test_fixed_phase17_artifact_is_loaded_once_without_training(self):
        first = get_model_bundle()
        second = get_model_bundle()
        self.assertIs(first, second)
        self.assertEqual(first["model_version"], MODEL_VERSION)
        self.assertEqual(first["feature_columns"], [
            "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach",
            "exang", "oldpeak", "slope", "ca", "thal",
        ])

    def test_model_loading_failure_is_generic_and_does_not_expose_path(self):
        self.login_as(self.doctor_user)
        with patch("apps.ai_api.views.predict", side_effect=ModelUnavailableError("/private/model/path")):
            response = self.post_json(self.valid_payload())
        self.assertEqual(response.status_code, 503)
        body = response.content.decode().lower()
        self.assertIn("temporarily unavailable", body)
        self.assertNotIn("private/model/path", body)
        self.assertNotIn("traceback", body)

    def test_prediction_failure_is_generic(self):
        self.login_as(self.doctor_user)
        with patch("apps.ai_api.views.predict", side_effect=PredictionServiceError("internal failure")):
            response = self.post_json(self.valid_payload())
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "AI prediction could not be completed."})

    def test_unexpected_failure_is_generic(self):
        self.login_as(self.doctor_user)
        with patch("apps.ai_api.views.predict", side_effect=RuntimeError("private internal error")):
            response = self.post_json(self.valid_payload())
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "An unexpected server error occurred."})
        self.assertNotIn("private internal error", response.content.decode())


class Phase18ApiSmokeTests(TestCase):
    endpoint = Phase18AiApiTests.endpoint

    def setUp(self):
        Phase18AiApiTests.setUp(self)

    def csrf_token(self):
        return self.client.get("/api/auth/csrf/").json()["csrfToken"]

    def login_as(self, user):
        self.client.force_login(user)

    def valid_payload(self):
        return Phase18AiApiTests.valid_payload(self)

    def test_manual_smoke_status_matrix(self):
        results = {}
        results["unauthenticated"] = Phase18AiApiTests.post_json(
            self, Phase18AiApiTests.valid_payload(self), csrf=False
        ).status_code

        Phase18AiApiTests.login_as(self, self.doctor_user)
        results["authorized_doctor_valid"] = Phase18AiApiTests.post_json(
            self, Phase18AiApiTests.valid_payload(self)
        ).status_code
        invalid = Phase18AiApiTests.valid_payload(self)
        del invalid["age"]
        results["authorized_doctor_invalid"] = Phase18AiApiTests.post_json(self, invalid).status_code

        Phase18AiApiTests.login_as(self, self.patient_user)
        results["unauthorized_patient"] = Phase18AiApiTests.post_json(
            self, Phase18AiApiTests.valid_payload(self)
        ).status_code

        Phase18AiApiTests.login_as(self, self.admin_user)
        results["authorized_admin_valid"] = Phase18AiApiTests.post_json(
            self, Phase18AiApiTests.valid_payload(self)
        ).status_code
        print(f"PHASE18_SMOKE_RESULTS={json.dumps(results, sort_keys=True)}")
        self.assertEqual(results, {
            "unauthenticated": 403,
            "authorized_doctor_valid": 200,
            "authorized_doctor_invalid": 400,
            "unauthorized_patient": 403,
            "authorized_admin_valid": 200,
        })
