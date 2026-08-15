const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const patientRecords = fs.readFileSync(path.join(root, 'js/patient/patient-medical-records.js'), 'utf8');
const patientReports = fs.readFileSync(path.join(root, 'js/patient/patient-reports.js'), 'utf8');
const doctorDashboard = fs.readFileSync(path.join(root, 'js/doctor/doctor-dashboard.js'), 'utf8');
const reportsHtml = fs.readFileSync(path.join(root, 'pages/patient/patient-reports.html'), 'utf8');
const doctorHtml = fs.readFileSync(path.join(root, 'pages/doctor/doctor-dashboard.html'), 'utf8');

function assert(condition, message) {
    if (!condition) throw new Error(message);
}

assert(patientRecords.includes('/api/patient/medical-records/'), 'patient record API path missing');
assert(patientRecords.includes('/download/'), 'patient record protected download path missing');
assert(patientRecords.includes('attachment_name') && patientRecords.includes('attachment_content_type') && patientRecords.includes('attachment_size'), 'patient record safe metadata missing');
assert(patientRecords.includes('Patient clinical uploads are not enabled'), 'patient record upload denial missing');
assert(patientRecords.includes('textContent') && patientRecords.includes('createElement'), 'patient record safe DOM APIs missing');
assert(patientReports.includes('/api/patient/reports/'), 'patient report API path missing');
assert(patientReports.includes('/download/'), 'patient report protected download path missing');
assert(patientReports.includes('attachment_name') && patientReports.includes('attachment_content_type') && patientReports.includes('attachment_size'), 'patient report safe metadata missing');
assert(patientReports.includes('Patient clinical uploads are not enabled'), 'patient report upload denial missing');
assert(patientReports.includes('textContent') && patientReports.includes('createElement'), 'patient report safe DOM APIs missing');
assert(doctorDashboard.includes('/api/doctor/medical-records/'), 'doctor record API path missing');
assert(doctorDashboard.includes('/api/doctor/reports/'), 'doctor report API path missing');
assert(doctorDashboard.includes('appointment-scoped access'), 'doctor appointment-scoped viewer wording missing');
assert(doctorDashboard.includes('record-download') && doctorDashboard.includes('downloadClinicalFile'), 'doctor protected download control missing');
assert(doctorDashboard.includes('textContent') && doctorDashboard.includes('createElement'), 'doctor safe DOM APIs missing');
assert(!patientRecords.includes('innerHTML') && !patientRecords.includes('insertAdjacentHTML'), 'patient record script contains unsafe HTML API');
assert(!patientReports.includes('innerHTML') && !patientReports.includes('insertAdjacentHTML'), 'patient report script contains unsafe HTML API');
assert(!doctorDashboard.includes('innerHTML') && !doctorDashboard.includes('insertAdjacentHTML'), 'doctor dashboard script contains unsafe HTML API');
assert(!/localStorage\.(getItem|setItem)\([^)]*medical/i.test(patientRecords + patientReports + doctorDashboard), 'clinical data is persisted in localStorage');
assert(reportsHtml.includes('id="btnDownloadReport"'), 'report download control missing');
assert(doctorHtml.includes('id="doctorClinicalRecordsModal"') && doctorHtml.includes('id="doctorClinicalRecordsContent"'), 'doctor clinical viewer modal missing');
console.log('phase24_clinical_files_frontend_contract=PASS');
console.log('phase24_clinical_files_safe_dom=PASS');
console.log('phase24_clinical_files_download_boundary=PASS');
console.log('phase24_clinical_files_no_persistence_or_console=PASS');
