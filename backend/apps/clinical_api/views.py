from django.db import transaction
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import DoctorProfile, PatientProfile
from apps.accounts.permissions import IsDoctor, IsPatient
from apps.appointments.models import Appointment
from apps.medical_records.models import MedicalRecord
from apps.prescriptions.models import Prescription, PrescriptionItem
from apps.reports.models import MedicalReport, ReportFinding

from .file_security import sanitize_original_filename
from .serializers import (
    DoctorMedicalRecordCreateSerializer,
    DoctorPrescriptionCreateSerializer,
    DoctorReportCreateSerializer,
    MedicalRecordSerializer,
    MedicalReportSerializer,
    PrescriptionSerializer,
)


class PatientAccessMixin:
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsPatient]

    def get_patient(self, request):
        try:
            return request.user.patient_profile
        except PatientProfile.DoesNotExist:
            return None


class DoctorAccessMixin:
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_doctor(self, request):
        try:
            return request.user.doctor_profile
        except DoctorProfile.DoesNotExist:
            return None


def _patient_error():
    return Response(
        {"detail": "Patient profile is not available."},
        status=status.HTTP_403_FORBIDDEN,
    )


def _doctor_error():
    return Response(
        {"detail": "Doctor profile is not available."},
        status=status.HTTP_403_FORBIDDEN,
    )


def _doctor_scope(queryset, doctor):
    return queryset.filter(Q(doctor=doctor) | Q(patient__appointments__doctor=doctor)).distinct()


def _patient_filter(queryset, request):
    patient_id = request.query_params.get("patient_id")
    if patient_id:
        return queryset.filter(patient_id=patient_id)
    return queryset


class PatientMedicalRecordsView(PatientAccessMixin, APIView):
    def get(self, request):
        patient = self.get_patient(request)
        if patient is None:
            return _patient_error()
        records = MedicalRecord.objects.select_related(
            "patient__user",
            "doctor__user",
            "appointment",
        ).filter(patient=patient)
        return Response(MedicalRecordSerializer(records, many=True).data)


class PatientPrescriptionsView(PatientAccessMixin, APIView):
    def get(self, request):
        patient = self.get_patient(request)
        if patient is None:
            return _patient_error()
        prescriptions = Prescription.objects.select_related(
            "patient__user",
            "doctor__user",
        ).prefetch_related("items").filter(patient=patient)
        return Response(PrescriptionSerializer(prescriptions, many=True).data)


class PatientReportsView(PatientAccessMixin, APIView):
    def get(self, request):
        patient = self.get_patient(request)
        if patient is None:
            return _patient_error()
        reports = MedicalReport.objects.select_related(
            "patient__user",
            "doctor__user",
            "appointment",
            "medical_record",
        ).prefetch_related("findings").filter(patient=patient)
        return Response(MedicalReportSerializer(reports, many=True).data)


class DoctorMedicalRecordsView(DoctorAccessMixin, APIView):
    def get(self, request):
        doctor = self.get_doctor(request)
        if doctor is None:
            return _doctor_error()
        records = _patient_filter(
            _doctor_scope(
                MedicalRecord.objects.select_related(
                    "patient__user",
                    "doctor__user",
                    "appointment",
                ),
                doctor,
            ),
            request,
        )
        return Response(MedicalRecordSerializer(records, many=True).data)

    def post(self, request):
        doctor = self.get_doctor(request)
        if doctor is None:
            return _doctor_error()
        serializer = DoctorMedicalRecordCreateSerializer(
            data=request.data,
            context={"doctor": doctor},
        )
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        attachment = validated.pop("attachment", None)
        attachment_metadata = validated.pop("attachment_metadata", {})
        record = MedicalRecord.objects.create(
            patient=validated["patient_id"],
            doctor=doctor,
            appointment=validated.get("appointment"),
            record_type=validated["record_type"],
            occurred_on=validated["occurred_on"],
            diagnosis=validated["diagnosis"],
            notes=validated.get("notes", ""),
            attachment=attachment,
            attachment_original_name=attachment_metadata.get("original_name", ""),
            attachment_content_type=attachment_metadata.get("content_type", ""),
            attachment_size=attachment_metadata.get("size"),
        )
        record = MedicalRecord.objects.select_related(
            "patient__user",
            "doctor__user",
            "appointment",
        ).get(pk=record.pk)
        return Response(MedicalRecordSerializer(record).data, status=status.HTTP_201_CREATED)


