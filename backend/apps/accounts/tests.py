import json

from django.test import Client, TestCase, override_settings
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from .models import DoctorProfile, PatientProfile, User
from .permissions import IsDoctor, IsPatient


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.registration_payload = {
            "first_name": "Test",
            "last_name": "Patient",
            "email": "test.patient@example.test",
            "phone": "9876543210",
            "date_of_birth": "1990-01-01",
            "gender": "Other",
            "role": "Patient",
            "password": "A-strong-test-password-123",
            "confirm_password": "A-strong-test-password-123",
        }

    def csrf_token(self):
        response = self.client.get("/api/auth/csrf/")
        self.assertEqual(response.status_code, 200)
        return response.json()["csrfToken"]

    def post_json(self, path, payload, csrf=True):
        headers = {"HTTP_X_CSRFTOKEN": self.csrf_token()} if csrf else {}
        return self.client.post(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            **headers,
        )

    def register_patient(self):
        response = self.post_json("/api/auth/register/", self.registration_payload)
        self.assertEqual(response.status_code, 201)
        return User.objects.get(email=self.registration_payload["email"])

    def test_successful_registration_creates_profile_and_hashes_password(self):
        response = self.post_json("/api/auth/register/", self.registration_payload)
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email=self.registration_payload["email"])
        self.assertTrue(user.check_password(self.registration_payload["password"]))
        self.assertNotEqual(user.password, self.registration_payload["password"])
        self.assertTrue(PatientProfile.objects.filter(user=user).exists())
        self.assertNotIn("password", response.json()["user"])
        self.assertNotIn("password", response.json()["user"])

    def test_duplicate_registration_is_rejected(self):
        self.register_patient()
        response = self.post_json("/api/auth/register/", self.registration_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("already exists", response.json()["email"][0])

    def test_invalid_registration_data_is_rejected(self):
        payload = {**self.registration_payload, "email": "not-an-email", "password": "short"}
        response = self.post_json("/api/auth/register/", payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json())
        self.assertIn("password", response.json())

    def test_doctor_registration_creates_doctor_profile(self):
        payload = {
            **self.registration_payload,
            "email": "doctor@example.test",
            "role": "Doctor",
            "doctor_id": "LIC-TEST-001",
        }
        response = self.post_json("/api/auth/register/", payload)
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email=payload["email"])
        self.assertEqual(user.role, User.Role.DOCTOR)
        self.assertEqual(user.doctor_profile.license_id, "LIC-TEST-001")
        self.assertFalse(PatientProfile.objects.filter(user=user).exists())
        self.assertTrue(DoctorProfile.objects.filter(user=user).exists())

    def test_admin_registration_requires_server_side_code(self):
        payload = {**self.registration_payload, "email": "admin@example.test", "role": "Admin", "admin_code": "wrong"}
        response = self.post_json("/api/auth/register/", payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("admin_code", response.json())

    def test_successful_login_and_current_user(self):
        self.register_patient()
        response = self.post_json(
            "/api/auth/login/",
            {"identifier": self.registration_payload["email"], "password": self.registration_payload["password"], "role": "Patient"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("_auth_user_id", self.client.session)
        current = self.client.get("/api/auth/me/")
        self.assertEqual(current.status_code, 200)
        data = current.json()["user"]
        self.assertEqual(data["email"], self.registration_payload["email"])
        self.assertEqual(data["role"], "patient")
        self.assertNotIn("password", data)
        self.assertNotIn("password_hash", data)

    def test_wrong_password_and_unknown_user_use_same_generic_error(self):
        self.register_patient()
        wrong_password = self.post_json(
            "/api/auth/login/",
            {"identifier": self.registration_payload["email"], "password": "wrong-password-123", "role": "Patient"},
        )
        unknown_user = self.post_json(
            "/api/auth/login/",
            {"identifier": "unknown@example.test", "password": "wrong-password-123", "role": "Patient"},
        )
        self.assertEqual(wrong_password.status_code, 400)
        self.assertEqual(unknown_user.status_code, 400)
        self.assertEqual(wrong_password.json()["detail"], "Invalid email or password.")
        self.assertEqual(unknown_user.json()["detail"], wrong_password.json()["detail"])

    def test_wrong_role_login_is_rejected(self):
        self.register_patient()
        response = self.post_json(
            "/api/auth/login/",
            {"identifier": self.registration_payload["email"], "password": self.registration_payload["password"], "role": "Doctor"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_requires_csrf(self):
        self.register_patient()
        response = self.post_json(
            "/api/auth/login/",
            {"identifier": self.registration_payload["email"], "password": self.registration_payload["password"], "role": "Patient"},
            csrf=False,
        )
        self.assertEqual(response.status_code, 403)

    def test_logout_invalidates_session_and_current_user_rejects(self):
        self.register_patient()
        self.post_json(
            "/api/auth/login/",
            {"identifier": self.registration_payload["email"], "password": self.registration_payload["password"], "role": "Patient"},
        )
        response = self.post_json("/api/auth/logout/", {})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 403)

    def test_unauthenticated_current_user_rejects(self):
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 403)

    def test_role_permissions_are_backend_enforced(self):
        patient = User.objects.create_user(
            email="permission.patient@example.test",
            password="A-strong-test-password-123",
            first_name="Permission",
            last_name="Patient",
            role=User.Role.PATIENT,
        )
        doctor = User.objects.create_user(
            email="permission.doctor@example.test",
            password="A-strong-test-password-123",
            first_name="Permission",
            last_name="Doctor",
            role=User.Role.DOCTOR,
        )
        factory = APIRequestFactory()
        patient_request = factory.get("/api/future-patient-endpoint/")
        doctor_request = factory.get("/api/future-doctor-endpoint/")
        patient_request.user = patient
        doctor_request.user = doctor
        self.assertTrue(IsPatient().has_permission(patient_request, None))
        self.assertFalse(IsDoctor().has_permission(patient_request, None))
        self.assertTrue(IsDoctor().has_permission(doctor_request, None))
        self.assertFalse(IsPatient().has_permission(doctor_request, None))
