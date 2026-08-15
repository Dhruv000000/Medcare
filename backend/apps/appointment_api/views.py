from datetime import datetime

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import DoctorProfile, PatientProfile, User
from apps.accounts.permissions import IsDoctor, IsPatient
from apps.appointments.models import Appointment

from .serializers import (
    AppointmentSerializer,
    AppointmentTransitionSerializer,
    DoctorDashboardSerializer,
    DoctorDirectorySerializer,
    DoctorProfileSerializer,
    PatientAppointmentCreateSerializer,
)


ACTIVE_STATUSES = [
    Appointment.Status.PENDING,
    Appointment.Status.CONFIRMED,
]


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


def apply_appointment_filters(queryset, request):
    status_filter = request.query_params.get("status")
    scope = request.query_params.get("scope")
    valid_statuses = {choice.value for choice in Appointment.Status}
    if status_filter:
        if status_filter not in valid_statuses:
            return None, Response({"status": "Invalid appointment status."}, status=status.HTTP_400_BAD_REQUEST)
        queryset = queryset.filter(status=status_filter)

    today = timezone.localdate()
    if scope == "today":
        queryset = queryset.filter(scheduled_date=today)
    elif scope == "upcoming":
        queryset = queryset.filter(scheduled_date__gte=today, status__in=ACTIVE_STATUSES)
    elif scope == "past":
        queryset = queryset.filter(scheduled_date__lt=today)
    elif scope:
        return None, Response({"scope": "Use today, upcoming, or past."}, status=status.HTTP_400_BAD_REQUEST)
    return queryset, None


def get_owned_appointment(appointment_id, owner_field, owner):
    filters = {"pk": appointment_id, owner_field: owner}
    return Appointment.objects.select_related("patient__user", "doctor__user").filter(**filters).first()


def conflict_exists(patient, doctor, scheduled_date, scheduled_time):
    return Appointment.objects.filter(
        Q(doctor=doctor) | Q(patient=patient),
        scheduled_date=scheduled_date,
        scheduled_time=scheduled_time,
        status__in=ACTIVE_STATUSES,
    ).exists()


class DoctorProfileView(DoctorAccessMixin, APIView):
    def get(self, request):
        doctor = self.get_doctor(request)
        if doctor is None:
            return Response({"detail": "Doctor profile is not available."}, status=status.HTTP_403_FORBIDDEN)
        return Response(DoctorProfileSerializer(doctor).data)


class DoctorDashboardView(DoctorAccessMixin, APIView):
    def get(self, request):
        doctor = self.get_doctor(request)
        if doctor is None:
            return Response({"detail": "Doctor profile is not available."}, status=status.HTTP_403_FORBIDDEN)
        appointments = Appointment.objects.select_related("patient__user", "doctor__user").filter(doctor=doctor)
        today = timezone.localdate()
        authorized_patients = []
        seen_patient_ids = set()
        for appointment in appointments.order_by("-scheduled_date", "-scheduled_time"):
            patient = appointment.patient
            if patient.pk in seen_patient_ids:
                continue
            seen_patient_ids.add(patient.pk)
            date_of_birth = patient.user.date_of_birth
            age = None
            if date_of_birth:
                age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            authorized_patients.append(
                {
                    "patient_id": patient.pk,
                    "patient_name": f"{patient.user.first_name} {patient.user.last_name}".strip(),
                    "age": age,
                    "condition": appointment.reason or "Appointment",
                    "last_visit": appointment.scheduled_date,
                    "status": appointment.get_status_display(),
                }
            )
        data = {
            "doctor": doctor,
            "pending_count": appointments.filter(status=Appointment.Status.PENDING).count(),
            "confirmed_count": appointments.filter(status=Appointment.Status.CONFIRMED).count(),
            "today_count": appointments.filter(scheduled_date=today, status__in=ACTIVE_STATUSES).count(),
            "completed_count": appointments.filter(status=Appointment.Status.COMPLETED).count(),
            "upcoming_count": appointments.filter(scheduled_date__gte=today, status__in=ACTIVE_STATUSES).count(),
            "patient_count": len(authorized_patients),
            "authorized_patients": authorized_patients,
            "today_appointments": appointments.filter(scheduled_date=today).order_by("scheduled_time"),
        }
        return Response(DoctorDashboardSerializer(data).data)


class PatientDoctorDirectoryView(PatientAccessMixin, APIView):
    def get(self, request):
        if self.get_patient(request) is None:
            return Response({"detail": "Patient profile is not available."}, status=status.HTTP_403_FORBIDDEN)
        doctors = DoctorProfile.objects.select_related("user").filter(
            user__role=User.Role.DOCTOR,
            user__is_active=True,
        ).order_by("user__last_name", "user__first_name")
        return Response(DoctorDirectorySerializer(doctors, many=True).data)


