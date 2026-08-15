from django.urls import path

from .views import (
    DoctorAppointmentDetailView,
    DoctorAppointmentTransitionView,
    DoctorAppointmentsView,
    DoctorDashboardView,
    DoctorProfileView,
)


urlpatterns = [
    path("profile/", DoctorProfileView.as_view(), name="doctor-profile"),
    path("dashboard/", DoctorDashboardView.as_view(), name="doctor-dashboard"),
    path("appointments/", DoctorAppointmentsView.as_view(), name="doctor-appointments"),
    path("appointments/<int:appointment_id>/", DoctorAppointmentDetailView.as_view(), name="doctor-appointment-detail"),
    path("appointments/<int:appointment_id>/transition/", DoctorAppointmentTransitionView.as_view(), name="doctor-appointment-transition"),
]
