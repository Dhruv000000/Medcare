import json
from datetime import date, time

from django.test import Client, TestCase

from apps.accounts.models import DoctorProfile, PatientPreferences, PatientProfile, User
from apps.appointments.models import Appointment
from apps.medical_records.models import MedicalRecord
from apps.prescriptions.models import Prescription


class PatientApiTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.patient_user = User.objects.create_user(
            email="patient.one@example.test",
            password="A-strong-test-password-123",
            first_name="Patient",
            last_name="One",
            phone="9876543210",
            date_of_birth=date(1990, 1, 1),
            gender="Other",
            role=User.Role.PATIENT,
        )
        self.patient = PatientProfile.objects.create(
            user=self.patient_user,
            blood_group=PatientProfile.BloodGroup.O_POSITIVE,
            address="Test address",
        )
        PatientPreferences.objects.create(patient=self.patient)

        self.other_user = User.objects.create_user(
            email="patient.two@example.test",
            password="A-strong-test-password-123",
            first_name="Patient",
            last_name="Two",
            phone="9876543211",
            role=User.Role.PATIENT,
        )
        self.other_patient = PatientProfile.objects.create(user=self.other_user)
        PatientPreferences.objects.create(patient=self.other_patient)

        self.doctor_user = User.objects.create_user(
            email="doctor@example.test",
            password="A-strong-test-password-123",
            first_name="Test",
            last_name="Doctor",
            role=User.Role.DOCTOR,
        )
        self.doctor = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization="General Medicine",
            license_id="LIC-PATIENT-TEST",
        )

    def csrf_token(self):
        return self.client.get("/api/auth/csrf/").json()["csrfToken"]

    def authenticate_as(self, user):
        self.client.force_login(user)

    def patch_json(self, path, payload):
        return self.client.patch(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=self.csrf_token(),
        )

    def test_authenticated_patient_retrieves_own_profile_only(self):
        self.authenticate_as(self.patient_user)
        response = self.client.get("/api/patient/profile/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["email"], self.patient_user.email)
        self.assertEqual(payload["blood_group"], "O+")
        self.assertEqual(payload["role"], "patient")
        self.assertNotIn("password", payload)
        self.assertNotIn("password_hash", payload)
        self.assertNotIn("user_id", payload)
        self.assertNotIn("patient_id", payload)

    def test_unauthenticated_user_cannot_access_patient_profile(self):
        response = self.client.get("/api/patient/profile/")
        self.assertEqual(response.status_code, 403)

    def test_doctor_cannot_access_patient_endpoints(self):
        self.authenticate_as(self.doctor_user)
        for path in ("/api/patient/profile/", "/api/patient/settings/", "/api/patient/dashboard/"):
            self.assertEqual(self.client.get(path).status_code, 403)

    def test_patient_id_parameter_cannot_select_another_patient(self):
        self.authenticate_as(self.patient_user)
        response = self.client.get(f"/api/patient/profile/?patient_id={self.other_patient.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], self.patient_user.email)
        self.assertNotEqual(response.json()["email"], self.other_user.email)

    def test_patient_can_update_permitted_profile_fields(self):
        self.authenticate_as(self.patient_user)
        response = self.patch_json(
            "/api/patient/profile/",
            {
                "first_name": "Updated",
                "last_name": "Patient",
                "phone": "9876543212",
                "blood_group": "A+",
                "address": "Updated test address",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.patient_user.refresh_from_db()
        self.patient.refresh_from_db()
        self.assertEqual(self.patient_user.first_name, "Updated")
        self.assertEqual(self.patient_user.phone, "9876543212")
        self.assertEqual(self.patient.blood_group, "A+")
        self.assertEqual(self.patient.address, "Updated test address")

    def test_protected_profile_fields_cannot_be_modified(self):
        self.authenticate_as(self.patient_user)
        response = self.patch_json(
            "/api/patient/profile/",
            {"role": "doctor", "user_id": self.other_user.pk, "patient_id": self.other_patient.pk},
        )
        self.assertEqual(response.status_code, 400)
        self.patient_user.refresh_from_db()
        self.assertEqual(self.patient_user.role, User.Role.PATIENT)
        self.assertEqual(self.patient_user.email, "patient.one@example.test")

    def test_invalid_profile_data_is_rejected(self):
        self.authenticate_as(self.patient_user)
        response = self.patch_json("/api/patient/profile/", {"phone": "not-a-phone"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone", response.json())

    def test_missing_patient_relationship_is_handled_safely(self):
        user = User.objects.create_user(
            email="orphan.patient@example.test",
            password="A-strong-test-password-123",
            first_name="Orphan",
            last_name="Patient",
            role=User.Role.PATIENT,
        )
        self.authenticate_as(user)
        for path in ("/api/patient/profile/", "/api/patient/settings/", "/api/patient/dashboard/"):
            self.assertEqual(self.client.get(path).status_code, 403)

    def test_patient_settings_are_owned_and_writable_only_with_allowed_fields(self):
        self.authenticate_as(self.patient_user)
        response = self.patch_json(
            "/api/patient/settings/",
            {"health_tips": True, "notification_method": "both", "theme": "dark", "font_size": "large"},
        )
        self.assertEqual(response.status_code, 200)
        prefs = PatientPreferences.objects.get(patient=self.patient)
        self.assertTrue(prefs.health_tips)
        self.assertEqual(prefs.notification_method, "both")
        protected = self.patch_json("/api/patient/settings/", {"patient_id": self.other_patient.pk, "role": "doctor"})
        self.assertEqual(protected.status_code, 400)

    def test_dashboard_returns_only_authenticated_patient_counts(self):
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            scheduled_date=date(2030, 1, 1),
            scheduled_time=time(9, 30),
            status=Appointment.Status.PENDING,
            reason="Test appointment",
        )
        MedicalRecord.objects.create(
            patient=self.patient,
            record_type=MedicalRecord.RecordType.CONSULTATION,
            occurred_on=date(2029, 1, 1),
            diagnosis="Test record",
        )
        prescription = Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            status=Prescription.Status.ACTIVE,
            issued_on=date(2029, 1, 1),
            start_date=date(2029, 1, 1),
        )
        self.assertIsNotNone(prescription)
        Appointment.objects.create(
            patient=self.other_patient,
            doctor=self.doctor,
            scheduled_date=date(2030, 1, 2),
            scheduled_time=time(9, 30),
            status=Appointment.Status.PENDING,
        )
        self.authenticate_as(self.patient_user)
        response = self.client.get("/api/patient/dashboard/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(
            {
                "upcoming_appointment_count": payload["upcoming_appointment_count"],
                "medical_record_count": payload["medical_record_count"],
                "active_prescription_count": payload["active_prescription_count"],
            },
            {
                "upcoming_appointment_count": 1,
                "medical_record_count": 1,
                "active_prescription_count": 1,
            },
        )
        self.assertEqual(
            [item["activity_type"] for item in payload["recent_activity"]],
            ["appointment", "medical_record", "prescription"],
        )

    def test_health_endpoint_still_works(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "service": "MediCare API"})
