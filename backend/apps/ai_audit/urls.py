from django.urls import path

from .views import (
    AdminAiAuditSummaryView,
    DoctorPredictionReportDetailView,
    DoctorPredictionReportListView,
)

urlpatterns = [
    path("reports/", DoctorPredictionReportListView.as_view(), name="ai-prediction-reports"),
    path("reports/<uuid:event_id>/", DoctorPredictionReportDetailView.as_view(), name="ai-prediction-report-detail"),
    path("admin-summary/", AdminAiAuditSummaryView.as_view(), name="ai-audit-admin-summary"),
]
