from rest_framework import serializers

from apps.accounts.models import DoctorProfile, PatientProfile, User
from apps.appointments.models import Appointment


class AdminRecentAppointmentSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(read_only=True)
    patient_name = serializers.SerializerMethodField()
    doctor_id = serializers.IntegerField(read_only=True)
    doctor_name = serializers.SerializerMethodField()
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id", "patient_id", "patient_name", "doctor_id", "doctor_name",
            "scheduled_date", "scheduled_time", "status", "status_label", "reason",
        ]
        read_only_fields = fields

    def get_patient_name(self, appointment):
        return f"{appointment.patient.user.first_name} {appointment.patient.user.last_name}".strip()

    def get_doctor_name(self, appointment):
        return f"{appointment.doctor.user.first_name} {appointment.doctor.user.last_name}".strip()


class AdminDashboardSerializer(serializers.Serializer):
    total_patients = serializers.IntegerField(read_only=True)
    total_doctors = serializers.IntegerField(read_only=True)
    total_appointments = serializers.IntegerField(read_only=True)
    pending_appointments = serializers.IntegerField(read_only=True)
    completed_appointments = serializers.IntegerField(read_only=True)
    cancelled_appointments = serializers.IntegerField(read_only=True)
    active_users = serializers.IntegerField(read_only=True)
    inactive_users = serializers.IntegerField(read_only=True)
    recent_appointments = AdminRecentAppointmentSerializer(many=True, read_only=True)


class AdminPatientSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)
    is_active = serializers.BooleanField(source="user.is_active", read_only=True)
    date_joined = serializers.DateTimeField(source="user.date_joined", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)
    role_label = serializers.CharField(source="user.get_role_display", read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            "id", "user_id", "first_name", "last_name", "email", "phone", "role",
            "role_label", "is_active", "date_joined", "created_at", "updated_at",
        ]
        read_only_fields = fields


class AdminDoctorSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)
    is_active = serializers.BooleanField(source="user.is_active", read_only=True)
    date_joined = serializers.DateTimeField(source="user.date_joined", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)
    role_label = serializers.CharField(source="user.get_role_display", read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            "id", "user_id", "first_name", "last_name", "email", "phone",
            "specialization", "license_id", "role", "role_label", "is_active",
            "date_joined", "created_at", "updated_at",
        ]
        read_only_fields = fields


class AdminAppointmentSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(read_only=True)
    patient_name = serializers.SerializerMethodField()
    doctor_id = serializers.IntegerField(read_only=True)
    doctor_name = serializers.SerializerMethodField()
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id", "patient_id", "patient_name", "doctor_id", "doctor_name",
            "scheduled_date", "scheduled_time", "status", "status_label", "reason",
            "notes", "created_at", "updated_at",
        ]
        read_only_fields = fields

    def get_patient_name(self, appointment):
        return f"{appointment.patient.user.first_name} {appointment.patient.user.last_name}".strip()

    def get_doctor_name(self, appointment):
        return f"{appointment.doctor.user.first_name} {appointment.doctor.user.last_name}".strip()


class AdminProfileSerializer(serializers.ModelSerializer):
    role_label = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "phone", "role",
            "role_label", "is_active", "date_joined",
        ]
        read_only_fields = fields


class AdminUserStatusSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=True)


class AdminUserStatusResponseSerializer(serializers.ModelSerializer):
    role_label = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "role", "role_label", "is_active"]
        read_only_fields = fields
