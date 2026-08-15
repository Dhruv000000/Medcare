const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..', '..');
const doctorHtml = fs.readFileSync(path.join(root, 'frontend/pages/doctor/doctor-dashboard.html'), 'utf8');
const doctorJs = fs.readFileSync(path.join(root, 'frontend/js/doctor/doctor-dashboard.js'), 'utf8');
const patientJs = fs.readFileSync(path.join(root, 'frontend/js/patient/patient-ai-insights.js'), 'utf8');
const patientHtml = fs.readFileSync(path.join(root, 'frontend/pages/patient/patient-ai-insights.html'), 'utf8');

const aiStart = doctorJs.indexOf("const AI_ENDPOINT =");
assert.notEqual(aiStart, -1);
const aiCode = doctorJs.slice(aiStart);

assert.match(doctorHtml, /id="aiButton"/);
assert.match(doctorHtml, /id="doctorAiForm"/);
assert.match(doctorHtml, /aria-describedby="aiFormNote"/);
assert.match(doctorHtml, /Model probability is an academic model output, not diagnostic confidence/);
assert.match(doctorHtml, /aria-controls="doctorAiForm"/);
assert.match(doctorHtml, /aria-expanded="false"/);
assert.match(doctorHtml, /not clinically validated/);
assert.match(doctorHtml, /not a diagnosis or medical advice/);
assert.match(doctorHtml, /id="aiPredictionResult"[^>]*role="status"[^>]*aria-live="polite"/);
assert.match(doctorHtml, /id="aiValidationMessage"[^>]*role="alert"[^>]*aria-live="polite"/);

const formStart = doctorHtml.indexOf('<form id="doctorAiForm"');
const formEnd = doctorHtml.indexOf('</form>', formStart);
assert.ok(formStart >= 0 && formEnd > formStart);
const formHtml = doctorHtml.slice(formStart, formEnd);
const expectedFields = [
    'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal',
];
const actualFields = [...formHtml.matchAll(/name="([^"]+)"/g)].map(match => match[1]);
assert.deepEqual(actualFields, expectedFields);

assert.match(aiCode, /const AI_ENDPOINT = '\/api\/ai\/heart-risk\/predict\/'/);
assert.match(aiCode, /method: 'POST'/);
assert.match(aiCode, /apiRequest\(AI_ENDPOINT/);
assert.match(aiCode, /JSON\.stringify\(payload\)/);
assert.match(doctorJs, /MediCareAuth\?\.apiRequest/); // The shared wrapper delegates to the existing CSRF/session helper.
assert.match(aiCode, /form\.dataset\.submitting/);
assert.match(aiCode, /submitButton\.disabled = true/);
assert.match(aiCode, /Analyzing…/);
assert.match(aiCode, /status === 400/);
assert.match(aiCode, /status === 403/);
assert.match(aiCode, /status === 429/);
assert.match(aiCode, /status === 500/);
assert.match(aiCode, /backend is unavailable/);
assert.match(aiCode, /model_probability/);
assert.match(aiCode, /academic_development_only/);
assert.match(aiCode, /replaceChildren\(/);
assert.match(aiCode, /textContent/);
assert.match(aiCode, /Doctor decision boundary/);
assert.doesNotMatch(aiCode, /diagnosis|prescription|treatment|emergency/);
assert.doesNotMatch(aiCode, /innerHTML/);
assert.doesNotMatch(aiCode, /localStorage|sessionStorage/);
assert.doesNotMatch(aiCode, /patient_id|medical_records|prescriptions|appointments/);

assert.doesNotMatch(patientJs, /heart-risk\/predict/);
assert.doesNotMatch(patientJs, /apiRequest|fetch\s*\(/);
assert.match(patientJs, /No prediction request was sent/);
assert.match(patientHtml, /AI Health Insights/);

const allFrontendFiles = [];
function walk(directory) {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
        const file = path.join(directory, entry.name);
        if (entry.isDirectory()) walk(file);
        else allFrontendFiles.push(file);
    }
}
walk(path.join(root, 'frontend'));
assert.deepEqual(
    allFrontendFiles.filter(file => /\.(joblib|pkl|onnx|pt|h5)$/i.test(file)),
    [],
);

console.log('phase20_doctor_workflow_contract=PASS');
console.log(`phase20_feature_count=${actualFields.length}`);
console.log('phase20_patient_denial_preserved=PASS');
console.log('phase20_frontend_model_artifacts=0');
