import json
from datetime import date, time

from django.test import Client, TestCase

from apps.accounts.models import DoctorProfile, PatientProfile, User
from apps.appointments.models import Appointment
from apps.medical_records.models import MedicalRecord
from apps.prescriptions.models import Prescription, PrescriptionItem
from apps.reports.models import MedicalReport, ReportFinding


class ClinicalApiTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.patient_user = User.objects.create_user(
            email="clinical.patient.one@example.test",
            password="A-strong-test-password-123",
            first_name="Patient",
            last_name="One",
            role=User.Role.PATIENT,
        )
        self.patient = PatientProfile.objects.create(user=self.patient_user)
        self.other_patient_user = User.objects.create_user(
            email="clinical.patient.two@example.test",
            password="A-strong-test-password-123",
            first_name="Patient",
            last_name="Two",
            role=User.Role.PATIENT,
        )
        self.other_patient = PatientProfile.objects.create(user=self.other_patient_user)
        self.doctor_user = User.objects.create_user(
            email="clinical.doctor.one@example.test",
            password="A-strong-test-password-123",
            first_name="Doctor",
            last_name="One",
            role=User.Role.DOCTOR,
        )
        self.doctor = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization="Cardiology",
            license_id="LIC-CLINICAL-001",
        )
        self.other_doctor_user = User.objects.create_user(
            email="clinical.doctor.two@example.test",
            password="A-strong-test-password-123",
            first_name="Doctor",
            last_name="Two",
            role=User.Role.DOCTOR,
        )
        self.other_doctor = DoctorProfile.objects.create(
            user=self.other_doctor_user,
            specialization="Dermatology",
            license_id="LIC-CLINICAL-002",
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            scheduled_date=date(2030, 1, 10),
            scheduled_time=time(9, 30),
            status=Appointment.Status.CONFIRMED,
            reason="Clinical API test",
        )
        self.other_appointment = Appointment.objects.create(
            patient=self.other_patient,
            doctor=self.other_doctor,
            scheduled_date=date(2030, 1, 11),
            scheduled_time=time(9, 30),
            status=Appointment.Status.CONFIRMED,
            reason="Other clinical API test",
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

    def test_unauthenticated_and_wrong_roles_are_rejected(self):
        for path in (
            "/api/patient/medical-records/",
            "/api/patient/prescriptions/",
            "/api/patient/reports/",
            "/api/doctor/medical-records/",
            "/api/doctor/prescriptions/",
            "/api/doctor/reports/",
        ):
            self.assertEqual(self.client.get(path).status_code, 403)

        self.login_as(self.patient_user)
        for path in ("/api/doctor/medical-records/", "/api/doctor/prescriptions/", "/api/doctor/reports/"):
            self.assertEqual(self.client.get(path).status_code, 403)

        self.login_as(self.doctor_user)
        for path in ("/api/patient/medical-records/", "/api/patient/prescriptions/", "/api/patient/reports/"):
            self.assertEqual(self.client.get(path).status_code, 403)

    def test_patient_lists_are_owned_and_ignore_supplied_patient_id(self):
        record = MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment=self.appointment,
            record_type=MedicalRecord.RecordType.LAB_TEST,
            occurred_on=date(2030, 1, 10),
            diagnosis="CBC",
            notes="Normal",
        )
        other_record = MedicalRecord.objects.create(
            patient=self.other_patient,
            doctor=self.other_doctor,
            appointment=self.other_appointment,
            record_type=MedicalRecord.RecordType.IMAGING,
            occurred_on=date(2030, 1, 11),
            diagnosis="X-ray",
        )
        prescription = Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            issued_on=date(2030, 1, 10),
            start_date=date(2030, 1, 10),
        )
        PrescriptionItem.objects.create(
            prescription=prescription,
            medicine="Test Medicine",
            dosage="5mg",
            frequency="Once daily",
        )
        other_prescription = Prescription.objects.create(
            patient=self.other_patient,
            doctor=self.other_doctor,
            issued_on=date(2030, 1, 11),
            start_date=date(2030, 1, 11),
        )
        report = MedicalReport.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment=self.appointment,
            title="CBC Report",
            report_type=MedicalReport.ReportType.BLOOD_TEST,
            laboratory_name="Test Lab",
            report_date=date(2030, 1, 10),
            status=MedicalReport.Status.NORMAL,
            summary="Within range",
        )
        ReportFinding.objects.create(report=report, label="WBC", value="7.2")
        other_report = MedicalReport.objects.create(
            patient=self.other_patient,
            doctor=self.other_doctor,
            appointment=self.other_appointment,
            title="Other Report",
            report_type=MedicalReport.ReportType.IMAGING,
            report_date=date(2030, 1, 11),
        )

        self.login_as(self.patient_user)
        records = self.client.get(f"/api/patient/medical-records/?patient_id={self.other_patient.pk}").json()
        prescriptions = self.client.get(f"/api/patient/prescriptions/?patient_id={self.other_patient.pk}").json()
        reports = self.client.get(f"/api/patient/reports/?patient_id={self.other_patient.pk}").json()
        self.assertEqual({item["id"] for item in records}, {record.pk})
        self.assertNotIn(other_record.pk, {item["id"] for item in records})
        self.assertEqual({item["id"] for item in prescriptions}, {prescription.pk})
        self.assertNotIn(other_prescription.pk, {item["id"] for item in prescriptions})
        self.assertEqual({item["id"] for item in reports}, {report.pk})
        self.assertNotIn(other_report.pk, {item["id"] for item in reports})
        self.assertEqual(reports[0]["findings"][0]["label"], "WBC")

    def test_patient_clinical_endpoints_are_read_only_and_have_no_delete(self):
        self.login_as(self.patient_user)
        self.assertEqual(self.post_json("/api/patient/medical-records/", {}).status_code, 405)
        self.assertEqual(self.post_json("/api/patient/prescriptions/", {}).status_code, 405)
        self.assertEqual(self.post_json("/api/patient/reports/", {}).status_code, 405)
        self.assertEqual(
            self.client.delete(
                "/api/patient/medical-records/",
                HTTP_X_CSRFTOKEN=self.csrf_token(),
            ).status_code,
            405,
        )

    def test_doctor_list_is_limited_to_own_or_appointment_authorized_patients(self):
        own_record = MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            record_type=MedicalRecord.RecordType.CONSULTATION,
            occurred_on=date(2030, 1, 10),
            diagnosis="Follow-up",
        )
        authorized_other_doctor_record = MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.other_doctor,
            record_type=MedicalRecord.RecordType.OTHER,
            occurred_on=date(2030, 1, 9),
            diagnosis="Authorized patient history",
        )
        unauthorized_record = MedicalRecord.objects.create(
            patient=self.other_patient,
            doctor=self.other_doctor,
            record_type=MedicalRecord.RecordType.IMAGING,
            occurred_on=date(2030, 1, 11),
            diagnosis="Private history",
        )
        self.login_as(self.doctor_user)
        response = self.client.get("/api/doctor/medical-records/")
        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.json()}
        self.assertEqual(ids, {own_record.pk, authorized_other_doctor_record.pk})
        self.assertNotIn(unauthorized_record.pk, ids)

    def test_doctor_cannot_create_for_patient_without_appointment(self):
        self.login_as(self.doctor_user)
        response = self.post_json(
            "/api/doctor/medical-records/",
            {
                "patient_id": self.other_patient.pk,
                "record_type": "consultation",
                "occurred_on": "2030-01-11",
                "diagnosis": "Unauthorized",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(MedicalRecord.objects.filter(diagnosis="Unauthorized").exists())

    def test_doctor_record_creation_derives_doctor_and_validates_appointment(self):
        self.login_as(self.doctor_user)
        response = self.post_json(
            "/api/doctor/medical-records/",
            {
                "patient_id": self.patient.pk,
                "doctor_id": self.other_doctor.pk,
                "appointment_id": self.appointment.pk,
                "record_type": "consultation",
                "occurred_on": "2030-01-10",
                "diagnosis": "Follow-up",
                "notes": "Stable",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(MedicalRecord.objects.filter(diagnosis="Follow-up").exists())

        response = self.post_json(
            "/api/doctor/medical-records/",
            {
                "patient_id": self.patient.pk,
                "appointment_id": self.appointment.pk,
                "record_type": "consultation",
                "occurred_on": "2030-01-10",
                "diagnosis": "Follow-up",
                "notes": "Stable",
            },
        )
        self.assertEqual(response.status_code, 201)
        record = MedicalRecord.objects.get(diagnosis="Follow-up")
        self.assertEqual(record.doctor, self.doctor)
        self.assertEqual(record.patient, self.patient)
        self.assertEqual(response.json()["doctor_name"], "Doctor One")

    def test_doctor_prescription_creation_persists_nested_items(self):
        self.login_as(self.doctor_user)
        response = self.post_json(
            "/api/doctor/prescriptions/",
            {
                "patient_id": self.patient.pk,
                "status": "active",
                "issued_on": "2030-01-10",
                "start_date": "2030-01-10",
                "end_date": "2030-02-10",
                "items": [
                    {
                        "medicine": "Amlodipine",
                        "dosage": "5mg",
                        "frequency": "Once daily",
                        "duration": "1 month",
                        "instructions": "Take with water",
                        "side_effects": "Dizziness",
                    }
                ],
            },
        )
        self.assertEqual(response.status_code, 201)
        prescription = Prescription.objects.get()
        self.assertEqual(prescription.patient, self.patient)
        self.assertEqual(prescription.doctor, self.doctor)
        self.assertEqual(prescription.items.count(), 1)
        self.assertEqual(response.json()["items"][0]["medicine"], "Amlodipine")

    def test_doctor_report_creation_persists_nested_findings_and_references(self):
        record = MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment=self.appointment,
            record_type=MedicalRecord.RecordType.LAB_TEST,
            occurred_on=date(2030, 1, 10),
            diagnosis="CBC",
        )
        self.login_as(self.doctor_user)
        response = self.post_json(
            "/api/doctor/reports/",
            {
                "patient_id": self.patient.pk,
                "appointment_id": self.appointment.pk,
                "medical_record_id": record.pk,
                "title": "CBC Report",
                "report_type": "blood_test",
                "laboratory_name": "Test Lab",
                "report_date": "2030-01-10",
                "status": "normal",
                "summary": "Within range",
                "interpretation": "No concern",
                "findings": [
                    {"label": "WBC", "value": "7.2 K/uL", "is_normal": True, "sort_order": 1},
                    {"label": "Hemoglobin", "value": "14.2 g/dL", "is_normal": True, "sort_order": 2},
                ],
            },
        )
        self.assertEqual(response.status_code, 201)
        report = MedicalReport.objects.get()
        self.assertEqual(report.doctor, self.doctor)
        self.assertEqual(report.patient, self.patient)
        self.assertEqual(report.medical_record, record)
        self.assertEqual(report.findings.count(), 2)
        self.assertEqual(response.json()["findings"][0]["label"], "WBC")

    def test_doctor_nested_reference_must_match_authorized_patient(self):
        other_record = MedicalRecord.objects.create(
            patient=self.other_patient,
            doctor=self.other_doctor,
            record_type=MedicalRecord.RecordType.LAB_TEST,
            occurred_on=date(2030, 1, 11),
            diagnosis="Other CBC",
        )
        self.login_as(self.doctor_user)
        response = self.post_json(
            "/api/doctor/reports/",
            {
                "patient_id": self.patient.pk,
                "medical_record_id": other_record.pk,
                "title": "Invalid Reference",
                "report_type": "blood_test",
                "report_date": "2030-01-10",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(MedicalReport.objects.filter(title="Invalid Reference").exists())

    def test_doctor_collection_endpoints_do_not_allow_delete(self):
        self.login_as(self.doctor_user)
        for path in (
            "/api/doctor/medical-records/",
            "/api/doctor/prescriptions/",
            "/api/doctor/reports/",
        ):
            response = self.client.delete(path, HTTP_X_CSRFTOKEN=self.csrf_token())
            self.assertEqual(response.status_code, 405)

    def test_invalid_clinical_payloads_and_sensitive_fields_are_rejected(self):
        self.login_as(self.doctor_user)
        invalid_prescription = self.post_json(
            "/api/doctor/prescriptions/",
            {
                "patient_id": self.patient.pk,
                "issued_on": "2030-01-10",
                "start_date": "2030-02-10",
                "end_date": "2030-01-10",
                "items": [],
            },
        )
        self.assertEqual(invalid_prescription.status_code, 400)

        protected_prescription = self.post_json(
            "/api/doctor/prescriptions/",
            {
                "patient_id": self.patient.pk,
                "doctor_id": self.other_doctor.pk,
                "issued_on": "2030-01-10",
                "start_date": "2030-01-10",
                "items": [
                    {"medicine": "Test", "dosage": "5mg", "frequency": "Once daily"},
                ],
            },
        )
        self.assertEqual(protected_prescription.status_code, 400)

        invalid_report = self.post_json(
            "/api/doctor/reports/",
            {
                "patient_id": self.patient.pk,
                "title": "Invalid Report",
                "report_type": "not-a-report-type",
                "report_date": "2030-01-10",
            },
        )
        self.assertEqual(invalid_report.status_code, 400)

        protected_report = self.post_json(
            "/api/doctor/reports/",
            {
                "patient_id": self.patient.pk,
                "doctor_id": self.other_doctor.pk,
                "title": "Protected Report",
                "report_type": "blood_test",
                "report_date": "2030-01-10",
            },
        )
        self.assertEqual(protected_report.status_code, 400)

        self.login_as(self.patient_user)
        records_response = self.client.get("/api/patient/medical-records/")
        self.assertEqual(records_response.status_code, 200)
        self.assertNotIn("password", records_response.content.decode("utf-8"))
        self.assertNotIn("password_hash", records_response.content.decode("utf-8"))
