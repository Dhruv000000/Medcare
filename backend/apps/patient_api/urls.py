from django.urls import path

from .views import PatientDashboardView, PatientProfileView, PatientSettingsView


urlpatterns = [
    path("profile/", PatientProfileView.as_view(), name="patient-profile"),
    path("settings/", PatientSettingsView.as_view(), name="patient-settings"),
    path("dashboard/", PatientDashboardView.as_view(), name="patient-dashboard"),
]