class DoctorPrescriptionsView(DoctorAccessMixin, APIView):
    def get(self, request):
        doctor = self.get_doctor(request)
        if doctor is None:
            return _doctor_error()
        prescriptions = _patient_filter(
            _doctor_scope(
                Prescription.objects.select_related("patient__user", "doctor__user").prefetch_related("items"),
                doctor,
            ),
            request,
        )
        return Response(PrescriptionSerializer(prescriptions, many=True).data)

    def post(self, request):
        doctor = self.get_doctor(request)
        if doctor is None:
            return _doctor_error()
        serializer = DoctorPrescriptionCreateSerializer(
            data=request.data,
            context={"doctor": doctor},
        )
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        with transaction.atomic():
            prescription = Prescription.objects.create(
                patient=validated["patient_id"],
                doctor=doctor,
                status=validated["status"],
                issued_on=validated["issued_on"],
                start_date=validated["start_date"],
                end_date=validated.get("end_date"),
            )
            PrescriptionItem.objects.bulk_create(
                [
                    PrescriptionItem(prescription=prescription, **item)
                    for item in validated["items"]
                ]
            )
        prescription = Prescription.objects.select_related(
            "patient__user",
            "doctor__user",
        ).prefetch_related("items").get(pk=prescription.pk)
        return Response(PrescriptionSerializer(prescription).data, status=status.HTTP_201_CREATED)


class DoctorReportsView(DoctorAccessMixin, APIView):
    def get(self, request):
        doctor = self.get_doctor(request)
        if doctor is None:
            return _doctor_error()
        reports = _patient_filter(
            _doctor_scope(
                MedicalReport.objects.select_related(
                    "patient__user",
                    "doctor__user",
                    "appointment",
                    "medical_record",
                ).prefetch_related("findings"),
                doctor,
            ),
            request,
        )
        return Response(MedicalReportSerializer(reports, many=True).data)

    def post(self, request):
        doctor = self.get_doctor(request)
        if doctor is None:
            return _doctor_error()
        serializer = DoctorReportCreateSerializer(
            data=request.data,
            context={"doctor": doctor},
        )
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        findings = validated.pop("findings", [])
        patient = validated.pop("patient_id")
        validated.pop("appointment_id", None)
        validated.pop("medical_record_id", None)
        appointment = validated.pop("appointment", None)
        medical_record = validated.pop("medical_record", None)
        attachment = validated.pop("attachment", None)
        attachment_metadata = validated.pop("attachment_metadata", {})
        with transaction.atomic():
            report = MedicalReport.objects.create(
                patient=patient,
                doctor=doctor,
                appointment=appointment,
                medical_record=medical_record,
                attachment=attachment,
                attachment_original_name=attachment_metadata.get("original_name", ""),
                attachment_content_type=attachment_metadata.get("content_type", ""),
                attachment_size=attachment_metadata.get("size"),
                **validated,
            )
            ReportFinding.objects.bulk_create(
                [ReportFinding(report=report, **finding) for finding in findings]
            )
        report = MedicalReport.objects.select_related(
            "patient__user",
            "doctor__user",
            "appointment",
            "medical_record",
        ).prefetch_related("findings").get(pk=report.pk)
        return Response(MedicalReportSerializer(report).data, status=status.HTTP_201_CREATED)



def _doctor_can_access_object(obj, doctor):
    return obj.doctor_id == doctor.id or Appointment.objects.filter(
        doctor=doctor,
        patient_id=obj.patient_id,
    ).exists()


def _protected_file_response(obj):
    if not obj.attachment:
        return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)
    try:
        file_handle = obj.attachment.open("rb")
    except (FileNotFoundError, OSError, ValueError):
        return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)

    filename = sanitize_original_filename(
        obj.attachment_original_name or obj.attachment.name.rsplit("/", 1)[-1]
    )
    response = FileResponse(
        file_handle,
        as_attachment=True,
        filename=filename,
        content_type=obj.attachment_content_type or "application/octet-stream",
    )
    response["X-Content-Type-Options"] = "nosniff"
    return response


class PatientMedicalRecordDownloadView(PatientAccessMixin, APIView):
    def get(self, request, pk):
        patient = self.get_patient(request)
        if patient is None:
            return _patient_error()
        record = get_object_or_404(MedicalRecord, pk=pk, patient=patient)
        return _protected_file_response(record)


class PatientReportDownloadView(PatientAccessMixin, APIView):
    def get(self, request, pk):
        patient = self.get_patient(request)
        if patient is None:
            return _patient_error()
        report = get_object_or_404(MedicalReport, pk=pk, patient=patient)
        return _protected_file_response(report)


class DoctorMedicalRecordDownloadView(DoctorAccessMixin, APIView):
    def get(self, request, pk):
        doctor = self.get_doctor(request)
        if doctor is None:
            return _doctor_error()
        record = get_object_or_404(MedicalRecord, pk=pk)
        if not _doctor_can_access_object(record, doctor):
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)
        return _protected_file_response(record)


class DoctorReportDownloadView(DoctorAccessMixin, APIView):
    def get(self, request, pk):
        doctor = self.get_doctor(request)
        if doctor is None:
            return _doctor_error()
        report = get_object_or_404(MedicalReport, pk=pk)
        if not _doctor_can_access_object(report, doctor):
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)
        return _protected_file_response(report)
