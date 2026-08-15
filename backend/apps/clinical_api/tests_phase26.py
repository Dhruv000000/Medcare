import json
from datetime import date, time

from django.test import Client, TestCase

from apps.accounts.models import DoctorProfile, PatientProfile, User
from apps.appointments.models import Appointment
from apps.medical_records.models import MedicalRecord
from apps.prescriptions.models import Prescription, PrescriptionItem
from apps.reports.models import MedicalReport, ReportFinding


class Phase26ClinicalWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.patient_user = User.objects.create_user(
            email="phase26.patient@example.test",
            password="Phase26-Strong-Password-123!",
            first_name="Phase26",
            last_name="Patient",
            role=User.Role.PATIENT,
        )
        self.patient = PatientProfile.objects.create(user=self.patient_user)
        self.other_patient_user = User.objects.create_user(
            email="phase26.other.patient@example.test",
            password="Phase26-Strong-Password-123!",
            first_name="Phase26 Other",
            last_name="Patient",
            role=User.Role.PATIENT,
        )
        self.other_patient = PatientProfile.objects.create(user=self.other_patient_user)
        self.doctor_user = User.objects.create_user(
            email="phase26.doctor@example.test",
            password="Phase26-Strong-Password-123!",
            first_name="Phase26",
            last_name="Doctor",
            role=User.Role.DOCTOR,
        )
        self.doctor = DoctorProfile.objects.create(user=self.doctor_user, specialization="Cardiology", license_id="PH26-LIC-001")
        self.other_doctor_user = User.objects.create_user(
            email="phase26.other.doctor@example.test",
            password="Phase26-Strong-Password-123!",
            first_name="Phase26 Other",
            last_name="Doctor",
            role=User.Role.DOCTOR,
        )
        self.other_doctor = DoctorProfile.objects.create(user=self.other_doctor_user, specialization="Dermatology", license_id="PH26-LIC-002")
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            scheduled_date=date(2030, 1, 10),
            scheduled_time=time(9, 30),
            status=Appointment.Status.CONFIRMED,
            reason="Phase 26 clinical workflow",
        )
        self.other_appointment = Appointment.objects.create(
            patient=self.other_patient,
            doctor=self.other_doctor,
            scheduled_date=date(2030, 1, 11),
            scheduled_time=time(10, 30),
            status=Appointment.Status.CONFIRMED,
            reason="Other workflow",
        )

    def csrf_token(self):
        return self.client.get("/api/auth/csrf/").json()["csrfToken"]

    def login(self, user):
        self.client.force_login(user)

    def post_json(self, path, payload):
        return self.client.post(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=self.csrf_token(),
        )

    def test_authorized_doctor_can_create_record_with_appointment_link(self):
        self.login(self.doctor_user)
        response = self.post_json(
            "/api/doctor/medical-records/",
            {
                "patient_id": self.patient.pk,
                "appointment_id": self.appointment.pk,
                "record_type": "consultation",
                "occurred_on": "2030-01-10",
                "diagnosis": "Workflow consultation",
                "notes": "Created through the authorized workflow.",
            },
        )
        self.assertEqual(response.status_code, 201)
        record = MedicalRecord.objects.get(pk=response.json()["id"])
        self.assertEqual(record.patient_id, self.patient.pk)
        self.assertEqual(record.doctor_id, self.doctor.pk)
        self.assertEqual(record.appointment_id, self.appointment.pk)

    def test_authorized_doctor_can_create_report_with_finding_and_record_link(self):
        record = MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment=self.appointment,
            record_type=MedicalRecord.RecordType.LAB_TEST,
            occurred_on=date(2030, 1, 10),
            diagnosis="CBC",
        )
        self.login(self.doctor_user)
        response = self.post_json(
            "/api/doctor/reports/",
            {
                "patient_id": self.patient.pk,
                "appointment_id": self.appointment.pk,
                "medical_record_id": record.pk,
                "title": "Workflow blood report",
                "report_type": "blood_test",
                "report_date": "2030-01-10",
                "status": "normal",
                "summary": "Within expected range.",
                "findings": [{"label": "WBC", "value": "7.2", "is_normal": True, "sort_order": 0}],
            },
        )
        self.assertEqual(response.status_code, 201)
        report = MedicalReport.objects.get(pk=response.json()["id"])
        self.assertEqual(report.doctor_id, self.doctor.pk)
        self.assertEqual(report.appointment_id, self.appointment.pk)
        self.assertEqual(report.medical_record_id, record.pk)
        self.assertEqual(ReportFinding.objects.filter(report=report).count(), 1)

    def test_authorized_doctor_can_create_prescription_with_nested_item(self):
        self.login(self.doctor_user)
        response = self.post_json(
            "/api/doctor/prescriptions/",
            {
                "patient_id": self.patient.pk,
                "status": "active",
                "issued_on": "2030-01-10",
                "start_date": "2030-01-10",
                "items": [{"medicine": "Example medicine", "dosage": "5 mg", "frequency": "Once daily", "duration": "7 days"}],
            },
        )
        self.assertEqual(response.status_code, 201)
        prescription = Prescription.objects.get(pk=response.json()["id"])
        self.assertEqual(prescription.doctor_id, self.doctor.pk)
        self.assertEqual(PrescriptionItem.objects.filter(prescription=prescription).count(), 1)

    def test_unrelated_doctor_cannot_create_for_patient(self):
        self.login(self.other_doctor_user)
        response = self.post_json(
            "/api/doctor/medical-records/",
            {
                "patient_id": self.patient.pk,
                "record_type": "consultation",
                "occurred_on": "2030-01-10",
                "diagnosis": "Unauthorized attempt",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(MedicalRecord.objects.filter(diagnosis="Unauthorized attempt").count(), 0)

    def test_patient_cannot_submit_clinical_workflow_writes(self):
        self.login(self.patient_user)
        for path in ("/api/patient/medical-records/", "/api/patient/reports/", "/api/patient/prescriptions/"):
            self.assertEqual(self.post_json(path, {}).status_code, 405)

    def test_doctor_appointment_payload_exposes_read_only_patient_link(self):
        self.login(self.doctor_user)
        response = self.client.get("/api/doctor/appointments/")
        self.assertEqual(response.status_code, 200)
        appointment = next(item for item in response.json() if item["id"] == self.appointment.pk)
        self.assertEqual(appointment["patient_id"], self.patient.pk)
