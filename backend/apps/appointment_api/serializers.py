from django.utils import timezone
from rest_framework import serializers

from apps.accounts.models import DoctorProfile
from apps.appointments.models import Appointment


class DoctorProfileSerializer(serializers.Serializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)
    specialization = serializers.CharField(read_only=True)
    license_id = serializers.CharField(read_only=True)
    contact_details = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        return {
            "email": instance.user.email,
            "first_name": instance.user.first_name,
            "last_name": instance.user.last_name,
            "role": instance.user.role,
            "specialization": instance.specialization,
            "license_id": instance.license_id,
            "contact_details": instance.contact_details,
        }


class DoctorDirectorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    specialization = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        return {
            "id": instance.pk,
            "name": f"Dr. {instance.user.first_name} {instance.user.last_name}".strip(),
            "specialization": instance.specialization,
        }


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_id = serializers.IntegerField(source="doctor.pk", read_only=True)
    patient_id = serializers.IntegerField(source="patient.pk", read_only=True)
    doctor_name = serializers.SerializerMethodField()
    doctor_specialization = serializers.CharField(source="doctor.specialization", read_only=True)
    patient_name = serializers.SerializerMethodField()
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "doctor_id",
            "patient_id",
            "doctor_name",
            "doctor_specialization",
            "patient_name",
            "scheduled_date",
            "scheduled_time",
            "status",
            "status_label",
            "reason",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_doctor_name(self, appointment):
        return f"Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}".strip()

    def get_patient_name(self, appointment):
        return f"{appointment.patient.user.first_name} {appointment.patient.user.last_name}".strip()


class PatientAppointmentCreateSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField()
    scheduled_date = serializers.DateField()
    scheduled_time = serializers.TimeField()
    reason = serializers.CharField(required=False, allow_blank=True, max_length=255)

    def to_internal_value(self, data):
        allowed = {"doctor_id", "scheduled_date", "scheduled_time", "reason"}
        invalid = {
            field: "This field is not permitted; ownership and status are server-controlled."
            for field in data
            if field not in allowed
        }
        if invalid:
            raise serializers.ValidationError(invalid)
        return super().to_internal_value(data)

    def validate_doctor_id(self, value):
        try:
            doctor = DoctorProfile.objects.select_related("user").get(pk=value, user__role="doctor", user__is_active=True)
        except DoctorProfile.DoesNotExist as exc:
            raise serializers.ValidationError("Select a valid active doctor.") from exc
        self._doctor = doctor
        return value

    def validate(self, attrs):
        scheduled_date = attrs["scheduled_date"]
        scheduled_time = attrs["scheduled_time"]
        now = timezone.localtime()
        if scheduled_date < now.date() or (scheduled_date == now.date() and scheduled_time <= now.time().replace(microsecond=0)):
            raise serializers.ValidationError("Appointment date and time must be in the future.")
        attrs["doctor"] = getattr(self, "_doctor", DoctorProfile.objects.get(pk=attrs["doctor_id"]))
        return attrs


class AppointmentTransitionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["confirm", "reject", "cancel", "complete"])

    def to_internal_value(self, data):
        invalid = {
            field: "Only the lifecycle action may be submitted."
            for field in data
            if field != "action"
        }
        if invalid:
            raise serializers.ValidationError(invalid)
        return super().to_internal_value(data)

    def validate_action(self, value):
        return value


class DoctorPatientSummarySerializer(serializers.Serializer):
    patient_id = serializers.IntegerField()
    patient_name = serializers.CharField()
    age = serializers.IntegerField(allow_null=True)
    condition = serializers.CharField()
    last_visit = serializers.DateField(allow_null=True)
    status = serializers.CharField()


class DoctorDashboardSerializer(serializers.Serializer):
    doctor = DoctorProfileSerializer()
    pending_count = serializers.IntegerField()
    confirmed_count = serializers.IntegerField()
    today_count = serializers.IntegerField()
    completed_count = serializers.IntegerField()
    upcoming_count = serializers.IntegerField()
    patient_count = serializers.IntegerField()
    authorized_patients = DoctorPatientSummarySerializer(many=True)
    today_appointments = AppointmentSerializer(many=True)
