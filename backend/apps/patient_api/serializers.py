import re

from rest_framework import serializers

from apps.accounts.models import PatientPreferences, PatientProfile


class PatientProfileSerializer(serializers.Serializer):
    protected_input_fields = {"email", "role", "id", "user_id", "patient_id", "is_active", "is_staff", "password", "password_hash"}

    def to_internal_value(self, data):
        invalid = {}
        for field in data:
            if field in self.protected_input_fields:
                invalid[field] = "This field cannot be modified here."
            elif field not in self.fields:
                invalid[field] = "This field is not permitted."
        if invalid:
            raise serializers.ValidationError(invalid)
        return super().to_internal_value(data)

    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", required=False, max_length=100)
    last_name = serializers.CharField(source="user.last_name", required=False, max_length=100)
    phone = serializers.CharField(source="user.phone", required=False, max_length=32)
    date_of_birth = serializers.DateField(source="user.date_of_birth", required=False, allow_null=True)
    gender = serializers.CharField(source="user.gender", required=False, max_length=32, allow_blank=True)
    role = serializers.CharField(source="user.role", read_only=True)
    blood_group = serializers.ChoiceField(choices=PatientProfile.BloodGroup.choices, required=False)
    address = serializers.CharField(required=False, allow_blank=True)

    def validate_first_name(self, value):
        if not re.fullmatch(r"[A-Za-z ]+", value.strip()):
            raise serializers.ValidationError("Enter a valid first name.")
        return value.strip()

    def validate_last_name(self, value):
        if not re.fullmatch(r"[A-Za-z ]+", value.strip()):
            raise serializers.ValidationError("Enter a valid last name.")
        return value.strip()

    def validate_phone(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Enter a valid 10-digit phone number.")
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        user = instance.user
        for field, value in user_data.items():
            setattr(user, field, value)
        if user_data:
            user.save(update_fields=[*user_data.keys()])

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        return {
            "email": instance.user.email,
            "first_name": instance.user.first_name,
            "last_name": instance.user.last_name,
            "phone": instance.user.phone,
            "date_of_birth": instance.user.date_of_birth,
            "gender": instance.user.gender,
            "role": instance.user.role,
            "blood_group": instance.blood_group,
            "address": instance.address,
        }


class PatientSettingsSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        invalid = {
            field: "This field is not permitted."
            for field in data
            if field not in self.fields
        }
        if invalid:
            raise serializers.ValidationError(invalid)
        return super().to_internal_value(data)

    class Meta:
        model = PatientPreferences
        fields = [
            "appointment_notifications",
            "laboratory_notifications",
            "prescription_notifications",
            "health_tips",
            "newsletter",
            "notification_method",
            "theme",
            "font_size",
        ]


class PatientActivitySerializer(serializers.Serializer):
    activity_type = serializers.CharField()
    title = serializers.CharField()
    subtitle = serializers.CharField()
    activity_date = serializers.DateField()
    icon = serializers.CharField()


class PatientDashboardSerializer(serializers.Serializer):
    upcoming_appointment_count = serializers.IntegerField()
    medical_record_count = serializers.IntegerField()
    active_prescription_count = serializers.IntegerField()
    recent_activity = PatientActivitySerializer(many=True)