class PatientAppointmentsView(PatientAccessMixin, APIView):
    def get(self, request):
        patient = self.get_patient(request)
        if patient is None:
            return Response({"detail": "Patient profile is not available."}, status=status.HTTP_403_FORBIDDEN)
        queryset, error = apply_appointment_filters(
            Appointment.objects.select_related("patient__user", "doctor__user").filter(patient=patient),
            request,
        )
        if error:
            return error
        return Response(AppointmentSerializer(queryset, many=True).data)

    def post(self, request):
        patient = self.get_patient(request)
        if patient is None:
            return Response({"detail": "Patient profile is not available."}, status=status.HTTP_403_FORBIDDEN)
        serializer = PatientAppointmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor = serializer.validated_data["doctor"]
        scheduled_date = serializer.validated_data["scheduled_date"]
        scheduled_time = serializer.validated_data["scheduled_time"]
        if conflict_exists(patient, doctor, scheduled_date, scheduled_time):
            return Response({"detail": "That appointment time is unavailable."}, status=status.HTTP_409_CONFLICT)
        try:
            with transaction.atomic():
                appointment = Appointment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    scheduled_date=scheduled_date,
                    scheduled_time=scheduled_time,
                    status=Appointment.Status.PENDING,
                    reason=serializer.validated_data.get("reason", ""),
                )
        except IntegrityError:
            return Response({"detail": "That appointment time is unavailable."}, status=status.HTTP_409_CONFLICT)
        appointment = Appointment.objects.select_related("patient__user", "doctor__user").get(pk=appointment.pk)
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)


class PatientAppointmentDetailView(PatientAccessMixin, APIView):
    def get(self, request, appointment_id):
        patient = self.get_patient(request)
        if patient is None:
            return Response({"detail": "Patient profile is not available."}, status=status.HTTP_403_FORBIDDEN)
        appointment = get_owned_appointment(appointment_id, "patient", patient)
        if appointment is None:
            return Response({"detail": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(AppointmentSerializer(appointment).data)


class PatientAppointmentCancelView(PatientAccessMixin, APIView):
    def post(self, request, appointment_id):
        patient = self.get_patient(request)
        if patient is None:
            return Response({"detail": "Patient profile is not available."}, status=status.HTTP_403_FORBIDDEN)
        appointment = get_owned_appointment(appointment_id, "patient", patient)
        if appointment is None:
            return Response({"detail": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
        if appointment.status not in {Appointment.Status.PENDING, Appointment.Status.CONFIRMED}:
            return Response({"detail": "This appointment cannot be cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=["status", "updated_at"])
        return Response(AppointmentSerializer(appointment).data)


class DoctorAppointmentsView(DoctorAccessMixin, APIView):
    def get(self, request):
        doctor = self.get_doctor(request)
        if doctor is None:
            return Response({"detail": "Doctor profile is not available."}, status=status.HTTP_403_FORBIDDEN)
        queryset, error = apply_appointment_filters(
            Appointment.objects.select_related("patient__user", "doctor__user").filter(doctor=doctor),
            request,
        )
        if error:
            return error
        return Response(AppointmentSerializer(queryset, many=True).data)


class DoctorAppointmentDetailView(DoctorAccessMixin, APIView):
    def get(self, request, appointment_id):
        doctor = self.get_doctor(request)
        if doctor is None:
            return Response({"detail": "Doctor profile is not available."}, status=status.HTTP_403_FORBIDDEN)
        appointment = get_owned_appointment(appointment_id, "doctor", doctor)
        if appointment is None:
            return Response({"detail": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(AppointmentSerializer(appointment).data)


class DoctorAppointmentTransitionView(DoctorAccessMixin, APIView):
    def post(self, request, appointment_id):
        doctor = self.get_doctor(request)
        if doctor is None:
            return Response({"detail": "Doctor profile is not available."}, status=status.HTTP_403_FORBIDDEN)
        appointment = get_owned_appointment(appointment_id, "doctor", doctor)
        if appointment is None:
            return Response({"detail": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AppointmentTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data["action"]
        allowed = {
            Appointment.Status.PENDING: {
                "confirm": Appointment.Status.CONFIRMED,
                "reject": Appointment.Status.REJECTED,
                "cancel": Appointment.Status.CANCELLED,
            },
            Appointment.Status.CONFIRMED: {
                "cancel": Appointment.Status.CANCELLED,
                "complete": Appointment.Status.COMPLETED,
            },
        }
        next_status = allowed.get(appointment.status, {}).get(action)
        if next_status is None:
            return Response(
                {"detail": f"Cannot {action} an appointment in {appointment.status} state."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        appointment.status = next_status
        appointment.save(update_fields=["status", "updated_at"])
        return Response(AppointmentSerializer(appointment).data)
