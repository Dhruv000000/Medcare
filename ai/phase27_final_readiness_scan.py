from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "ai/models/artifacts/uci-heart-disease-logreg-v1.0.0.joblib"
CHECKSUM = "e548527e51c67a7b611501acc844b367cecdde53413e33914ed9757fb9bae6cd"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_pins(path: Path) -> bool:
    lines = [line.strip() for line in read(path).splitlines() if line.strip() and not line.lstrip().startswith("#")]
    return bool(lines) and all("==" in line and not line.startswith(("-", "git+", "http://", "https://")) for line in lines)


settings = read(ROOT / "backend/config/settings.py")
urls = read(ROOT / "backend/apps/ai_api/urls.py")
clinical_views = read(ROOT / "backend/apps/clinical_api/views.py")
clinical_serializers = read(ROOT / "backend/apps/clinical_api/serializers.py")
clinical_js = read(ROOT / "frontend/js/doctor/doctor-dashboard.js")
patient_ai_js = read(ROOT / "frontend/js/patient/patient-ai-insights.js")
patient_prescriptions_js = read(ROOT / "frontend/js/patient/patient-prescriptions.js")
requirements = ROOT / "backend/requirements.txt"

required_docs = [
    ROOT / "docs/MEDICARE_PHASE_27_CURRENT_REQUIREMENT_MATRIX.md",
    ROOT / "docs/MEDICARE_FINAL_SRS_TRACEABILITY.md",
    ROOT / "docs/MEDICARE_PHASE_27_FINAL_COMPLETION_AUDIT.md",
    ROOT / "docs/PHASE27_CLINICAL_VALIDATION_READINESS.md",
    ROOT / "docs/PHASE27_DEPLOYMENT_READINESS.md",
]

checks = {
    "model_artifact_exists": ARTIFACT.is_file(),
    "model_checksum_preserved": ARTIFACT.is_file() and sha256(ARTIFACT) == CHECKSUM,
    "single_ai_route": urls.count("heart-risk/predict/") == 1,
    "no_forbidden_ai_features": not bool(re.search(r"chatbot|RAG|LLM|external.?AI|model.?upload|retrain", "\n".join([urls, clinical_views, clinical_js]), re.IGNORECASE)),
    "patient_ai_denial_preserved": "No prediction request was sent" in patient_ai_js and not bool(re.search(r"heart-risk/predict|apiRequest|fetch\s*\(", patient_ai_js)),
    "clinical_server_authorization": all(token in clinical_views + clinical_serializers for token in ["Appointment.objects.filter", "patient_id", "doctor"]),
    "doctor_workflow_uses_csrf_wrapper": "MediCareAuth.apiRequest" in clinical_js or "apiRequest(request.endpoint" in clinical_js,
    "clinical_js_no_unsafe_html": not bool(re.search(r"innerHTML|insertAdjacentHTML|document\.write", clinical_js)),
    "patient_prescription_js_no_unsafe_html": not bool(re.search(r"innerHTML|insertAdjacentHTML|document\.write", patient_prescriptions_js)),
    "no_raw_sql_in_clinical_api": not bool(re.search(r"\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b", clinical_views + clinical_serializers, re.IGNORECASE)),
    "csrf_not_exempt": "csrf_exempt" not in clinical_views + clinical_serializers,
    "production_secret_fail_closed": "DJANGO_SECRET_KEY must be set" in settings and "DEBUG must be false" in settings,
    "production_hosts_fail_closed": "ALLOWED_HOSTS must be set" in settings and "FRONTEND_ALLOWED_ORIGINS must be set" in settings,
    "secure_production_cookies_and_https": all(token in settings for token in ["SESSION_COOKIE_SECURE", "CSRF_COOKIE_SECURE", "SECURE_SSL_REDIRECT", "SECURE_HSTS_SECONDS"]),
    "database_fallback_explicit": "POSTGRES_CONFIGURED" in settings and "sqlite3" in settings and "postgresql" in settings,
    "dependencies_exactly_pinned": exact_pins(requirements),
    "required_phase27_docs_present": all(path.is_file() for path in required_docs),
    "runtime_database_absent": not (ROOT / "backend/db.sqlite3").exists(),
    "protected_media_smoke_files_absent": not any((ROOT / "backend/protected_media").rglob("*")) if (ROOT / "backend/protected_media").exists() else True,
}

matrix = read(ROOT / "docs/MEDICARE_PHASE_27_CURRENT_REQUIREMENT_MATRIX.md")
checks["matrix_reconciled_59_rows"] = "**Total** | **59**" in matrix and "Complete | 47" in matrix and "Partial | 6" in matrix and "Deferred | 2" in matrix and "Blocked | 3" in matrix
checks["external_boundaries_documented"] = all(token in matrix for token in ["CLINICAL VALIDATION REQUIRED", "PRODUCTION DEPLOYMENT REQUIRED", "Original external SRS absent"])
checks["all_checks_passed"] = all(checks.values())
result = {
    "phase": 27,
    "all_checks_passed": checks["all_checks_passed"],
    "artifact_sha256": sha256(ARTIFACT) if ARTIFACT.is_file() else None,
    "ai_route_count": urls.count("heart-risk/predict/"),
    "checks": checks,
}
print(json.dumps(result, indent=2, sort_keys=True))
raise SystemExit(0 if result["all_checks_passed"] else 1)
