from __future__ import annotations

import json
import os
import sys
from datetime import date, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, str(ROOT / "backend"))

import django

django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile

from apps.accounts.models import DoctorProfile, PatientProfile, User
from apps.appointments.models import Appointment
from apps.medical_records.models import MedicalRecord
from apps.reports.models import MedicalReport

PASSWORD = "Phase24-Smoke-Password-123!"
EMAILS = [
    "phase24.patient@example.test",
    "phase24.other.patient@example.test",
    "phase24.doctor@example.test",
    "phase24.other.doctor@example.test",
    "phase24.admin@example.test",
]

for email in EMAILS:
    User.objects.filter(email=email).delete()

patient_user = User.objects.create_user(
    email=EMAILS[0], password=PASSWORD, first_name="Phase24", last_name="Patient", role=User.Role.PATIENT, date_of_birth=date(1990, 1, 1), gender="Other"
)
patient = PatientProfile.objects.create(user=patient_user)
other_patient_user = User.objects.create_user(
    email=EMAILS[1], password=PASSWORD, first_name="Other", last_name="Patient", role=User.Role.PATIENT, date_of_birth=date(1991, 2, 2), gender="Other"
)
other_patient = PatientProfile.objects.create(user=other_patient_user)
doctor_user = User.objects.create_user(
    email=EMAILS[2], password=PASSWORD, first_name="Phase24", last_name="Doctor", role=User.Role.DOCTOR
)
doctor = DoctorProfile.objects.create(user=doctor_user, specialization="Cardiology", license_id="PHASE24-SMOKE-001")
other_doctor_user = User.objects.create_user(
    email=EMAILS[3], password=PASSWORD, first_name="Other", last_name="Doctor", role=User.Role.DOCTOR
)
other_doctor = DoctorProfile.objects.create(user=other_doctor_user, specialization="Dermatology", license_id="PHASE24-SMOKE-002")
admin_user = User.objects.create_user(
    email="phase24.admin@example.test", password=PASSWORD, first_name="Phase24", last_name="Admin", role=User.Role.ADMINISTRATOR, is_staff=True
)
appointment = Appointment.objects.create(
    patient=patient, doctor=doctor, scheduled_date=date.today(), scheduled_time=time(9, 30), status=Appointment.Status.CONFIRMED, reason="Synthetic Phase 24 review"
)
other_appointment = Appointment.objects.create(
    patient=other_patient, doctor=other_doctor, scheduled_date=date.today(), scheduled_time=time(10, 30), status=Appointment.Status.CONFIRMED, reason="Synthetic unrelated appointment"
)

pdf = b"%PDF-1.7\nPhase24 synthetic file\n"
record = MedicalRecord.objects.create(
    patient=patient,
    doctor=doctor,
    appointment=appointment,
    record_type=MedicalRecord.RecordType.LAB_TEST,
    occurred_on=date.today(),
    diagnosis="Synthetic CBC",
    notes="Synthetic browser smoke record",
    attachment=SimpleUploadedFile("phase24-record.pdf", pdf, content_type="application/pdf"),
    attachment_original_name="phase24-record.pdf",
    attachment_content_type="application/pdf",
    attachment_size=len(pdf),
)
report = MedicalReport.objects.create(
    patient=patient,
    doctor=doctor,
    appointment=appointment,
    title="Synthetic Blood Report",
    report_type=MedicalReport.ReportType.BLOOD_TEST,
    laboratory_name="Synthetic Lab",
    report_date=date.today(),
    status=MedicalReport.Status.NORMAL,
    summary="Synthetic browser smoke report",
    interpretation="Synthetic only",
    attachment=SimpleUploadedFile("phase24-report.pdf", pdf, content_type="application/pdf"),
    attachment_original_name="phase24-report.pdf",
    attachment_content_type="application/pdf",
    attachment_size=len(pdf),
)
other_record = MedicalRecord.objects.create(
    patient=other_patient,
    doctor=other_doctor,
    appointment=other_appointment,
    record_type=MedicalRecord.RecordType.OTHER,
    occurred_on=date.today(),
    diagnosis="Other synthetic record",
    attachment=SimpleUploadedFile("other-record.pdf", pdf, content_type="application/pdf"),
    attachment_original_name="other-record.pdf",
    attachment_content_type="application/pdf",
    attachment_size=len(pdf),
)
print(json.dumps({
    "password": PASSWORD,
    "patient": patient_user.email,
    "other_patient": other_patient_user.email,
    "doctor": doctor_user.email,
    "other_doctor": other_doctor_user.email,
    "admin": admin_user.email,
    "record_id": record.pk,
    "report_id": report.pk,
    "other_record_id": other_record.pk,
    "record_download": f"/api/patient/medical-records/{record.pk}/download/",
    "doctor_record_download": f"/api/doctor/medical-records/{record.pk}/download/",
}, indent=2))
