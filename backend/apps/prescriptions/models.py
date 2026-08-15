from django.db import models
from django.db.models import F, Q

from apps.accounts.models import DoctorProfile, PatientProfile


class Prescription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        REFILL_NEEDED = "refill_needed", "Refill Needed"
        COMPLETED = "completed", "Completed"

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.PROTECT,
        related_name="prescriptions",
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.PROTECT,
        related_name="prescriptions",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    issued_on = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issued_on", "-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__isnull=True) | Q(start_date__lte=F("end_date")),
                name="prescription_start_before_end",
            ),
        ]
        indexes = [
            models.Index(fields=["patient", "-issued_on"]),
            models.Index(fields=["doctor", "-issued_on"]),
            models.Index(fields=["status", "-end_date"]),
        ]

    def __str__(self):
        return f"Prescription {self.pk} for {self.patient}"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="items",
    )
    medicine = models.CharField(max_length=255)
    dosage = models.CharField(max_length=120)
    frequency = models.CharField(max_length=120)
    duration = models.CharField(max_length=120, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    instructions = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)

    class Meta:
        ordering = ["medicine", "id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__isnull=True) | Q(start_date__isnull=True) | Q(start_date__lte=F("end_date")),
                name="prescription_item_start_before_end",
            ),
        ]

    def __str__(self):
        return f"{self.medicine} ({self.dosage})"
