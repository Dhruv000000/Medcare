import json
from datetime import date, time

from django.test import Client, TestCase

from apps.accounts.models import DoctorProfile, PatientProfile, User
from apps.appointments.models import Appointment


class AppointmentApiTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.patient_user = User.objects.create_user(
            email="appointment.patient.one@example.test",
            password="A-strong-test-password-123",
            first_name="Patient",
            last_name="One",
            phone="9876543210",
            role=User.Role.PATIENT,
        )
        self.patient = PatientProfile.objects.create(user=self.patient_user)
        self.other_patient_user = User.objects.create_user(
            email="appointment.patient.two@example.test",
            password="A-strong-test-password-123",
            first_name="Patient",
            last_name="Two",
            phone="9876543211",
            role=User.Role.PATIENT,
        )
        self.other_patient = PatientProfile.objects.create(user=self.other_patient_user)
        self.doctor_user = User.objects.create_user(
            email="appointment.doctor.one@example.test",
            password="A-strong-test-password-123",
            first_name="Doctor",
            last_name="One",
            role=User.Role.DOCTOR,
        )
        self.doctor = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization="Cardiology",
            license_id="LIC-APPOINTMENT-001",
        )
        self.other_doctor_user = User.objects.create_user(
            email="appointment.doctor.two@example.test",
            password="A-strong-test-password-123",
            first_name="Doctor",
            last_name="Two",
            role=User.Role.DOCTOR,
        )
        self.other_doctor = DoctorProfile.objects.create(
            user=self.other_doctor_user,
            specialization="Dermatology",
            license_id="LIC-APPOINTMENT-002",
        )

    def csrf_token(self):
        return self.client.get("/api/auth/csrf/").json()["csrfToken"]

    def login_as(self, user):
        self.client.force_login(user)

    def post_json(self, path, payload):
        return self.client.post(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=self.csrf_token(),
        )

    def create_appointment(self, patient=None, doctor=None, scheduled_date=date(2030, 1, 10), scheduled_time=time(9, 30), status=Appointment.Status.PENDING):
        return Appointment.objects.create(
            patient=patient or self.patient,
            doctor=doctor or self.doctor,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            status=status,
            reason="Test appointment",
        )

    def test_doctor_can_access_own_profile_and_dashboard(self):
        self.login_as(self.doctor_user)
        profile = self.client.get("/api/doctor/profile/")
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.json()["email"], self.doctor_user.email)
        self.assertEqual(profile.json()["specialization"], "Cardiology")
        self.assertNotIn("password", profile.json())
        dashboard = self.client.get("/api/doctor/dashboard/")
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.json()["doctor"]["license_id"], "LIC-APPOINTMENT-001")

    def test_unauthenticated_and_patient_cannot_access_doctor_apis(self):
        self.assertEqual(self.client.get("/api/doctor/profile/").status_code, 403)
        self.login_as(self.patient_user)
        self.assertEqual(self.client.get("/api/doctor/profile/").status_code, 403)
        self.assertEqual(self.client.get("/api/doctor/dashboard/").status_code, 403)
        self.assertEqual(self.client.get("/api/doctor/appointments/").status_code, 403)

    def test_doctor_appointment_list_is_scoped_to_authenticated_doctor(self):
        owned = self.create_appointment()
        other = self.create_appointment(doctor=self.other_doctor, scheduled_time=time(10, 30))
        self.login_as(self.doctor_user)
        response = self.client.get("/api/doctor/appointments/")
        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.json()}
        self.assertEqual(ids, {owned.pk})
        self.assertNotIn(other.pk, ids)

    def test_patient_can_create_appointment_with_server_derived_owner(self):
        self.login_as(self.patient_user)
        response = self.post_json(
            "/api/patient/appointments/",
            {
                "doctor_id": self.doctor.pk,
                "scheduled_date": "2030-02-01",
                "scheduled_time": "09:30",
                "reason": "Follow-up",
                "patient_id": self.other_patient.pk,
                "status": "completed",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Appointment.objects.exists())

        response = self.post_json(
            "/api/patient/appointments/",
            {
                "doctor_id": self.doctor.pk,
                "scheduled_date": "2030-02-01",
                "scheduled_time": "09:30",
                "reason": "Follow-up",
            },
        )
        self.assertEqual(response.status_code, 201)
        appointment = Appointment.objects.get()
        self.assertEqual(appointment.patient, self.patient)
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(appointment.status, Appointment.Status.PENDING)

    def test_patient_appointment_list_and_detail_are_scoped(self):
        owned = self.create_appointment()
        other = self.create_appointment(patient=self.other_patient, scheduled_time=time(10, 30))
        self.login_as(self.patient_user)
        response = self.client.get("/api/patient/appointments/")
        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.json()}
        self.assertEqual(ids, {owned.pk})
        self.assertEqual(self.client.get(f"/api/patient/appointments/{owned.pk}/").status_code, 200)
        self.assertEqual(self.client.get(f"/api/patient/appointments/{other.pk}/").status_code, 404)

    def test_patient_filters_and_can_cancel_own_pending_or_confirmed_appointment(self):
        pending = self.create_appointment()
        completed = self.create_appointment(scheduled_time=time(10, 30), status=Appointment.Status.COMPLETED)
        self.login_as(self.patient_user)
        response = self.client.get("/api/patient/appointments/?status=pending")
        self.assertEqual(response.status_code, 200)
        self.assertEqual({item["id"] for item in response.json()}, {pending.pk})
        cancelled = self.post_json(f"/api/patient/appointments/{pending.pk}/cancel/", {})
        self.assertEqual(cancelled.status_code, 200)
        pending.refresh_from_db()
        self.assertEqual(pending.status, Appointment.Status.CANCELLED)
        cannot_cancel = self.post_json(f"/api/patient/appointments/{completed.pk}/cancel/", {})
        self.assertEqual(cannot_cancel.status_code, 400)

    def test_doctor_can_confirm_reject_and_complete_only_valid_transitions(self):
        pending = self.create_appointment()
        self.login_as(self.doctor_user)
        confirmed = self.post_json(
            f"/api/doctor/appointments/{pending.pk}/transition/",
            {"action": "confirm", "status": "completed", "doctor_id": self.other_doctor.pk},
        )
        self.assertEqual(confirmed.status_code, 400)
        pending.refresh_from_db()
        self.assertEqual(pending.status, Appointment.Status.PENDING)

        confirmed = self.post_json(f"/api/doctor/appointments/{pending.pk}/transition/", {"action": "confirm"})
        self.assertEqual(confirmed.status_code, 200)
        pending.refresh_from_db()
        self.assertEqual(pending.status, Appointment.Status.CONFIRMED)

        completed = self.post_json(f"/api/doctor/appointments/{pending.pk}/transition/", {"action": "complete"})
        self.assertEqual(completed.status_code, 200)
        pending.refresh_from_db()
        self.assertEqual(pending.status, Appointment.Status.COMPLETED)

        invalid = self.post_json(f"/api/doctor/appointments/{pending.pk}/transition/", {"action": "cancel"})
        self.assertEqual(invalid.status_code, 400)

    def test_doctor_can_reject_pending_and_other_doctor_cannot_modify_it(self):
        pending = self.create_appointment()
        self.login_as(self.other_doctor_user)
        self.assertEqual(self.client.get(f"/api/doctor/appointments/{pending.pk}/").status_code, 404)
        self.assertEqual(
            self.post_json(f"/api/doctor/appointments/{pending.pk}/transition/", {"action": "reject"}).status_code,
            404,
        )
        self.login_as(self.doctor_user)
        response = self.post_json(f"/api/doctor/appointments/{pending.pk}/transition/", {"action": "reject"})
        self.assertEqual(response.status_code, 200)
        pending.refresh_from_db()
        self.assertEqual(pending.status, Appointment.Status.REJECTED)

    def test_past_date_is_rejected(self):
        self.login_as(self.patient_user)
        response = self.post_json(
            "/api/patient/appointments/",
            {"doctor_id": self.doctor.pk, "scheduled_date": "2020-01-01", "scheduled_time": "09:30"},
        )
        self.assertEqual(response.status_code, 400)

    def test_doctor_and_patient_double_booking_is_rejected(self):
        self.create_appointment()
        self.login_as(self.patient_user)
        doctor_conflict = self.post_json(
            "/api/patient/appointments/",
            {"doctor_id": self.doctor.pk, "scheduled_date": "2030-01-10", "scheduled_time": "09:30"},
        )
        self.assertEqual(doctor_conflict.status_code, 409)
        patient_conflict = self.post_json(
            "/api/patient/appointments/",
            {"doctor_id": self.other_doctor.pk, "scheduled_date": "2030-01-10", "scheduled_time": "09:30"},
        )
        self.assertEqual(patient_conflict.status_code, 409)

    def test_patient_doctor_directory_is_authenticated_and_limited(self):
        self.assertEqual(self.client.get("/api/patient/doctors/").status_code, 403)
        self.login_as(self.patient_user)
        response = self.client.get("/api/patient/doctors/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"id": self.doctor.pk, "name": "Dr. Doctor One", "specialization": "Cardiology"}, {"id": self.other_doctor.pk, "name": "Dr. Doctor Two", "specialization": "Dermatology"}])

    def test_health_endpoint_still_works(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "service": "MediCare API"})

    def test_doctor_dashboard_contains_authorized_patient_summary(self):
        appointment = self.create_appointment()
        self.login_as(self.doctor_user)
        response = self.client.get("/api/doctor/dashboard/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["patient_count"], 1)
        self.assertEqual(payload["authorized_patients"][0]["patient_id"], appointment.patient_id)
        self.assertEqual(payload["authorized_patients"][0]["patient_name"], "Patient One")
        self.assertNotIn("password", response.content.decode("utf-8"))
