from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class AiPredictionEvent(models.Model):
    class Status(models.TextChoices):
        COMPLETED = "completed", "Completed"
        VALIDATION_FAILED = "validation_failed", "Validation failed"
        INFERENCE_FAILED = "inference_failed", "Inference failed"
        MODEL_UNAVAILABLE = "model_unavailable", "Model unavailable"

    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requesting_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ai_prediction_events",
        editable=False,
    )
    requesting_role = models.CharField(max_length=20, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, editable=False)
    model_version = models.CharField(max_length=120, editable=False, db_index=True)
    preprocessing_version = models.CharField(max_length=120, editable=False)
    status = models.CharField(max_length=32, choices=Status.choices, editable=False, db_index=True)
    prediction_label = models.CharField(max_length=32, blank=True, editable=False)
    model_probability = models.FloatField(null=True, blank=True, editable=False)
    explanation = models.JSONField(default=dict, blank=True, editable=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["requesting_user", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["model_version", "-created_at"]),
        ]

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValueError("AI prediction events are immutable.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("AI prediction events cannot be deleted.")

    def __str__(self):
        return f"{self.model_version} {self.status} {self.event_id}"
