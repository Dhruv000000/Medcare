from __future__ import annotations

import math
from collections.abc import Mapping

from rest_framework import serializers

from .constants import (
    ACADEMIC_DISCLAIMER,
    CATEGORICAL_DOMAINS,
    FEATURE_ORDER,
    NUMERIC_SUPPORT_DOMAINS,
)


class HeartRiskPredictionRequestSerializer(serializers.Serializer):
    age = serializers.FloatField(required=True)
    sex = serializers.IntegerField(required=True)
    cp = serializers.IntegerField(required=True)
    trestbps = serializers.FloatField(required=True)
    chol = serializers.FloatField(required=True)
    fbs = serializers.IntegerField(required=True)
    restecg = serializers.IntegerField(required=True)
    thalach = serializers.FloatField(required=True)
    exang = serializers.IntegerField(required=True)
    oldpeak = serializers.FloatField(required=True)
    slope = serializers.IntegerField(required=True)
    ca = serializers.IntegerField(required=True)
    thal = serializers.IntegerField(required=True)

    def to_internal_value(self, data):
        if not isinstance(data, Mapping):
            raise serializers.ValidationError({"detail": "Expected a JSON object."})

        unknown = sorted(set(data.keys()) - set(FEATURE_ORDER))
        if unknown:
            raise serializers.ValidationError(
                {field: "This field is not permitted." for field in unknown}
            )

        errors = {}
        integer_fields = set(CATEGORICAL_DOMAINS)
        for field in FEATURE_ORDER:
            if field not in data:
                continue
            value = data[field]
            if field in integer_fields:
                if isinstance(value, bool) or not isinstance(value, int):
                    errors[field] = "Expected a JSON integer."
            else:
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    errors[field] = "Expected a finite JSON number."
                elif not math.isfinite(float(value)):
                    errors[field] = "Value must be finite; NaN and Infinity are not permitted."
        if errors:
            raise serializers.ValidationError(errors)
        return super().to_internal_value(data)

    def validate(self, attrs):
        errors = {}
        for field, allowed in CATEGORICAL_DOMAINS.items():
            value = attrs.get(field)
            if value not in allowed:
                errors[field] = f"Use one of the approved source codes: {sorted(allowed)}."

        for field, (minimum, maximum) in NUMERIC_SUPPORT_DOMAINS.items():
            value = attrs.get(field)
            if value is None or not math.isfinite(float(value)):
                errors[field] = "Value must be finite."
            elif not minimum <= float(value) <= maximum:
                errors[field] = (
                    f"Value must remain within the verified Phase 17 dataset support "
                    f"domain [{minimum:g}, {maximum:g}]."
                )
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def feature_frame(self):
        """Return a one-row mapping in the exact trained feature order."""

        if not hasattr(self, "validated_data"):
            raise RuntimeError("Call is_valid() before feature_frame().")
        return {field: self.validated_data[field] for field in FEATURE_ORDER}


class HeartRiskFeatureContributionSerializer(serializers.Serializer):
    feature = serializers.ChoiceField(choices=FEATURE_ORDER, read_only=True)
    value = serializers.FloatField(read_only=True)
    contribution = serializers.FloatField(read_only=True)
    direction = serializers.ChoiceField(
        choices=["supports_predicted_class", "opposes_predicted_class", "neutral"],
        read_only=True,
    )


class HeartRiskExplanationSerializer(serializers.Serializer):
    method = serializers.CharField(read_only=True)
    preprocessing = serializers.CharField(read_only=True)
    output_space = serializers.ChoiceField(choices=["logit"], read_only=True)
    base_value = serializers.FloatField(read_only=True)
    features = HeartRiskFeatureContributionSerializer(many=True, read_only=True)
    disclaimer = serializers.CharField(read_only=True)


class HeartRiskPredictionResponseSerializer(serializers.Serializer):
    model = serializers.CharField(read_only=True)
    prediction = serializers.ChoiceField(choices=["label_absent", "label_present"], read_only=True)
    model_probability = serializers.FloatField(read_only=True, allow_null=True)
    status = serializers.ChoiceField(choices=["academic_development_only"], read_only=True)
    disclaimer = serializers.CharField(read_only=True, default=ACADEMIC_DISCLAIMER)
    explanation = HeartRiskExplanationSerializer(read_only=True)


class SymptomChatMessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["user", "assistant"])
    content = serializers.CharField(max_length=2000, allow_blank=False, trim_whitespace=True)


class SymptomChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000, allow_blank=False, trim_whitespace=True)
    history = SymptomChatMessageSerializer(many=True, required=False, default=list)

    def validate_history(self, value):
        if len(value) > 20:
            raise serializers.ValidationError("Conversation history is too long.")
        return value
