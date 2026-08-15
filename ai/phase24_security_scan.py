from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
ARTIFACT = ROOT / "ai/models/artifacts/uci-heart-disease-logreg-v1.0.0.joblib"
EXPECTED_HASH = "e548527e51c67a7b611501acc844b367cecdde53413e33914ed9757fb9bae6cd"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


checks: dict[str, bool] = {}
record_model = read(BACKEND / "apps/medical_records/models.py")
report_model = read(BACKEND / "apps/reports/models.py")
security = read(BACKEND / "apps/clinical_api/file_security.py")
views = read(BACKEND / "apps/clinical_api/views.py")
settings = read(BACKEND / "config/settings.py")
patient_urls = read(BACKEND / "apps/clinical_api/patient_urls.py")
doctor_urls = read(BACKEND / "apps/clinical_api/doctor_urls.py")
serializers = read(BACKEND / "apps/clinical_api/serializers.py")
patient_records = read(FRONTEND / "js/patient/patient-medical-records.js")
patient_reports = read(FRONTEND / "js/patient/patient-reports.js")
doctor_dashboard = read(FRONTEND / "js/doctor/doctor-dashboard.js")

checks["protected_upload_callable"] = "upload_to=protected_upload_to" in record_model and "upload_to=protected_upload_to" in report_model and "def protected_upload_to" in security
checks["protected_media_root"] = "MEDIA_ROOT = BASE_DIR / \"protected_media\"" in settings and "MEDIA_URL" not in settings
checks["bounded_upload_size"] = "MAX_UPLOAD_SIZE = 5 * 1024 * 1024" in security and "FILE_UPLOAD_MAX_MEMORY_SIZE" in settings
checks["conservative_allowlist"] = all(marker in security for marker in [".pdf", ".png", ".jpg", ".jpeg", ".txt"])
checks["signature_validation"] = all(marker in security for marker in ["_PDF_SIGNATURE", "_PNG_SIGNATURE", "_JPEG_SIGNATURE", "_signature_matches"])
checks["filename_sanitization"] = "Path(str(name or \"attachment\")).name" in security and "_UNSAFE_FILENAME_CHARS" in security
checks["safe_metadata_only"] = all(marker in serializers for marker in ["attachment_original_name", "attachment_content_type", "attachment_size"])
checks["download_routes"] = all(marker in patient_urls + doctor_urls for marker in ["/download/", "<int:pk>"])
checks["download_route_count"] = patient_urls.count("/download/") + doctor_urls.count("/download/") == 4
checks["object_authorization"] = "patient=patient" in views and "def _doctor_can_access_object" in views and "Appointment.objects.filter" in views
checks["protected_file_response"] = "FileResponse" in views and "X-Content-Type-Options" in views and "as_attachment=True" in views
checks["safe_errors"] = '"File not found."' in views
checks["csrf_not_exempt"] = "csrf_exempt" not in views and "csrf_exempt" not in serializers
checks["frontend_safe_dom"] = all("innerHTML" not in source and "insertAdjacentHTML" not in source for source in [patient_records, patient_reports, doctor_dashboard])
checks["frontend_download_allowlist"] = all(marker in patient_records + patient_reports + doctor_dashboard for marker in ["/download/", "response.blob()", "MediCareAuth.apiRequest"])
checks["frontend_no_clinical_console"] = all("console." not in source for source in [patient_records, patient_reports, doctor_dashboard])
checks["frontend_no_file_persistence"] = not any(re.search(r"(localStorage|sessionStorage)\.(setItem|getItem)\([^)]*(attachment|medical|report|record|file)", source, re.IGNORECASE) for source in [patient_records, patient_reports, doctor_dashboard])
checks["ai_checksum_preserved"] = ARTIFACT.is_file() and sha256(ARTIFACT) == EXPECTED_HASH
ai_urls = read(BACKEND / "apps/ai_api/urls.py")
checks["ai_route_scope"] = ai_urls.count("heart-risk/predict/") == 1
checks["no_public_media_route"] = "/media/" not in read(BACKEND / "config/urls.py")
checks["no_ai_source_touch"] = not any("phase24" in path.read_text(encoding="utf-8", errors="ignore").lower() for path in (BACKEND / "apps/ai_api").glob("*.py"))
checks["phase24_upload_validation_wired"] = "validate_uploaded_file" in serializers and "attachment_metadata" in views

result = {
    "phase": 24,
    "all_checks_passed": all(checks.values()),
    "artifact_sha256": sha256(ARTIFACT) if ARTIFACT.is_file() else None,
    "ai_route_count": ai_urls.count("heart-risk/predict/"),
    "download_route_count": patient_urls.count("/download/") + doctor_urls.count("/download/"),
    "checks": checks,
}
print(json.dumps(result, indent=2, sort_keys=True))
raise SystemExit(0 if result["all_checks_passed"] else 1)
