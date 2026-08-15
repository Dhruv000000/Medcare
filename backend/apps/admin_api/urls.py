from django.urls import path

from .views import (
    AdminAppointmentsView,
    AdminDashboardView,
    AdminDoctorDetailView,
    AdminDoctorsView,
    AdminPatientDetailView,
    AdminPatientsView,
    AdminProfileView,
    AdminUserStatusView,
)

urlpatterns = [
    path("dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("patients/", AdminPatientsView.as_view(), name="admin-patients"),
    path("patients/<int:patient_id>/", AdminPatientDetailView.as_view(), name="admin-patient-detail"),
    path("doctors/", AdminDoctorsView.as_view(), name="admin-doctors"),
    path("doctors/<int:doctor_id>/", AdminDoctorDetailView.as_view(), name="admin-doctor-detail"),
    path("appointments/", AdminAppointmentsView.as_view(), name="admin-appointments"),
    path("profile/", AdminProfileView.as_view(), name="admin-profile"),
    path("users/<int:user_id>/status/", AdminUserStatusView.as_view(), name="admin-user-status"),
]
