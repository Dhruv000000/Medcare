const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const doctorHtml = fs.readFileSync(path.join(root, 'pages/doctor/doctor-dashboard.html'), 'utf8');
const doctorJs = fs.readFileSync(path.join(root, 'js/doctor/doctor-dashboard.js'), 'utf8');
const doctorCss = fs.readFileSync(path.join(root, 'css/doctor/doctor-dashboard.css'), 'utf8');
const patientAi = fs.readFileSync(path.join(root, 'js/patient/patient-ai-insights.js'), 'utf8');

function assert(condition, message) {
    if (!condition) throw new Error(message);
}

assert(doctorHtml.includes('id="viewAiReportsButton"'), 'Phase 25 report button missing');
assert(doctorHtml.includes('id="aiReportsList"'), 'Phase 25 report list missing');
assert(doctorHtml.includes('Patient prediction history is not available'), 'Patient-history boundary missing');
assert(doctorJs.includes("'/api/ai/reports/'"), 'Protected report route missing');
assert(doctorJs.includes('renderAiReport'), 'Safe report renderer missing');
assert(doctorJs.includes('textContent'), 'Report renderer must use textContent');
assert(doctorJs.includes('replaceChildren'), 'Report list must be cleared safely');
assert(!doctorJs.includes('localStorage') && !doctorJs.includes('sessionStorage'), 'Report data must not use browser storage');
assert(!doctorJs.includes('console.log') && !doctorJs.includes('innerHTML'), 'Report data must not use console logging or unsafe HTML');
assert(doctorJs.includes('not diagnostic confidence'), 'Probability safety wording missing');
assert(doctorJs.includes('clinician remains responsible'), 'Clinician-responsibility wording missing');
assert(doctorCss.includes('.ai-reports-panel'), 'Report panel styles missing');
assert(doctorCss.includes('.ai-report-card'), 'Report card styles missing');
assert(!patientAi.includes('/api/ai/heart-risk/predict/'), 'Patient AI denial must remain intact');

console.log('phase25_ai_reporting_frontend_contract=PASS');
console.log('phase25_authorized_report_route=PASS');
console.log('phase25_safe_dom_and_privacy=PASS');
console.log('phase25_patient_ai_denial=PASS');
