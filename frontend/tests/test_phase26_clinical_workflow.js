const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..', '..');
const html = fs.readFileSync(path.join(root, 'frontend/pages/doctor/doctor-dashboard.html'), 'utf8');
const doctorJs = fs.readFileSync(path.join(root, 'frontend/js/doctor/doctor-dashboard.js'), 'utf8');
const patientJs = fs.readFileSync(path.join(root, 'frontend/js/patient/patient-ai-insights.js'), 'utf8');
const patientPrescriptionsJs = fs.readFileSync(path.join(root, 'frontend/js/patient/patient-prescriptions.js'), 'utf8');

for (const id of [
    'phase26ClinicalWorkflow', 'phase26ClinicalForm', 'phase26WorkflowType', 'phase26AppointmentId',
    'phase26RecordFields', 'phase26ReportFields', 'phase26PrescriptionFields', 'phase26WorkflowStatus',
    'phase26Submit', 'phase26Reset', 'phase26MedicalRecordId',
]) assert.match(html, new RegExp(`id="${id}"`));

assert.match(html, /role="status" aria-live="polite"/);
assert.match(html, /server re-checks patient, doctor, appointment, and record authorization/);
assert.match(doctorJs, /\/api\/doctor\/medical-records\//);
assert.match(doctorJs, /\/api\/doctor\/reports\//);
assert.match(doctorJs, /\/api\/doctor\/prescriptions\//);
assert.match(doctorJs, /patient_id: phase26CurrentPatientId/);
assert.match(doctorJs, /method: 'POST'/);
assert.match(doctorJs, /phase26Form\.dataset\.submitting/);
assert.match(doctorJs, /Saving…/);
assert.match(doctorJs, /response\.status === 401/);
assert.match(doctorJs, /response\.status === 403/);
assert.match(doctorJs, /phase26SetStatus/);
assert.match(doctorJs, /replaceChildren\(/);
assert.match(doctorJs, /textContent/);
assert.doesNotMatch(doctorJs, /innerHTML|insertAdjacentHTML|document\.write/);
assert.doesNotMatch(doctorJs, /localStorage|sessionStorage/);
assert.match(patientPrescriptionsJs, /replaceChildren\(/);
assert.match(patientPrescriptionsJs, /textContent/);
assert.doesNotMatch(patientPrescriptionsJs, /innerHTML|insertAdjacentHTML|document\.write/);
assert.doesNotMatch(patientJs, /heart-risk\/predict/);
assert.match(patientJs, /No prediction request was sent/);

console.log('phase26_clinical_workflow_frontend_contract=PASS');
console.log('phase26_existing_api_routes_reused=PASS');
console.log('phase26_safe_dom_and_auth_states=PASS');
console.log('phase26_patient_prescriptions_safe_dom=PASS');
console.log('phase26_patient_ai_denial_preserved=PASS');
