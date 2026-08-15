from django.db import models

from apps.accounts.models import DoctorProfile, PatientProfile
from apps.clinical_api.file_security import protected_upload_to


class MedicalReport(models.Model):
    class ReportType(models.TextChoices):
        BLOOD_TEST = "blood_test", "Blood Test"
        IMAGING = "imaging", "Imaging"
        ECG = "ecg", "ECG"
        URINE_TEST = "urine_test", "Urine Test"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        NORMAL = "normal", "Normal"
        ABNORMAL = "abnormal", "Abnormal"
        PENDING = "pending", "Pending"

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.PROTECT,
        related_name="medical_reports",
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medical_reports",
    )
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medical_reports",
    )
    medical_record = models.ForeignKey(
        "medical_records.MedicalRecord",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
    )
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    laboratory_name = models.CharField(max_length=255, blank=True)
    report_date = models.DateField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    summary = models.TextField(blank=True)
    interpretation = models.TextField(blank=True)
    attachment = models.FileField(upload_to=protected_upload_to, null=True, blank=True)
    attachment_original_name = models.CharField(max_length=180, blank=True)
    attachment_content_type = models.CharField(max_length=100, blank=True)
    attachment_size = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-report_date", "-created_at"]
        indexes = [
            models.Index(fields=["patient", "-report_date"]),
            models.Index(fields=["report_type", "-report_date"]),
            models.Index(fields=["status", "-report_date"]),
        ]

    def __str__(self):
        return self.title


class ReportFinding(models.Model):
    report = models.ForeignKey(
        MedicalReport,
        on_delete=models.CASCADE,
        related_name="findings",
    )
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    is_normal = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.label}: {self.value}"
