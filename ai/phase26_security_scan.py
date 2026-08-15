from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / 'ai/models/artifacts/uci-heart-disease-logreg-v1.0.0.joblib'
DOCTOR_JS = ROOT / 'frontend/js/doctor/doctor-dashboard.js'
DOCTOR_HTML = ROOT / 'frontend/pages/doctor/doctor-dashboard.html'
PATIENT_AI = ROOT / 'frontend/js/patient/patient-ai-insights.js'
CLINICAL_VIEWS = ROOT / 'backend/apps/clinical_api/views.py'
CLINICAL_SERIALIZERS = ROOT / 'backend/apps/clinical_api/serializers.py'
AI_URLS = ROOT / 'backend/apps/ai_api/urls.py'


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


doctor_js = read(DOCTOR_JS)
doctor_html = read(DOCTOR_HTML)
patient_ai = read(PATIENT_AI)
clinical_text = read(CLINICAL_VIEWS) + '\n' + read(CLINICAL_SERIALIZERS)
checks = {
    'phase26_panel_and_form': all(token in doctor_html for token in ['phase26ClinicalWorkflow', 'phase26ClinicalForm', 'phase26WorkflowStatus', 'phase26Submit']),
    'existing_clinical_routes_reused': all(token in doctor_js for token in ['/api/doctor/medical-records/', '/api/doctor/reports/', '/api/doctor/prescriptions/']),
    'server_authorization_preserved': all(token in clinical_text for token in ['Appointment.objects.filter', 'This patient is not authorized for this doctor', 'The appointment must belong to this doctor and patient']),
    'safe_dom_no_unsafe_html': not bool(re.search(r'innerHTML|insertAdjacentHTML|document\.write', doctor_js)),
    'no_browser_storage_or_console': not bool(re.search(r'localStorage|sessionStorage|console\.', doctor_js)),
    'patient_ai_denial_preserved': not bool(re.search(r'heart-risk/predict|apiRequest|fetch\s*\(', patient_ai)) and 'No prediction request was sent' in patient_ai,
    'single_ai_route': read(AI_URLS).count('heart-risk/predict/') == 1,
    'model_checksum_preserved': sha256(ARTIFACT) == 'e548527e51c67a7b611501acc844b367cecdde53413e33914ed9757fb9bae6cd',
    'no_phase26_model_or_endpoint': not any(path.name.lower().startswith(('phase26_model', 'phase26_ai')) for path in (ROOT / 'ai').rglob('*') if path.is_file()),
    'no_new_schema_required': not (ROOT / 'backend/apps/phase26').exists(),
    'form_server_owned_patient': 'patient_id: phase26CurrentPatientId' in doctor_js,
    'csrf_session_wrapper_used': 'apiRequest(request.endpoint' in doctor_js,
    'unauthorized_state': 'response.status === 401' in doctor_js and 'response.status === 403' in doctor_js,
    'loading_success_error_states': all(token in doctor_js for token in ['Saving…', 'Clinical entry saved.', 'phase26SetStatus(error.message']),
}
checks['all_checks_passed'] = all(checks.values())
result = {'phase': 26, 'checks': checks, 'all_checks_passed': checks['all_checks_passed'], 'ai_route_count': read(AI_URLS).count('heart-risk/predict/'), 'artifact_sha256': sha256(ARTIFACT)}
print(json.dumps(result, indent=2, sort_keys=True))
raise SystemExit(0 if result['all_checks_passed'] else 1)
