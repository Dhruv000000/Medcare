from django.db import models

from apps.accounts.models import DoctorProfile, PatientProfile


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    reason = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["scheduled_date", "scheduled_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "scheduled_date", "scheduled_time"],
                name="unique_doctor_appointment_slot",
            ),
            models.UniqueConstraint(
                fields=["patient", "scheduled_date", "scheduled_time"],
                name="unique_patient_appointment_slot",
            ),
        ]
        indexes = [
            models.Index(fields=["patient", "scheduled_date"]),
            models.Index(fields=["doctor", "scheduled_date"]),
            models.Index(fields=["status", "scheduled_date"]),
        ]

    def __str__(self):
        return f"{self.doctor} with {self.patient} on {self.scheduled_date}"
