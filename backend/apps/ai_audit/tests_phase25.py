import json
from datetime import date
from unittest import mock

from django.test import Client, TestCase
from rest_framework.exceptions import APIException

from apps.accounts.models import DoctorProfile, PatientProfile, User
from apps.ai_api.services import PredictionServiceError

from .models import AiPredictionEvent


class Phase25PredictionReportingTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.password = "Phase25-Synthetic-Password-123!"
        self.doctor_user = User.objects.create_user(
            email="phase25.doctor.one@example.test",
            password=self.password,
            first_name="Phase25",
            last_name="Doctor One",
            role=User.Role.DOCTOR,
        )
        self.doctor = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization="Cardiology",
            license_id="PHASE25-001",
        )
        self.other_doctor_user = User.objects.create_user(
            email="phase25.doctor.two@example.test",
            password=self.password,
            first_name="Phase25",
            last_name="Doctor Two",
            role=User.Role.DOCTOR,
        )
        self.other_doctor = DoctorProfile.objects.create(
            user=self.other_doctor_user,
            specialization="Dermatology",
            license_id="PHASE25-002",
        )
        self.patient_user = User.objects.create_user(
            email="phase25.patient@example.test",
            password=self.password,
            first_name="Phase25",
            last_name="Patient",
            role=User.Role.PATIENT,
        )
        PatientProfile.objects.create(user=self.patient_user)
        self.admin_user = User.objects.create_user(
            email="phase25.admin@example.test",
            password=self.password,
            first_name="Phase25",
            last_name="Admin",
            role=User.Role.ADMINISTRATOR,
            is_staff=True,
        )
        self.valid_payload = {
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

    def csrf_token(self):
        return self.client.get("/api/auth/csrf/").json()["csrfToken"]

    def login_as(self, user):
        self.client.force_login(user)

    def post_prediction(self, payload=None):
        return self.client.post(
            "/api/ai/heart-risk/predict/",
            data=json.dumps(payload or self.valid_payload),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=self.csrf_token(),
        )

    def test_successful_authorized_prediction_creates_minimized_server_owned_event(self):
        self.login_as(self.doctor_user)
        response = self.post_prediction()
        self.assertEqual(response.status_code, 200, response.content)
        event = AiPredictionEvent.objects.get()
        self.assertEqual(event.requesting_user, self.doctor_user)
        self.assertEqual(event.requesting_role, User.Role.DOCTOR)
        self.assertEqual(event.status, AiPredictionEvent.Status.COMPLETED)
        self.assertEqual(event.model_version, "uci-heart-disease-logreg-v1.0.0")
        self.assertIsNotNone(event.created_at)
        self.assertIn(event.prediction_label, {"label_absent", "label_present"})
        self.assertIsNotNone(event.model_probability)
        self.assertFalse(any("value" in item for item in event.explanation.get("features", [])))
        self.assertNotIn("patient_id", event.explanation)
        self.assertEqual(len(event.explanation["features"]), 13)
        self.assertNotIn("disclaimer", event.explanation)

    def test_validation_failure_is_recorded_without_submitted_features(self):
        self.login_as(self.doctor_user)
        payload = dict(self.valid_payload)
        payload.pop("age")
        response = self.post_prediction(payload)
        self.assertEqual(response.status_code, 400)
        event = AiPredictionEvent.objects.get()
        self.assertEqual(event.status, AiPredictionEvent.Status.VALIDATION_FAILED)
        self.assertEqual(event.prediction_label, "")
        self.assertIsNone(event.model_probability)
        self.assertEqual(event.explanation, {})

    @mock.patch("apps.ai_api.views.predict", side_effect=PredictionServiceError)
    def test_prediction_failure_is_recorded_without_exposing_internal_error(self, _predict):
        self.login_as(self.doctor_user)
        response = self.post_prediction()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "AI prediction could not be completed."})
        event = AiPredictionEvent.objects.get()
        self.assertEqual(event.status, AiPredictionEvent.Status.INFERENCE_FAILED)
        self.assertEqual(event.explanation, {})

    def test_patient_and_unauthenticated_report_access_is_denied(self):
        self.assertEqual(self.client.get("/api/ai/reports/").status_code, 403)
        self.login_as(self.patient_user)
        self.assertEqual(self.client.get("/api/ai/reports/").status_code, 403)
        self.assertEqual(self.post_prediction().status_code, 403)
        self.assertFalse(AiPredictionEvent.objects.exists())

    def test_doctor_can_only_list_and_retrieve_own_completed_reports(self):
        self.login_as(self.doctor_user)
        self.assertEqual(self.post_prediction().status_code, 200)
        own = AiPredictionEvent.objects.get()
        self.login_as(self.other_doctor_user)
        self.assertEqual(self.client.get("/api/ai/reports/").status_code, 200)
        self.assertEqual(self.client.get("/api/ai/reports/").json(), [])
        response = self.client.get(f"/api/ai/reports/{own.event_id}/")
        self.assertEqual(response.status_code, 404)
        self.login_as(self.doctor_user)
        list_response = self.client.get("/api/ai/reports/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)
        detail = self.client.get(f"/api/ai/reports/{own.event_id}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["model_version"], "uci-heart-disease-logreg-v1.0.0")
        self.assertIn("not diagnostic confidence", detail.json()["probability_note"])
        self.assertIn("clinician remains responsible", detail.json()["clinician_responsibility"])

    def test_admin_sees_only_aggregate_audit_summary(self):
        self.login_as(self.doctor_user)
        self.assertEqual(self.post_prediction().status_code, 200)
        self.login_as(self.admin_user)
        response = self.client.get("/api/admin/ai-audit/summary/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total_events"], 1)
        self.assertEqual(payload["completed_events"], 1)
        self.assertEqual(payload["rejected_events"], 0)
        self.assertEqual(payload["model_versions"], ["uci-heart-disease-logreg-v1.0.0"])
        self.assertNotIn("patient_id", json.dumps(payload))
        self.assertNotIn("prediction_label", json.dumps(payload))
        self.assertEqual(self.client.get("/api/ai/reports/").status_code, 403)

    def test_report_routes_are_read_only_and_client_fields_are_not_accepted(self):
        self.login_as(self.doctor_user)
        self.assertEqual(self.client.post("/api/ai/reports/", data={}, HTTP_X_CSRFTOKEN=self.csrf_token()).status_code, 405)
        self.login_as(self.admin_user)
        self.assertEqual(self.client.post("/api/admin/ai-audit/summary/", data={}, HTTP_X_CSRFTOKEN=self.csrf_token()).status_code, 405)
        self.login_as(self.doctor_user)
        response = self.post_prediction(dict(self.valid_payload, model="attacker", event_id="attacker"))
        self.assertEqual(response.status_code, 400)
        event = AiPredictionEvent.objects.get()
        self.assertEqual(event.status, AiPredictionEvent.Status.VALIDATION_FAILED)
        self.assertEqual(event.explanation, {})

    def test_event_is_immutable_and_cannot_be_deleted(self):
        self.login_as(self.doctor_user)
        self.assertEqual(self.post_prediction().status_code, 200)
        event = AiPredictionEvent.objects.get()
        event.status = AiPredictionEvent.Status.INFERENCE_FAILED
        with self.assertRaises(ValueError):
            event.save()
        with self.assertRaises(ValueError):
            event.delete()

    def test_logout_denies_report_access(self):
        self.login_as(self.doctor_user)
        self.assertEqual(self.post_prediction().status_code, 200)
        event = AiPredictionEvent.objects.get()
        csrf = self.csrf_token()
        self.assertEqual(self.client.post("/api/auth/logout/", HTTP_X_CSRFTOKEN=csrf).status_code, 200)
        self.assertEqual(self.client.get(f"/api/ai/reports/{event.event_id}/").status_code, 403)
