const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const projectRoot = path.resolve(__dirname, '..', '..');
const htmlPath = path.join(projectRoot, 'frontend', 'pages', 'patient', 'patient-ai-insights.html');
const jsPath = path.join(projectRoot, 'frontend', 'js', 'patient', 'patient-ai-insights.js');
const html = fs.readFileSync(htmlPath, 'utf8');
const js = fs.readFileSync(jsPath, 'utf8');

assert.match(html, /patient-ai-insights\.css/);
assert.match(html, /auth-client\.js/);
assert.match(html, /patient-ai-insights\.js/);
assert.match(html, /role="status"/);
assert.match(html, /aria-live="polite"/);
assert.match(html, /aria-controls="analysisResultsArea"/);

assert.match(js, /Patient-facing AI risk classification is not available/);
assert.match(js, /No prediction request was sent/);
assert.match(js, /replaceChildren\(/);
assert.match(js, /textContent/);
assert.doesNotMatch(js, /innerHTML/);
assert.doesNotMatch(js, /apiRequest/);
assert.doesNotMatch(js, /fetch\s*\(/);
assert.doesNotMatch(js, /heart-risk\/predict/);
assert.doesNotMatch(js, /model_probability|uci-heart-disease-logreg/);

function walk(directory) {
    return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
        const absolute = path.join(directory, entry.name);
        return entry.isDirectory() ? walk(absolute) : [absolute];
    });
}

const forbiddenModelFiles = walk(path.join(projectRoot, 'frontend')).filter((file) =>
    /\.(joblib|pkl|onnx|pt|h5)$/i.test(file)
);
assert.deepEqual(forbiddenModelFiles, []);

console.log('phase19_frontend_contract=PASS');
console.log('patient_ai_page_api_call=NONE_BY_AUTHORIZATION_DECISION');
console.log('safe_dom_rendering=PASS');
console.log('accessibility_attributes=PASS');
console.log('frontend_model_artifacts=0');
