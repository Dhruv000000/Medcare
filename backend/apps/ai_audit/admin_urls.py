from django.urls import path

from .views import AdminAiAuditSummaryView

urlpatterns = [
    path("summary/", AdminAiAuditSummaryView.as_view(), name="admin-ai-audit-summary"),
]
