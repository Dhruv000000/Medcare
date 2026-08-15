from django.conf import settings
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from .models import DoctorProfile, PatientPreferences, PatientProfile, User


ROLE_ALIASES = {
    "patient": User.Role.PATIENT,
    "doctor": User.Role.DOCTOR,
    "admin": User.Role.ADMINISTRATOR,
    "administrator": User.Role.ADMINISTRATOR,
}


class RegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=32)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.CharField(max_length=32)
    role = serializers.CharField()
    doctor_id = serializers.CharField(max_length=120, required=False, allow_blank=True)
    admin_code = serializers.CharField(max_length=255, required=False, allow_blank=True, write_only=True)
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    confirm_password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_email(self, value):
        value = User.objects.normalize_email(value).lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_phone(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Enter a valid 10-digit phone number.")
        return value

    def validate_role(self, value):
        normalized = ROLE_ALIASES.get(value.strip().lower())
        if not normalized:
            raise serializers.ValidationError("Select a valid role.")
        return normalized

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        try:
            password_validation.validate_password(attrs["password"])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc

        if attrs["role"] == User.Role.DOCTOR and not attrs.get("doctor_id"):
            raise serializers.ValidationError({"doctor_id": "Medical License ID is required for doctors."})

        if attrs["role"] == User.Role.ADMINISTRATOR:
            configured_code = getattr(settings, "ADMIN_REGISTRATION_CODE", "")
            if not configured_code or attrs.get("admin_code") != configured_code:
                raise serializers.ValidationError({"admin_code": "Administrator registration is not available."})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        role = validated_data.pop("role")
        doctor_id = validated_data.pop("doctor_id", "")
        validated_data.pop("admin_code", None)
        password = validated_data.pop("password")
        validated_data.pop("confirm_password")

        user = User.objects.create_user(password=password, role=role, **validated_data)

        if role == User.Role.PATIENT:
            patient = PatientProfile.objects.create(user=user)
            PatientPreferences.objects.create(patient=patient)
        elif role == User.Role.DOCTOR:
            DoctorProfile.objects.create(user=user, license_id=doctor_id, specialization="Unspecified")

        return user


class SafeUserSerializer(serializers.ModelSerializer):
    role_label = serializers.CharField(source="get_role_display", read_only=True)
    patient_profile = serializers.SerializerMethodField()
    doctor_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "date_of_birth",
            "gender",
            "role",
            "role_label",
            "patient_profile",
            "doctor_profile",
        ]
        read_only_fields = fields

    def get_patient_profile(self, user):
        try:
            profile = user.patient_profile
        except PatientProfile.DoesNotExist:
            return None
        return {
            "blood_group": profile.blood_group,
            "address": profile.address,
        }

    def get_doctor_profile(self, user):
        try:
            profile = user.doctor_profile
        except DoctorProfile.DoesNotExist:
            return None
        return {
            "specialization": profile.specialization,
            "license_id": profile.license_id,
        }
