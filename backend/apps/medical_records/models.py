from django.db import models

from apps.accounts.models import DoctorProfile, PatientProfile
from apps.clinical_api.file_security import protected_upload_to


class MedicalRecord(models.Model):
    class RecordType(models.TextChoices):
        LAB_TEST = "lab_test", "Lab Test"
        CONSULTATION = "consultation", "Consultation"
        IMAGING = "imaging", "Imaging"
        PRESCRIPTION = "prescription", "Prescription"
        OTHER = "other", "Other"

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.PROTECT,
        related_name="medical_records",
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medical_records",
    )
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medical_records",
    )
    record_type = models.CharField(max_length=20, choices=RecordType.choices)
    occurred_on = models.DateField()
    diagnosis = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to=protected_upload_to, null=True, blank=True)
    attachment_original_name = models.CharField(max_length=180, blank=True)
    attachment_content_type = models.CharField(max_length=100, blank=True)
    attachment_size = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-occurred_on", "-created_at"]
        indexes = [
            models.Index(fields=["patient", "-occurred_on"]),
            models.Index(fields=["record_type", "-occurred_on"]),
        ]

    def __str__(self):
        return f"{self.record_type}: {self.diagnosis}"
