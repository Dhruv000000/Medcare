import io
import tempfile
from datetime import date, time
from pathlib import Path

from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.accounts.models import DoctorProfile, PatientProfile, User
from apps.appointments.models import Appointment
from apps.medical_records.models import MedicalRecord
from apps.reports.models import MedicalReport


class Phase24FileSecurityTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.media_dir = tempfile.TemporaryDirectory()
        self.media_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)
        self.addCleanup(self.media_dir.cleanup)

        self.patient_user = User.objects.create_user(
            email="phase24.patient.one@example.test",
            password="Phase24-Password-123!",
            first_name="Patient",
            last_name="One",
            role=User.Role.PATIENT,
        )
        self.patient = PatientProfile.objects.create(user=self.patient_user)
        self.other_patient_user = User.objects.create_user(
            email="phase24.patient.two@example.test",
            password="Phase24-Password-123!",
            first_name="Patient",
            last_name="Two",
            role=User.Role.PATIENT,
        )
        self.other_patient = PatientProfile.objects.create(user=self.other_patient_user)
        self.doctor_user = User.objects.create_user(
            email="phase24.doctor.one@example.test",
            password="Phase24-Password-123!",
            first_name="Doctor",
            last_name="One",
            role=User.Role.DOCTOR,
        )
        self.doctor = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization="Cardiology",
            license_id="PHASE24-001",
        )
        self.other_doctor_user = User.objects.create_user(
            email="phase24.doctor.two@example.test",
            password="Phase24-Password-123!",
            first_name="Doctor",
            last_name="Two",
            role=User.Role.DOCTOR,
        )
        self.other_doctor = DoctorProfile.objects.create(
            user=self.other_doctor_user,
            specialization="Dermatology",
            license_id="PHASE24-002",
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            scheduled_date=date(2030, 1, 10),
            scheduled_time=time(9, 30),
            status=Appointment.Status.CONFIRMED,
            reason="Phase 24 synthetic appointment",
        )
        self.other_appointment = Appointment.objects.create(
            patient=self.other_patient,
            doctor=self.other_doctor,
            scheduled_date=date(2030, 1, 11),
            scheduled_time=time(9, 30),
            status=Appointment.Status.CONFIRMED,
            reason="Phase 24 unrelated appointment",
        )

    def csrf_token(self):
        return self.client.get("/api/auth/csrf/").json()["csrfToken"]

    def login_as(self, user):
        self.client.force_login(user)

    def valid_pdf(self, name="lab report.pdf", content=b"%PDF-1.7\nsynthetic"):
        return SimpleUploadedFile(name, content, content_type="application/pdf")

    def create_record(self, patient=None, doctor=None, appointment=None, attachment=None):
        return MedicalRecord.objects.create(
            patient=patient or self.patient,
            doctor=doctor or self.doctor,
            appointment=appointment or self.appointment,
            record_type=MedicalRecord.RecordType.LAB_TEST,
            occurred_on=date(2030, 1, 10),
            diagnosis="Synthetic CBC",
            notes="Synthetic Phase 24 record",
            attachment=attachment,
            attachment_original_name="synthetic.pdf" if attachment else "",
            attachment_content_type="application/pdf" if attachment else "",
            attachment_size=len(b"%PDF-1.7\nsynthetic") if attachment else None,
        )

    def create_report(self, patient=None, doctor=None, appointment=None, attachment=None):
        return MedicalReport.objects.create(
            patient=patient or self.patient,
            doctor=doctor or self.doctor,
            appointment=appointment or self.appointment,
            title="Synthetic Report",
            report_type=MedicalReport.ReportType.BLOOD_TEST,
            report_date=date(2030, 1, 10),
            status=MedicalReport.Status.NORMAL,
            summary="Synthetic summary",
            attachment=attachment,
            attachment_original_name="synthetic.pdf" if attachment else "",
            attachment_content_type="application/pdf" if attachment else "",
            attachment_size=len(b"%PDF-1.7\nsynthetic") if attachment else None,
        )

    def upload(self, path, data):
        return self.client.post(path, data=data, HTTP_X_CSRFTOKEN=self.csrf_token())

    def test_doctor_uploads_are_validated_and_metadata_is_safe(self):
        self.login_as(self.doctor_user)
        response = self.upload(
            "/api/doctor/medical-records/",
            {
                "patient_id": self.patient.pk,
                "appointment_id": self.appointment.pk,
                "record_type": "lab_test",
                "occurred_on": "2030-01-10",
                "diagnosis": "Synthetic CBC",
                "attachment": self.valid_pdf("../../private report.pdf"),
            },
        )
        self.assertEqual(response.status_code, 201, response.content)
        record = MedicalRecord.objects.get(diagnosis="Synthetic CBC")
        self.assertEqual(record.attachment_original_name, "private_report.pdf")
        self.assertEqual(record.attachment_content_type, "application/pdf")
        self.assertEqual(record.attachment_size, len(b"%PDF-1.7\nsynthetic"))
        self.assertTrue(record.attachment.name.startswith("protected/clinical/"))
        self.assertNotIn("private report", record.attachment.name)
        payload = response.json()
        self.assertEqual(payload["attachment_name"], "private_report.pdf")
        self.assertEqual(payload["attachment_content_type"], "application/pdf")
        self.assertEqual(payload["attachment_size"], len(b"%PDF-1.7\nsynthetic"))
        self.assertNotIn("attachment.path", response.content.decode())

    def test_upload_rejects_extension_mime_signature_and_size(self):
        self.login_as(self.doctor_user)
        base = {
            "patient_id": self.patient.pk,
            "appointment_id": self.appointment.pk,
            "record_type": "lab_test",
            "occurred_on": "2030-01-10",
            "diagnosis": "Invalid upload",
        }
        unsupported = dict(base, attachment=SimpleUploadedFile("payload.exe", b"MZ", content_type="application/octet-stream"))
        self.assertEqual(self.upload("/api/doctor/medical-records/", unsupported).status_code, 400)
        mismatch = dict(base, attachment=SimpleUploadedFile("payload.pdf", b"not a pdf", content_type="application/pdf"))
        self.assertEqual(self.upload("/api/doctor/medical-records/", mismatch).status_code, 400)
        mime_mismatch = dict(base, attachment=SimpleUploadedFile("payload.pdf", b"%PDF-1.7\nvalid", content_type="image/png"))
        self.assertEqual(self.upload("/api/doctor/medical-records/", mime_mismatch).status_code, 400)
        oversized = dict(base, attachment=SimpleUploadedFile("payload.pdf", b"%PDF-" + b"x" * (5 * 1024 * 1024), content_type="application/pdf"))
        self.assertEqual(self.upload("/api/doctor/medical-records/", oversized).status_code, 400)
        self.assertFalse(MedicalRecord.objects.filter(diagnosis="Invalid upload").exists())

    def test_doctor_report_upload_is_validated_and_patient_upload_is_denied(self):
        self.login_as(self.doctor_user)
        response = self.upload(
            "/api/doctor/reports/",
            {
                "patient_id": self.patient.pk,
                "appointment_id": self.appointment.pk,
                "title": "Synthetic Report",
                "report_type": "blood_test",
                "report_date": "2030-01-10",
                "attachment": self.valid_pdf("report.pdf"),
            },
        )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(MedicalReport.objects.get(title="Synthetic Report").attachment_content_type, "application/pdf")
        self.login_as(self.patient_user)
        self.assertEqual(
            self.client.post(
                "/api/patient/medical-records/",
                data={"attachment": self.valid_pdf()},
                HTTP_X_CSRFTOKEN=self.csrf_token(),
            ).status_code,
            405,
        )
        self.assertEqual(
            self.client.post(
                "/api/patient/reports/",
                data={"attachment": self.valid_pdf()},
                HTTP_X_CSRFTOKEN=self.csrf_token(),
            ).status_code,
            405,
        )

    def test_patient_download_is_owned_and_protected(self):
        stored = self.valid_pdf()
        record = self.create_record(attachment=stored)
        report = self.create_report(attachment=self.valid_pdf("report.pdf"))
        self.login_as(self.patient_user)
        record_response = self.client.get(f"/api/patient/medical-records/{record.pk}/download/")
        report_response = self.client.get(f"/api/patient/reports/{report.pk}/download/")
        self.assertEqual(record_response.status_code, 200)
        self.assertEqual(report_response.status_code, 200)
        self.assertEqual(record_response["Content-Type"], "application/pdf")
        self.assertEqual(record_response["X-Content-Type-Options"], "nosniff")
        self.assertIn("attachment", record_response["Content-Disposition"])
        self.assertEqual(b"".join(record_response.streaming_content), b"%PDF-1.7\nsynthetic")
        other_record = self.create_record(patient=self.other_patient, doctor=self.other_doctor, appointment=self.other_appointment, attachment=self.valid_pdf("other.pdf"))
        other_report = self.create_report(patient=self.other_patient, doctor=self.other_doctor, appointment=self.other_appointment, attachment=self.valid_pdf("other-report.pdf"))
        self.assertEqual(self.client.get(f"/api/patient/medical-records/{other_record.pk}/download/").status_code, 404)
        self.assertEqual(self.client.get(f"/api/patient/reports/{other_report.pk}/download/").status_code, 404)

    def test_doctor_download_is_appointment_scoped_and_unrelated_doctor_is_denied(self):
        record = self.create_record(attachment=self.valid_pdf())
        report = self.create_report(attachment=self.valid_pdf("report.pdf"))
        self.login_as(self.doctor_user)
        self.assertEqual(self.client.get(f"/api/doctor/medical-records/{record.pk}/download/").status_code, 200)
        self.assertEqual(self.client.get(f"/api/doctor/reports/{report.pk}/download/").status_code, 200)
        self.login_as(self.other_doctor_user)
        self.assertEqual(self.client.get(f"/api/doctor/medical-records/{record.pk}/download/").status_code, 404)
        self.assertEqual(self.client.get(f"/api/doctor/reports/{report.pk}/download/").status_code, 404)

    def test_unauthenticated_and_missing_attachment_downloads_are_denied_safely(self):
        record = self.create_record()
        self.assertEqual(self.client.get(f"/api/patient/medical-records/{record.pk}/download/").status_code, 403)
        self.login_as(self.patient_user)
        response = self.client.get(f"/api/patient/medical-records/{record.pk}/download/")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "File not found."})
        self.assertEqual(self.client.get("/api/patient/medical-records/999999/download/").status_code, 404)

    def test_patient_list_returns_safe_attachment_metadata_only(self):
        record = self.create_record(attachment=self.valid_pdf())
        self.login_as(self.patient_user)
        response = self.client.get("/api/patient/medical-records/")
        self.assertEqual(response.status_code, 200)
        item = next(row for row in response.json() if row["id"] == record.pk)
        self.assertEqual(item["attachment_name"], "synthetic.pdf")
        self.assertEqual(item["attachment_content_type"], "application/pdf")
        self.assertNotIn("protected/clinical", response.content.decode())
        self.assertNotIn("/home/", response.content.decode())

    def test_doctor_upload_requires_existing_patient_authorization(self):
        self.login_as(self.doctor_user)
        response = self.upload(
            "/api/doctor/medical-records/",
            {
                "patient_id": self.other_patient.pk,
                "record_type": "lab_test",
                "occurred_on": "2030-01-10",
                "diagnosis": "Unauthorized",
                "attachment": self.valid_pdf(),
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(MedicalRecord.objects.filter(diagnosis="Unauthorized").exists())

    def test_logout_invalidates_protected_access(self):
        record = self.create_record(attachment=self.valid_pdf())
        self.login_as(self.patient_user)
        self.assertEqual(self.client.get(f"/api/patient/medical-records/{record.pk}/download/").status_code, 200)
        csrf = self.csrf_token()
        self.assertEqual(self.client.post("/api/auth/logout/", HTTP_X_CSRFTOKEN=csrf).status_code, 200)
        self.assertEqual(self.client.get(f"/api/patient/medical-records/{record.pk}/download/").status_code, 403)
