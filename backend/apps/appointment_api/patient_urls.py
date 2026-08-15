from django.urls import path

from .views import PatientAppointmentCancelView, PatientAppointmentDetailView, PatientAppointmentsView, PatientDoctorDirectoryView


urlpatterns = [
    path("doctors/", PatientDoctorDirectoryView.as_view(), name="patient-doctors"),
    path("appointments/", PatientAppointmentsView.as_view(), name="patient-appointments"),
    path("appointments/<int:appointment_id>/", PatientAppointmentDetailView.as_view(), name="patient-appointment-detail"),
    path("appointments/<int:appointment_id>/cancel/", PatientAppointmentCancelView.as_view(), name="patient-appointment-cancel"),
]
