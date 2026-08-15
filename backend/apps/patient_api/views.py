from django.db.models import Count, Q
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import PatientPreferences, PatientProfile, User
from apps.accounts.permissions import IsPatient
from apps.appointments.models import Appointment
from apps.medical_records.models import MedicalRecord
from apps.prescriptions.models import Prescription
from apps.reports.models import MedicalReport

from .serializers import PatientDashboardSerializer, PatientProfileSerializer, PatientSettingsSerializer


class PatientAccessMixin:
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsPatient]

    def get_patient(self, request):
        if request.user.role != User.Role.PATIENT:
            return None
        try:
            return request.user.patient_profile
        except PatientProfile.DoesNotExist:
            return None


class PatientProfileView(PatientAccessMixin, APIView):
    def get(self, request):
        patient = self.get_patient(request)
        if patient is None:
            return Response({"detail": "Patient profile is not available."}, status=status.HTTP_403_FORBIDDEN)
        return Response(PatientProfileSerializer(patient).data)

    def patch(self, request):
        patient = self.get_patient(request)
        if patient is None:
            return Response({"detail": "Patient profile is not available."}, status=status.HTTP_403_FORBIDDEN)
        serializer = PatientProfileSerializer(patient, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(PatientProfileSerializer(patient).data)

    def put(self, request):
        return self.patch(request)


class PatientSettingsView(PatientAccessMixin, APIView):
    def get(self, request):
        patient = self.get_patient(request)
        if patient is None:
            return Response({"detail": "Patient profile is not available."}, status=status.HTTP_403_FORBIDDEN)
        preferences, _ = PatientPreferences.objects.get_or_create(patient=patient)
        return Response(PatientSettingsSerializer(preferences).data)

    def patch(self, request):
        patient = self.get_patient(request)
        if patient is None:
            return Response({"detail": "Patient profile is not available."}, status=status.HTTP_403_FORBIDDEN)
        preferences, _ = PatientPreferences.objects.get_or_create(patient=patient)
        serializer = PatientSettingsSerializer(preferences, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(PatientSettingsSerializer(preferences).data)

    def put(self, request):
        return self.patch(request)


class PatientDashboardView(PatientAccessMixin, APIView):
    def get(self, request):
        patient = self.get_patient(request)
        if patient is None:
            return Response({"detail": "Patient profile is not available."}, status=status.HTTP_403_FORBIDDEN)

        appointments = Appointment.objects.select_related("doctor__user").filter(patient=patient)
        medical_records = MedicalRecord.objects.filter(patient=patient)
        prescriptions = Prescription.objects.filter(patient=patient)
        reports = MedicalReport.objects.filter(patient=patient)

        recent_activity = []
        for appointment in appointments.order_by("-scheduled_date", "-scheduled_time")[:6]:
            recent_activity.append(
                {
                    "activity_type": "appointment",
                    "title": f"Appointment {appointment.get_status_display().lower()}",
                    "subtitle": f"Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}".strip(),
                    "activity_date": appointment.scheduled_date,
                    "icon": "fa-calendar-check",
                }
            )
        for record in medical_records.order_by("-occurred_on", "-created_at")[:6]:
            recent_activity.append(
                {
                    "activity_type": "medical_record",
                    "title": "Medical record added",
                    "subtitle": record.diagnosis,
                    "activity_date": record.occurred_on,
                    "icon": "fa-file-medical",
                }
            )
        for prescription in prescriptions.order_by("-issued_on", "-created_at")[:6]:
            recent_activity.append(
                {
                    "activity_type": "prescription",
                    "title": "Prescription issued",
                    "subtitle": prescription.get_status_display(),
                    "activity_date": prescription.issued_on,
                    "icon": "fa-pills",
                }
            )
        for report in reports.order_by("-report_date", "-created_at")[:6]:
            recent_activity.append(
                {
                    "activity_type": "medical_report",
                    "title": "Medical report available",
                    "subtitle": report.title,
                    "activity_date": report.report_date,
                    "icon": "fa-chart-line",
                }
            )
        recent_activity.sort(key=lambda item: item["activity_date"], reverse=True)

        data = {
            "upcoming_appointment_count": appointments.filter(
                status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
            ).count(),
            "medical_record_count": medical_records.count(),
            "active_prescription_count": prescriptions.filter(
                status__in=[Prescription.Status.ACTIVE, Prescription.Status.REFILL_NEEDED],
            ).count(),
            "recent_activity": recent_activity[:6],
        }
        return Response(PatientDashboardSerializer(data).data)
