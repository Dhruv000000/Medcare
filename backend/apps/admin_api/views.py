from django.db.models import Q
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import DoctorProfile, PatientProfile, User
from apps.accounts.permissions import IsAdministrator
from apps.appointments.models import Appointment

from .serializers import (
    AdminAppointmentSerializer,
    AdminDashboardSerializer,
    AdminDoctorSerializer,
    AdminPatientSerializer,
    AdminProfileSerializer,
    AdminUserStatusResponseSerializer,
    AdminUserStatusSerializer,
)


class AdminAccessMixin:
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsAdministrator]


def parse_integer_filter(request, key):
    value = request.query_params.get(key)
    if value in (None, ""):
        return None, None
    try:
        return int(value), None
    except (TypeError, ValueError):
        return None, Response({key: "Enter a valid numeric identifier."}, status=status.HTTP_400_BAD_REQUEST)


class AdminDashboardView(AdminAccessMixin, APIView):
    def get(self, request):
        appointments = Appointment.objects.select_related(
            "patient__user", "doctor__user"
        )
        payload = {
            "total_patients": PatientProfile.objects.filter(user__role=User.Role.PATIENT).count(),
            "total_doctors": DoctorProfile.objects.filter(user__role=User.Role.DOCTOR).count(),
            "total_appointments": appointments.count(),
            "pending_appointments": appointments.filter(status=Appointment.Status.PENDING).count(),
            "completed_appointments": appointments.filter(status=Appointment.Status.COMPLETED).count(),
            "cancelled_appointments": appointments.filter(status=Appointment.Status.CANCELLED).count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "inactive_users": User.objects.filter(is_active=False).count(),
            "recent_appointments": appointments.order_by("-created_at", "-id")[:10],
        }
        return Response(AdminDashboardSerializer(payload).data)


class AdminPatientsView(AdminAccessMixin, APIView):
    def get(self, request):
        queryset = PatientProfile.objects.select_related("user").filter(
            user__role=User.Role.PATIENT
        )
        query = request.query_params.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(user__email__icontains=query)
                | Q(user__phone__icontains=query)
            )
        active = request.query_params.get("is_active")
        if active in {"true", "false"}:
            queryset = queryset.filter(user__is_active=active == "true")
        elif active:
            return Response(
                {"is_active": "Use true or false."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = queryset.order_by("user__last_name", "user__first_name", "id")
        return Response(AdminPatientSerializer(queryset, many=True).data)


class AdminPatientDetailView(AdminAccessMixin, APIView):
    def get(self, request, patient_id):
        patient = (
            PatientProfile.objects.select_related("user")
            .filter(pk=patient_id, user__role=User.Role.PATIENT)
            .first()
        )
        if patient is None:
            return Response({"detail": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(AdminPatientSerializer(patient).data)


class AdminDoctorsView(AdminAccessMixin, APIView):
    def get(self, request):
        queryset = DoctorProfile.objects.select_related("user").filter(
            user__role=User.Role.DOCTOR
        )
        query = request.query_params.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(user__email__icontains=query)
                | Q(user__phone__icontains=query)
                | Q(license_id__icontains=query)
                | Q(specialization__icontains=query)
            )
        active = request.query_params.get("is_active")
        if active in {"true", "false"}:
            queryset = queryset.filter(user__is_active=active == "true")
        elif active:
            return Response(
                {"is_active": "Use true or false."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = queryset.order_by("user__last_name", "user__first_name", "id")
        return Response(AdminDoctorSerializer(queryset, many=True).data)


class AdminDoctorDetailView(AdminAccessMixin, APIView):
    def get(self, request, doctor_id):
        doctor = (
            DoctorProfile.objects.select_related("user")
            .filter(pk=doctor_id, user__role=User.Role.DOCTOR)
            .first()
        )
        if doctor is None:
            return Response({"detail": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(AdminDoctorSerializer(doctor).data)


class AdminAppointmentsView(AdminAccessMixin, APIView):
    def get(self, request):
        queryset = Appointment.objects.select_related("patient__user", "doctor__user")
        status_filter = request.query_params.get("status")
        if status_filter:
            valid_statuses = {choice.value for choice in Appointment.Status}
            if status_filter not in valid_statuses:
                return Response(
                    {"status": "Invalid appointment status."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            queryset = queryset.filter(status=status_filter)

        patient_id, error = parse_integer_filter(request, "patient_id")
        if error:
            return error
        doctor_id, error = parse_integer_filter(request, "doctor_id")
        if error:
            return error
        if patient_id is not None:
            queryset = queryset.filter(patient_id=patient_id)
        if doctor_id is not None:
            queryset = queryset.filter(doctor_id=doctor_id)

        query = request.query_params.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(patient__user__first_name__icontains=query)
                | Q(patient__user__last_name__icontains=query)
                | Q(doctor__user__first_name__icontains=query)
                | Q(doctor__user__last_name__icontains=query)
                | Q(reason__icontains=query)
            )
        queryset = queryset.order_by("-scheduled_date", "-scheduled_time", "-id")
        return Response(AdminAppointmentSerializer(queryset, many=True).data)


class AdminProfileView(AdminAccessMixin, APIView):
    def get(self, request):
        return Response(AdminProfileSerializer(request.user).data)


class AdminUserStatusView(AdminAccessMixin, APIView):
    def patch(self, request, user_id):
        serializer = AdminUserStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target = User.objects.filter(pk=user_id).first()
        if target is None:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        if target.pk == request.user.pk:
            return Response(
                {"detail": "Administrators cannot change their own account status here."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if target.role == User.Role.ADMINISTRATOR:
            return Response(
                {"detail": "Administrator account status is managed outside this endpoint."},
                status=status.HTTP_403_FORBIDDEN,
            )
        target.is_active = serializer.validated_data["is_active"]
        target.save(update_fields=["is_active"])
        return Response(AdminUserStatusResponseSerializer(target).data)
