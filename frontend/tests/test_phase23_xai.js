const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..', '..');
const doctorHtml = fs.readFileSync(path.join(root, 'frontend/pages/doctor/doctor-dashboard.html'), 'utf8');
const doctorJs = fs.readFileSync(path.join(root, 'frontend/js/doctor/doctor-dashboard.js'), 'utf8');
const patientJs = fs.readFileSync(path.join(root, 'frontend/js/patient/patient-ai-insights.js'), 'utf8');

const aiStart = doctorJs.indexOf("const AI_ENDPOINT =");
assert.notEqual(aiStart, -1);
const aiCode = doctorJs.slice(aiStart);

assert.match(doctorHtml, /id="aiExplanation"[^>]*aria-labelledby="aiExplanationTitle"/);
assert.match(doctorHtml, /id="aiExplanationList"[^>]*role="list"/);
assert.match(doctorHtml, /These signed values describe how the model used/);
assert.match(aiCode, /const AI_FEATURE_ORDER = \['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'\]/);
assert.match(aiCode, /validateAiExplanation/);
assert.match(aiCode, /logistic_regression_native_coefficient_contribution/);
assert.match(aiCode, /supports the predicted class/);
assert.match(aiCode, /opposes the predicted class/);
assert.match(aiCode, /logit units/);
assert.match(aiCode, /createElement\(/);
assert.match(aiCode, /replaceChildren\(/);
assert.match(aiCode, /textContent/);
assert.match(aiCode, /aria-hidden/);
assert.doesNotMatch(aiCode, /innerHTML/);
assert.doesNotMatch(aiCode, /eval\s*\(/);
assert.doesNotMatch(aiCode, /Function\s*\(/);
assert.doesNotMatch(aiCode, /localStorage|sessionStorage/);
assert.doesNotMatch(aiCode, /patient_id|medical_records|prescriptions|appointments/);
assert.doesNotMatch(aiCode, /diagnosed the patient|caused the disease|treatment recommendation/);
assert.doesNotMatch(patientJs, /heart-risk\/predict/);
assert.match(patientJs, /No prediction request was sent/);

console.log('phase23_xai_frontend_contract=PASS');
console.log('phase23_xai_safe_dom=PASS');
console.log('phase23_xai_patient_denial=PASS');
