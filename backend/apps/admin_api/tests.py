import json
from datetime import date, time
from pathlib import Path

from django.test import Client, TestCase

from apps.accounts.models import DoctorProfile, PatientProfile, User
from apps.appointments.models import Appointment


class AdminApiTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.admin_user = User.objects.create_user(
            email="admin.phase14@example.test",
            password="A-strong-test-password-123",
            first_name="System",
            last_name="Admin",
            phone="9000000001",
            role=User.Role.ADMINISTRATOR,
        )
        self.patient_user = User.objects.create_user(
            email="patient.phase14@example.test",
            password="A-strong-test-password-123",
            first_name="Asha",
            last_name="Patient",
            phone="9000000002",
            role=User.Role.PATIENT,
        )
        self.patient = PatientProfile.objects.create(user=self.patient_user)
        self.doctor_user = User.objects.create_user(
            email="doctor.phase14@example.test",
            password="A-strong-test-password-123",
            first_name="Dev",
            last_name="Doctor",
            phone="9000000003",
            role=User.Role.DOCTOR,
        )
        self.doctor = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization="Cardiology",
            license_id="LIC-PHASE14-001",
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            scheduled_date=date(2031, 3, 10),
            scheduled_time=time(9, 30),
            status=Appointment.Status.PENDING,
            reason="Administrative test appointment",
        )

    def csrf_token(self):
        return self.client.get("/api/auth/csrf/").json()["csrfToken"]

    def login_as(self, user):
        self.client.force_login(user)

    def patch_json(self, path, payload):
        return self.client.patch(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=self.csrf_token(),
        )

    def test_unauthenticated_and_wrong_roles_are_denied(self):
        self.assertEqual(self.client.get("/api/admin/dashboard/").status_code, 403)
        self.login_as(self.patient_user)
        self.assertEqual(self.client.get("/api/admin/dashboard/").status_code, 403)
        self.assertEqual(self.client.get("/api/admin/patients/").status_code, 403)
        self.login_as(self.doctor_user)
        self.assertEqual(self.client.get("/api/admin/doctors/").status_code, 403)
        self.assertEqual(self.client.get("/api/admin/appointments/").status_code, 403)

    def test_admin_can_access_dashboard_with_real_statistics(self):
        self.login_as(self.admin_user)
        response = self.client.get("/api/admin/dashboard/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total_patients"], 1)
        self.assertEqual(payload["total_doctors"], 1)
        self.assertEqual(payload["total_appointments"], 1)
        self.assertEqual(payload["pending_appointments"], 1)
        self.assertEqual(payload["completed_appointments"], 0)
        self.assertEqual(payload["cancelled_appointments"], 0)
        self.assertEqual(payload["recent_appointments"][0]["id"], self.appointment.pk)
        self.assertNotIn("password", json.dumps(payload).lower())
        self.assertNotIn("session", json.dumps(payload).lower())

    def test_empty_database_dashboard_returns_zero_counts(self):
        Appointment.objects.all().delete()
        PatientProfile.objects.all().delete()
        DoctorProfile.objects.all().delete()
        User.objects.exclude(pk=self.admin_user.pk).delete()
        self.login_as(self.admin_user)
        payload = self.client.get("/api/admin/dashboard/").json()
        self.assertEqual(payload["total_patients"], 0)
        self.assertEqual(payload["total_doctors"], 0)
        self.assertEqual(payload["total_appointments"], 0)
        self.assertEqual(payload["recent_appointments"], [])

    def test_patient_list_search_and_detail(self):
        self.login_as(self.admin_user)
        response = self.client.get("/api/admin/patients/?q=asha")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        item = response.json()[0]
        self.assertEqual(item["user_id"], self.patient_user.pk)
        self.assertNotIn("password", json.dumps(item).lower())
        detail = self.client.get(f"/api/admin/patients/{self.patient.pk}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["email"], self.patient_user.email)
        self.assertEqual(self.client.get("/api/admin/patients/99999/").status_code, 404)

    def test_doctor_list_search_and_detail(self):
        self.login_as(self.admin_user)
        response = self.client.get("/api/admin/doctors/?q=cardiology")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        item = response.json()[0]
        self.assertEqual(item["user_id"], self.doctor_user.pk)
        self.assertEqual(item["license_id"], "LIC-PHASE14-001")
        self.assertNotIn("password", json.dumps(item).lower())
        detail = self.client.get(f"/api/admin/doctors/{self.doctor.pk}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["specialization"], "Cardiology")
        self.assertEqual(self.client.get("/api/admin/doctors/99999/").status_code, 404)

    def test_appointment_oversight_filters(self):
        self.login_as(self.admin_user)
        self.assertEqual(self.client.get("/api/admin/appointments/?status=pending").json()[0]["id"], self.appointment.pk)
        self.assertEqual(self.client.get(f"/api/admin/appointments/?patient_id={self.patient.pk}").status_code, 200)
        self.assertEqual(self.client.get(f"/api/admin/appointments/?doctor_id={self.doctor.pk}").status_code, 200)
        self.assertEqual(self.client.get("/api/admin/appointments/?status=invalid").status_code, 400)
        self.assertEqual(self.client.get("/api/admin/appointments/?patient_id=not-a-number").status_code, 400)
        payload = self.client.get("/api/admin/appointments/").json()[0]
        self.assertEqual(payload["patient_name"], "Asha Patient")
        self.assertEqual(payload["doctor_name"], "Dev Doctor")
        self.assertNotIn("password", json.dumps(payload).lower())

    def test_admin_profile_is_read_only_and_safe(self):
        self.login_as(self.admin_user)
        response = self.client.get("/api/admin/profile/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["role"], User.Role.ADMINISTRATOR)
        self.assertNotIn("password", json.dumps(payload).lower())
        self.assertNotIn("session", json.dumps(payload).lower())

    def test_status_change_requires_csrf_and_cannot_target_self_or_admin(self):
        self.login_as(self.admin_user)
        csrf_rejected = self.client.patch(
            f"/api/admin/users/{self.patient_user.pk}/status/",
            data=json.dumps({"is_active": False}),
            content_type="application/json",
        )
        self.assertEqual(csrf_rejected.status_code, 403)
        response = self.patch_json(f"/api/admin/users/{self.patient_user.pk}/status/", {"is_active": False})
        self.assertEqual(response.status_code, 200)
        self.patient_user.refresh_from_db()
        self.assertFalse(self.patient_user.is_active)
        self.assertEqual(self.patch_json(f"/api/admin/users/{self.admin_user.pk}/status/", {"is_active": False}).status_code, 400)
        self.assertEqual(self.patch_json(f"/api/admin/users/{self.doctor_user.pk}/status/", {"is_active": True}).status_code, 200)

    def test_admin_cannot_access_patient_or_doctor_scoped_apis(self):
        self.login_as(self.admin_user)
        self.assertEqual(self.client.get("/api/patient/dashboard/").status_code, 403)
        self.assertEqual(self.client.get("/api/doctor/dashboard/").status_code, 403)
        self.assertEqual(self.client.get("/api/patient/medical-records/").status_code, 403)

    def test_admin_frontend_files_and_navigation_exist(self):
        project_root = Path(__file__).resolve().parents[3]
        for filename in [
            "admin-dashboard.html", "admin-patients.html", "admin-doctors.html",
            "admin-appointments.html", "admin-profile.html",
        ]:
            content = (project_root / "frontend" / "pages" / "admin" / filename).read_text(encoding="utf-8")
            self.assertIn("../../js/auth/auth-client.js", content)
            self.assertIn("../../js/admin/admin.js", content)
            self.assertIn("admin-dashboard.html", content)
            self.assertIn("admin-patients.html", content)
            self.assertIn("admin-doctors.html", content)
            self.assertIn("admin-appointments.html", content)
            self.assertIn("admin-profile.html", content)

from django.test import override_settings


class AdminAuthenticationIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def test_admin_registration_uses_existing_server_side_code(self):
        with override_settings(ADMIN_REGISTRATION_CODE="phase14-test-code"):
            csrf = self.client.get("/api/auth/csrf/").json()["csrfToken"]
            response = self.client.post(
                "/api/auth/register/",
                data=json.dumps(
                    {
                        "first_name": "Registered",
                        "last_name": "Administrator",
                        "email": "registered.admin.phase14@example.test",
                        "phone": "9000000010",
                        "date_of_birth": "1990-01-01",
                        "gender": "Prefer not to say",
                        "role": "admin",
                        "admin_code": "phase14-test-code",
                        "password": "A-strong-test-password-123",
                        "confirm_password": "A-strong-test-password-123",
                    }
                ),
                content_type="application/json",
                HTTP_X_CSRFTOKEN=csrf,
            )
        self.assertEqual(response.status_code, 201)
        created = User.objects.get(email="registered.admin.phase14@example.test")
        self.assertEqual(created.role, User.Role.ADMINISTRATOR)
        self.assertFalse(hasattr(created, "patient_profile"))
        self.assertFalse(hasattr(created, "doctor_profile"))
        self.assertNotIn("password", json.dumps(response.json()).lower())
