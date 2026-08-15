"""Root URL configuration for the MediCare backend foundation."""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(url="/pages/public/index.html", permanent=False)),
    path("admin/", admin.site.urls),
    path("api/", include("apps.health.urls")),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/patient/", include("apps.patient_api.urls")),
    path("api/patient/", include("apps.appointment_api.patient_urls")),
    path("api/patient/", include("apps.clinical_api.patient_urls")),
    path("api/doctor/", include("apps.appointment_api.doctor_urls")),
    path("api/doctor/", include("apps.clinical_api.doctor_urls")),
    path("api/admin/", include("apps.admin_api.urls")),
    path("api/admin/ai-audit/", include("apps.ai_audit.admin_urls")),
    path("api/ai/", include("apps.ai_api.urls")),
    path("api/ai/", include("apps.ai_audit.urls")),
]
