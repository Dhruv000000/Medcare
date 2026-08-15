from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AI_API = ROOT / "backend" / "apps" / "ai_api"
ARTIFACT = ROOT / "ai" / "models" / "artifacts" / "uci-heart-disease-logreg-v1.0.0.joblib"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


checks: dict[str, object] = {}
urls = read(AI_API / "urls.py")
checks["single_ai_route"] = urls.count("heart-risk/predict/") == 1
checks["no_csrf_exempt"] = not any("csrf_exempt" in read(path) for path in AI_API.glob("*.py"))
checks["no_frontend_backend_model_artifacts"] = not any(
    path.suffix.lower() in {".joblib", ".pkl", ".onnx", ".pt", ".h5"}
    for base in (ROOT / "frontend", ROOT / "backend")
    for path in base.rglob("*")
    if path.is_file() and "venv" not in path.parts and "__pycache__" not in path.parts
)
requirements = read(ROOT / "backend" / "requirements.txt")
checks["all_backend_dependencies_pinned"] = all(
    (not line.strip() or line.lstrip().startswith("#") or "==" in line)
    for line in requirements.splitlines()
)
runtime_text = "\n".join(
    read(path)
    for path in AI_API.glob("*.py")
    if path.name not in {"tests.py", "apps.py"}
)
checks["no_runtime_secrets"] = not bool(
    re.search(
        r"sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA|OPENSSH|EC) PRIVATE KEY-----|api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_-]{16,}",
        runtime_text,
    )
)
checks["no_patient_data_history_retraining_external_ai"] = not bool(
    re.search(
        r"PatientProfile|MedicalRecord|Prescription|Appointment|prediction_history|PredictionHistory|fit\(|fit_transform|api/chat|openai|gemini|claude|huggingface",
        runtime_text,
        flags=re.IGNORECASE,
    )
)
patient_js = read(ROOT / "frontend" / "js" / "patient" / "patient-ai-insights.js")
checks["patient_ai_denial_no_prediction_or_storage"] = not bool(
    re.search(r"heart-risk/predict|sessionStorage|document\\.write|innerHTML", patient_js)
)
doctor_js = read(ROOT / "frontend" / "js" / "doctor" / "doctor-dashboard.js")
ai_block = doctor_js.split("const AI_ENDPOINT =", 1)[1].split("document.addEventListener('DOMContentLoaded', loadDoctorDashboard);", 1)[0]
checks["doctor_ai_safe_rendering_and_transient_state"] = not bool(
    re.search(r"innerHTML|insertAdjacentHTML|document\\.write|localStorage|sessionStorage|patient_id|medical_records|prescriptions|appointments|diagnosis|prescription|treatment|emergency", ai_block)
)
checks["artifact_sha256"] = sha256(ARTIFACT) == "e548527e51c67a7b611501acc844b367cecdde53413e33914ed9757fb9bae6cd"
checks["all_checks_pass"] = all(bool(value) for value in checks.values())
print(json.dumps(checks, sort_keys=True))
if not checks["all_checks_pass"]:
    raise SystemExit(1)
