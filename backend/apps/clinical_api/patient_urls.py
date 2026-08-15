from django.urls import path

from .views import (
    PatientMedicalRecordDownloadView,
    PatientMedicalRecordsView,
    PatientPrescriptionsView,
    PatientReportDownloadView,
    PatientReportsView,
)


urlpatterns = [
    path("medical-records/", PatientMedicalRecordsView.as_view(), name="patient-medical-records"),
    path("medical-records/<int:pk>/download/", PatientMedicalRecordDownloadView.as_view(), name="patient-medical-record-download"),
    path("prescriptions/", PatientPrescriptionsView.as_view(), name="patient-prescriptions"),
    path("reports/", PatientReportsView.as_view(), name="patient-reports"),
    path("reports/<int:pk>/download/", PatientReportDownloadView.as_view(), name="patient-report-download"),
]
