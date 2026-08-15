from django.urls import path

from .views import (
    DoctorMedicalRecordDownloadView,
    DoctorMedicalRecordsView,
    DoctorPrescriptionsView,
    DoctorReportDownloadView,
    DoctorReportsView,
)


urlpatterns = [
    path("medical-records/", DoctorMedicalRecordsView.as_view(), name="doctor-medical-records"),
    path("medical-records/<int:pk>/download/", DoctorMedicalRecordDownloadView.as_view(), name="doctor-medical-record-download"),
    path("prescriptions/", DoctorPrescriptionsView.as_view(), name="doctor-prescriptions"),
    path("reports/", DoctorReportsView.as_view(), name="doctor-reports"),
    path("reports/<int:pk>/download/", DoctorReportDownloadView.as_view(), name="doctor-report-download"),
]
