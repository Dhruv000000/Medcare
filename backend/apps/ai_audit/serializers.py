from rest_framework import serializers

from apps.ai_api.constants import ACADEMIC_DISCLAIMER

from .models import AiPredictionEvent


class AiPredictionReportSerializer(serializers.ModelSerializer):
    disclaimer = serializers.SerializerMethodField()
    probability_note = serializers.SerializerMethodField()
    clinician_responsibility = serializers.SerializerMethodField()

    class Meta:
        model = AiPredictionEvent
        fields = [
            "event_id",
            "created_at",
            "model_version",
            "preprocessing_version",
            "status",
            "prediction_label",
            "model_probability",
            "explanation",
            "disclaimer",
            "probability_note",
            "clinician_responsibility",
        ]
        read_only_fields = fields

    def get_disclaimer(self, obj):
        return ACADEMIC_DISCLAIMER

    def get_probability_note(self, obj):
        return "Model probability is not diagnostic confidence or clinical certainty."

    def get_clinician_responsibility(self, obj):
        return "The clinician remains responsible for interpretation and decisions."


class AiAuditSummarySerializer(serializers.Serializer):
    total_events = serializers.IntegerField(read_only=True)
    completed_events = serializers.IntegerField(read_only=True)
    rejected_events = serializers.IntegerField(read_only=True)
    model_versions = serializers.ListField(child=serializers.CharField(), read_only=True)
