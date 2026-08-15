from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
artifact = ROOT / "ai/models/artifacts/uci-heart-disease-logreg-v1.0.0.joblib"
expected = "e548527e51c67a7b611501acc844b367cecdde53413e33914ed9757fb9bae6cd"

def read(path):
    return (ROOT / path).read_text(encoding="utf-8", errors="ignore")

model = read("backend/apps/ai_audit/models.py")
service = read("backend/apps/ai_audit/services.py")
views = read("backend/apps/ai_audit/views.py")
serializers = read("backend/apps/ai_audit/serializers.py")
urls = read("backend/apps/ai_audit/urls.py")
admin_urls = read("backend/apps/ai_audit/admin_urls.py")
ai_view = read("backend/apps/ai_api/views.py")
root_urls = read("backend/config/urls.py")
doctor_js = read("frontend/js/doctor/doctor-dashboard.js")
doctor_html = read("frontend/pages/doctor/doctor-dashboard.html")
patient_ai = read("frontend/js/patient/patient-ai-insights.js")

checks = {
    "model_checksum_preserved": artifact.is_file() and hashlib.sha256(artifact.read_bytes()).hexdigest() == expected,
    "single_prediction_route": read("backend/apps/ai_api/urls.py").count("heart-risk/predict/") == 1,
    "phase25_app_registered": "apps.ai_audit" in read("backend/config/settings.py"),
    "phase25_routes_registered": "apps.ai_audit.urls" in root_urls and "apps.ai_audit.admin_urls" in root_urls,
    "immutable_event_fields": all(token in model for token in ["editable=False", "def save", "def delete", "models.PROTECT"]),
    "event_minimization": all(token in service for token in ["minimize_explanation", '"contribution"', '"direction"']) and '"value"' not in service,
    "no_patient_or_raw_feature_fields": not any(token in model for token in ["patient_id", "patient =", "feature_payload", "request_payload", "raw_file"]),
    "server_owned_recording": all(token in ai_view for token in ["record_prediction_event", "VALIDATION_FAILED", "COMPLETED"]),
    "doctor_own_report_scope": all(token in views for token in ["requesting_user=request.user", "Status.COMPLETED", "role != \"doctor\""]),
    "admin_aggregate_only": all(token in views for token in ["IsAdministrator", "total_events", "completed_events", "rejected_events", "model_versions"]),
    "read_only_report_routes": "def post" not in views and "get(" in views,
    "safe_report_serialization": all(token in serializers for token in ["read_only_fields", "ACADEMIC_DISCLAIMER", "not diagnostic confidence"]),
    "no_patient_report_route": "patient" not in urls.lower(),
    "no_csrf_exempt": "csrf_exempt" not in ai_view and "csrf_exempt" not in views,
    "frontend_report_route": "'/api/ai/reports/'" in doctor_js,
    "frontend_safe_dom": all(token in doctor_js for token in ["textContent", "replaceChildren", "createElement"]),
    "frontend_no_storage_or_console": not any(token in doctor_js for token in ["localStorage", "sessionStorage", "console.log", "innerHTML"]),
    "patient_ai_denial_preserved": "/api/ai/heart-risk/predict/" not in patient_ai,
    "safety_language": all(token in doctor_js.lower() for token in ["not diagnostic confidence", "clinician remains responsible"]),
    "no_raw_sql": not any("cursor(" in read(path) or "raw(" in read(path) for path in ["backend/apps/ai_audit/views.py", "backend/apps/ai_audit/services.py"]),
    "no_phase24_storage_change": all((ROOT / path).is_file() for path in ["backend/apps/clinical_api/file_security.py", "backend/apps/medical_records/models.py", "backend/apps/reports/models.py"]),
}
result = {
    "phase": 25,
    "all_checks_passed": all(checks.values()),
    "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest() if artifact.is_file() else None,
    "ai_route_count": read("backend/apps/ai_api/urls.py").count("heart-risk/predict/"),
    "checks": checks,
}
print(json.dumps(result, indent=2, sort_keys=True))
raise SystemExit(0 if result["all_checks_passed"] else 1)
