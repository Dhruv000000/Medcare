from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .file_security import validate_uploaded_file

from apps.accounts.models import DoctorProfile, PatientProfile
from apps.appointments.models import Appointment
from apps.medical_records.models import MedicalRecord
from apps.prescriptions.models import Prescription, PrescriptionItem
from apps.reports.models import MedicalReport, ReportFinding


class MedicalRecordSerializer(serializers.ModelSerializer):
    record_type_label = serializers.CharField(source="get_record_type_display", read_only=True)
    patient_name = serializers.SerializerMethodField()
    patient_email = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    doctor_specialization = serializers.SerializerMethodField()
    attachment_name = serializers.SerializerMethodField()
    has_attachment = serializers.SerializerMethodField()

    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "patient_id",
            "patient_name",
            "patient_email",
            "doctor_name",
            "doctor_specialization",
            "appointment_id",
            "record_type",
            "record_type_label",
            "occurred_on",
            "diagnosis",
            "notes",
            "attachment_name",
            "attachment_original_name",
            "attachment_content_type",
            "attachment_size",
            "has_attachment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_patient_name(self, obj):
        return _user_display_name(obj.patient.user)

    def get_patient_email(self, obj):
        return obj.patient.user.email

    def get_doctor_name(self, obj):
        return _user_display_name(obj.doctor.user) if obj.doctor else ""

    def get_doctor_specialization(self, obj):
        return obj.doctor.specialization if obj.doctor else ""

    def get_attachment_name(self, obj):
        return obj.attachment_original_name or (obj.attachment.name.rsplit("/", 1)[-1] if obj.attachment else "")

    def get_has_attachment(self, obj):
        return bool(obj.attachment)


class DoctorMedicalRecordCreateSerializer(serializers.Serializer):
    patient_id = serializers.PrimaryKeyRelatedField(queryset=PatientProfile.objects.select_related("user"))
    appointment_id = serializers.IntegerField(required=False, allow_null=True)
    record_type = serializers.ChoiceField(choices=MedicalRecord.RecordType.choices)
    occurred_on = serializers.DateField()
    diagnosis = serializers.CharField(max_length=255)
    notes = serializers.CharField(required=False, allow_blank=True)
    attachment = serializers.FileField(required=False, allow_null=True, write_only=True)

    protected_fields = {"id", "patient", "doctor", "doctor_id", "created_at", "updated_at"}

    def to_internal_value(self, data):
        supplied = set(data.keys()) if hasattr(data, "keys") else set()
        forbidden = sorted(supplied & self.protected_fields)
        if forbidden:
            raise serializers.ValidationError(
                {field: "This field is server-managed and cannot be supplied." for field in forbidden}
            )
        return super().to_internal_value(data)

    def validate(self, attrs):
        doctor = self.context["doctor"]
        patient = attrs["patient_id"]
        if not Appointment.objects.filter(doctor=doctor, patient=patient).exists():
            raise serializers.ValidationError({"patient_id": "This patient is not authorized for this doctor."})

        upload = attrs.get("attachment")
        if upload is not None:
            try:
                attrs["attachment_metadata"] = validate_uploaded_file(upload)
            except DjangoValidationError as exc:
                raise serializers.ValidationError({"attachment": exc.messages}) from exc

        appointment_id = attrs.get("appointment_id")
        if appointment_id is not None:
            appointment = Appointment.objects.filter(
                pk=appointment_id,
                doctor=doctor,
                patient=patient,
            ).first()
            if appointment is None:
                raise serializers.ValidationError(
                    {"appointment_id": "The appointment must belong to this doctor and patient."}
                )
            attrs["appointment"] = appointment
        return attrs


class PrescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = [
            "id",
            "medicine",
            "dosage",
            "frequency",
            "duration",
            "start_date",
            "end_date",
            "instructions",
            "side_effects",
        ]
        read_only_fields = fields


class PrescriptionSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    patient_name = serializers.SerializerMethodField()
    patient_email = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    doctor_specialization = serializers.SerializerMethodField()
    items = PrescriptionItemSerializer(many=True, read_only=True)

    class Meta:
        model = Prescription
        fields = [
            "id",
            "patient_id",
            "patient_name",
            "patient_email",
            "doctor_id",
            "doctor_name",
            "doctor_specialization",
            "status",
            "status_label",
            "issued_on",
            "start_date",
            "end_date",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_patient_name(self, obj):
        return _user_display_name(obj.patient.user)

    def get_patient_email(self, obj):
        return obj.patient.user.email

    def get_doctor_name(self, obj):
        return _user_display_name(obj.doctor.user)

    def get_doctor_specialization(self, obj):
        return obj.doctor.specialization


class PrescriptionItemCreateSerializer(serializers.Serializer):
    medicine = serializers.CharField(max_length=255)
    dosage = serializers.CharField(max_length=120)
    frequency = serializers.CharField(max_length=120)
    duration = serializers.CharField(max_length=120, required=False, allow_blank=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    instructions = serializers.CharField(required=False, allow_blank=True)
    side_effects = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if start and end and start > end:
            raise serializers.ValidationError("Item start_date cannot be after end_date.")
        return attrs


class DoctorPrescriptionCreateSerializer(serializers.Serializer):
    patient_id = serializers.PrimaryKeyRelatedField(queryset=PatientProfile.objects.select_related("user"))
    status = serializers.ChoiceField(choices=Prescription.Status.choices, default=Prescription.Status.ACTIVE)
    issued_on = serializers.DateField()
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)
    items = PrescriptionItemCreateSerializer(many=True, allow_empty=False)

    protected_fields = {"id", "patient", "doctor", "doctor_id", "created_at", "updated_at"}

    def to_internal_value(self, data):
        supplied = set(data.keys()) if hasattr(data, "keys") else set()
        forbidden = sorted(supplied & self.protected_fields)
        if forbidden:
            raise serializers.ValidationError(
                {field: "This field is server-managed and cannot be supplied." for field in forbidden}
            )
        return super().to_internal_value(data)

    def validate(self, attrs):
        doctor = self.context["doctor"]
        patient = attrs["patient_id"]
        if not Appointment.objects.filter(doctor=doctor, patient=patient).exists():
            raise serializers.ValidationError({"patient_id": "This patient is not authorized for this doctor."})
        end = attrs.get("end_date")
        if end and attrs["start_date"] > end:
            raise serializers.ValidationError({"end_date": "end_date cannot be before start_date."})
        return attrs


class ReportFindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportFinding
        fields = ["id", "label", "value", "is_normal", "sort_order"]
        read_only_fields = fields


class MedicalReportSerializer(serializers.ModelSerializer):
    report_type_label = serializers.CharField(source="get_report_type_display", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    patient_name = serializers.SerializerMethodField()
    patient_email = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    doctor_specialization = serializers.SerializerMethodField()
    attachment_name = serializers.SerializerMethodField()
    has_attachment = serializers.SerializerMethodField()
    findings = ReportFindingSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalReport
        fields = [
            "id",
            "patient_id",
            "patient_name",
            "patient_email",
            "doctor_id",
            "doctor_name",
            "doctor_specialization",
            "appointment_id",
            "medical_record_id",
            "title",
            "report_type",
            "report_type_label",
            "laboratory_name",
            "report_date",
            "status",
            "status_label",
            "summary",
            "interpretation",
            "attachment_name",
            "attachment_original_name",
            "attachment_content_type",
            "attachment_size",
            "has_attachment",
            "findings",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_patient_name(self, obj):
        return _user_display_name(obj.patient.user)

    def get_patient_email(self, obj):
        return obj.patient.user.email

    def get_doctor_name(self, obj):
        return _user_display_name(obj.doctor.user) if obj.doctor else ""

    def get_doctor_specialization(self, obj):
        return obj.doctor.specialization if obj.doctor else ""

    def get_attachment_name(self, obj):
        return obj.attachment_original_name or (obj.attachment.name.rsplit("/", 1)[-1] if obj.attachment else "")

    def get_has_attachment(self, obj):
        return bool(obj.attachment)


class ReportFindingCreateSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=255)
    value = serializers.CharField(max_length=255)
    is_normal = serializers.BooleanField(default=True)
    sort_order = serializers.IntegerField(min_value=0, default=0)


class DoctorReportCreateSerializer(serializers.Serializer):
    patient_id = serializers.PrimaryKeyRelatedField(queryset=PatientProfile.objects.select_related("user"))
    appointment_id = serializers.IntegerField(required=False, allow_null=True)
    medical_record_id = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField(max_length=255)
    report_type = serializers.ChoiceField(choices=MedicalReport.ReportType.choices)
    laboratory_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    report_date = serializers.DateField()
    status = serializers.ChoiceField(choices=MedicalReport.Status.choices, default=MedicalReport.Status.PENDING)
    summary = serializers.CharField(required=False, allow_blank=True)
    interpretation = serializers.CharField(required=False, allow_blank=True)
    findings = ReportFindingCreateSerializer(many=True, required=False)
    attachment = serializers.FileField(required=False, allow_null=True, write_only=True)

    protected_fields = {"id", "patient", "doctor", "doctor_id", "created_at", "updated_at"}

    def to_internal_value(self, data):
        supplied = set(data.keys()) if hasattr(data, "keys") else set()
        forbidden = sorted(supplied & self.protected_fields)
        if forbidden:
            raise serializers.ValidationError(
                {field: "This field is server-managed and cannot be supplied." for field in forbidden}
            )
        return super().to_internal_value(data)

    def validate(self, attrs):
        doctor = self.context["doctor"]
        patient = attrs["patient_id"]
        if not Appointment.objects.filter(doctor=doctor, patient=patient).exists():
            raise serializers.ValidationError({"patient_id": "This patient is not authorized for this doctor."})

        upload = attrs.get("attachment")
        if upload is not None:
            try:
                attrs["attachment_metadata"] = validate_uploaded_file(upload)
            except DjangoValidationError as exc:
                raise serializers.ValidationError({"attachment": exc.messages}) from exc

        appointment_id = attrs.get("appointment_id")
        if appointment_id is not None:
            appointment = Appointment.objects.filter(
                pk=appointment_id,
                doctor=doctor,
                patient=patient,
            ).first()
            if appointment is None:
                raise serializers.ValidationError(
                    {"appointment_id": "The appointment must belong to this doctor and patient."}
                )
            attrs["appointment"] = appointment

        medical_record_id = attrs.get("medical_record_id")
        if medical_record_id is not None:
            record = MedicalRecord.objects.filter(pk=medical_record_id, patient=patient).first()
            if record is None:
                raise serializers.ValidationError(
                    {"medical_record_id": "The medical record must belong to this patient."}
                )
            if record.doctor_id not in (None, doctor.id):
                raise serializers.ValidationError(
                    {"medical_record_id": "The medical record belongs to another doctor."}
                )
            attrs["medical_record"] = record
        return attrs


def _user_display_name(user):
    name = f"{user.first_name} {user.last_name}".strip()
    return name or user.email
