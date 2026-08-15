/*
   DOCTOR DASHBOARD JAVASCRIPT
========================================================= */

function apiRequest(path, options = {}) {
    if (window.MediCareAuth?.apiRequest) return window.MediCareAuth.apiRequest(path, options);
    return Promise.reject(new Error('Unable to connect to the server.'));
}

function escapeHTML(value) {
    return String(value ?? '').replace(/[&<>'"]/g, character => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[character]));
}

function displayTime(value) {
    if (!value) return '—';
    const [hours, minutes] = value.slice(0, 5).split(':').map(Number);
    const suffix = hours >= 12 ? 'PM' : 'AM';
    const displayHour = hours % 12 || 12;
    return `${String(displayHour).padStart(2, '0')}:${String(minutes).padStart(2, '0')} ${suffix}`;
}

function displayDate(value) {
    if (!value) return '—';
    return new Date(`${value}T00:00:00`).toLocaleDateString(undefined, { day: '2-digit', month: 'short', year: 'numeric' });
}

function displayStatus(status) {
    return {
        pending: 'Pending', confirmed: 'Confirmed', rejected: 'Rejected',
        cancelled: 'Cancelled', completed: 'Completed'
    }[status] || status || '—';
}

function errorMessage(payload, fallback) {
    if (payload?.detail) return payload.detail;
    return Object.values(payload || {}).flatMap(value => Array.isArray(value) ? value : [value]).filter(Boolean).join(' ') || fallback;
}

function showToast(message) {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('hiding');
        toast.addEventListener('animationend', () => toast.remove());
    }, 3000);
}

function patientStatusClass(status) {
    const normalized = String(status || '').toLowerCase();
    if (normalized.includes('cancel') || normalized.includes('reject')) return 'critical';
    if (normalized.includes('pending')) return 'review';
    return 'stable';
}

function renderDoctorSchedule(appointments) {
    const panel = document.querySelector('.appointment-panel');
    if (!panel) return;
    panel.querySelectorAll('.appointment').forEach(element => element.remove());
    const header = panel.querySelector('.section-header');
    const insertAfterHeader = element => {
        if (header && header.parentElement) header.parentElement.insertBefore(element, header.nextSibling);
        else panel.appendChild(element);
    };
    if (!appointments.length) {
        const empty = document.createElement('div');
        empty.className = 'appointment';
        const info = document.createElement('div');
        info.className = 'appointment-info';
        info.append(document.createElement('strong'), document.createElement('span'));
        info.firstChild.textContent = 'No appointments today';
        info.lastChild.textContent = 'Your schedule is clear.';
        empty.appendChild(info);
        insertAfterHeader(empty);
        return;
    }
    appointments.forEach(appointment => {
        const item = document.createElement('div');
        item.className = 'appointment';
        item.dataset.appointmentId = String(appointment.id);
        const time = document.createElement('div');
        time.className = 'time';
        time.appendChild(Object.assign(document.createElement('strong'), { textContent: displayTime(appointment.scheduled_time) }));
        const info = document.createElement('div');
        info.className = 'appointment-info';
        info.append(
            Object.assign(document.createElement('strong'), { textContent: appointment.patient_name || 'Patient' }),
            Object.assign(document.createElement('span'), { textContent: appointment.reason || 'Appointment' }),
            Object.assign(document.createElement('small'), { textContent: displayStatus(appointment.status) })
        );
        const actions = document.createElement('div');
        actions.className = 'appointment-actions';
        const actionNames = appointment.status === 'pending' ? ['confirm', 'reject'] : appointment.status === 'confirmed' ? ['complete', 'cancel'] : [];
        actionNames.forEach(action => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'view-btn appointment-action';
            button.dataset.appointmentId = String(appointment.id);
            button.dataset.action = action;
            button.textContent = action.charAt(0).toUpperCase() + action.slice(1);
            actions.appendChild(button);
        });
        item.append(time, info, actions, Object.assign(document.createElement('i'), { className: 'fa-solid fa-chevron-right' }));
        insertAfterHeader(item);
    });
}

function renderAuthorizedPatients(patients) {
    const tbody = document.querySelector('#patientTable tbody');
    if (!tbody) return;
    while (tbody.firstChild) tbody.removeChild(tbody.firstChild);
    if (!patients.length) {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = 6;
        cell.className = 'empty-state';
        cell.textContent = 'No authorized patients with appointments.';
        row.appendChild(cell);
        tbody.appendChild(row);
        return;
    }
    patients.forEach(patient => {
        const name = patient.patient_name || 'Patient';
        const initials = name.split(/\s+/).map(part => part[0]).join('').slice(0, 2).toUpperCase();
        const row = document.createElement('tr');
        const patientCell = document.createElement('td');
        const patientWrap = document.createElement('div');
        patientWrap.className = 'patient';
        const avatar = document.createElement('div');
        avatar.className = 'patient-avatar';
        avatar.textContent = initials;
        const identity = document.createElement('div');
        const strong = document.createElement('strong');
        strong.textContent = name;
        const small = document.createElement('small');
        small.textContent = 'Authorized patient';
        identity.append(strong, small);
        patientWrap.append(avatar, identity);
        patientCell.appendChild(patientWrap);
        const ageCell = document.createElement('td');
        ageCell.textContent = String(patient.age ?? '—');
        const conditionCell = document.createElement('td');
        conditionCell.textContent = patient.condition || 'Appointment';
        const visitCell = document.createElement('td');
        visitCell.textContent = displayDate(patient.last_visit);
        const statusCell = document.createElement('td');
        const status = document.createElement('span');
        status.className = `status ${patientStatusClass(patient.status)}`;
        status.textContent = patient.status || '—';
        statusCell.appendChild(status);
        const actionCell = document.createElement('td');
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'view-btn patient-summary-btn';
        button.dataset.patientId = String(patient.patient_id);
        button.dataset.patientName = name;
        button.textContent = 'View';
        actionCell.appendChild(button);
        row.append(patientCell, ageCell, conditionCell, visitCell, statusCell, actionCell);
        tbody.appendChild(row);
    });
}

function applyDoctorDashboard(data) {
    const doctor = data.doctor || {};
    const fullName = `Dr. ${doctor.first_name || ''} ${doctor.last_name || ''}`.replace(/\s+/g, ' ').trim();
    document.getElementById('doctorName')?.replaceChildren(document.createTextNode(fullName));
    document.getElementById('doctorWelcomeName')?.replaceChildren(document.createTextNode(fullName));
    const specialization = document.getElementById('doctorSpecialization');
    if (specialization) specialization.textContent = doctor.specialization || '—';
    const todayCount = document.getElementById('doctorTodayAppointmentsCount');
    const remainingCount = document.getElementById('doctorTodayRemainingCount');
    if (todayCount) todayCount.textContent = data.today_count ?? 0;
    if (remainingCount) remainingCount.textContent = `${data.today_count ?? 0} active today`;
    const totalPatients = document.getElementById('doctorTotalPatientsCount');
    const pendingReports = document.getElementById('doctorPendingReportsCount');
    const criticalAlerts = document.getElementById('doctorCriticalAlertsCount');
    if (totalPatients) totalPatients.textContent = data.patient_count ?? 0;
    if (pendingReports) pendingReports.textContent = '—';
    if (criticalAlerts) criticalAlerts.textContent = '—';
    renderAuthorizedPatients(data.authorized_patients || []);
    renderDoctorSchedule(data.today_appointments || []);
}

function renderPatientTableMessage(message) {
    const tbody = document.querySelector('#patientTable tbody');
    if (!tbody) return;
    while (tbody.firstChild) tbody.removeChild(tbody.firstChild);
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 6;
    cell.className = 'empty-state';
    cell.textContent = message;
    row.appendChild(cell);
    tbody.appendChild(row);
}

async function loadDoctorDashboard() {
    renderPatientTableMessage('Loading authorized patients…');
    try {
        const response = await apiRequest('/api/doctor/dashboard/');
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '../auth/login.html';
                return;
            }
            if (response.status === 403) throw new Error('You are not authorized to view this dashboard.');
            throw new Error(errorMessage(payload, 'Unable to load doctor dashboard.'));
        }
        applyDoctorDashboard(payload);
    } catch (error) {
        renderPatientTableMessage(error.message || 'Unable to connect to the server.');
        showToast(error.message || 'Unable to load doctor dashboard.');
    }
}

async function transitionAppointment(id, action) {
    try {
        const response = await apiRequest(`/api/doctor/appointments/${id}/transition/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action }),
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(errorMessage(payload, 'Unable to update appointment.'));
        showToast(`Appointment ${displayStatus(payload.status).toLowerCase()}.`);
        await loadDoctorDashboard();
    } catch (error) {
        showToast(error.message || 'Unable to update appointment.');
    }
}

const appointmentPanel = document.querySelector('.appointment-panel');
appointmentPanel?.addEventListener('click', event => {
    const actionButton = event.target.closest('.appointment-action');
    if (!actionButton) return;
    event.stopPropagation();
    transitionAppointment(actionButton.dataset.appointmentId, actionButton.dataset.action);
});

const patientSearch = document.getElementById('patientSearch');
patientSearch?.addEventListener('input', function () {
    const searchValue = this.value.toLowerCase().trim();
    document.querySelectorAll('#patientTable tbody tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(searchValue) ? '' : 'none';
    });
});

const clinicalModal = document.getElementById('doctorClinicalRecordsModal');
const clinicalContent = document.getElementById('doctorClinicalRecordsContent');
const clinicalPatient = document.getElementById('doctorClinicalRecordsPatient');

function clinicalNode(tag, value, className) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (value !== undefined) element.textContent = String(value ?? '');
    return element;
}

function clearClinicalContent() {
    while (clinicalContent && clinicalContent.firstChild) clinicalContent.removeChild(clinicalContent.firstChild);
}

function clinicalStatus(message, isError = false) {
    clearClinicalContent();
    const status = clinicalNode('p', message, 'clinical-records-status');
    if (isError) status.classList.add('is-error');
    clinicalContent.appendChild(status);
}

function clinicalMetadata(label, value) {
    const item = clinicalNode('div', undefined, 'doctor-clinical-record-meta');
    item.append(clinicalNode('strong', `${label}: `), clinicalNode('span', value || '—'));
    return item;
}

function renderClinicalRecordCard(item, kind) {
    const card = clinicalNode('article', undefined, 'doctor-clinical-record');
    const title = kind === 'record' ? item.diagnosis || 'Medical record' : item.title || 'Medical report';
    const date = kind === 'record' ? item.occurred_on : item.report_date;
    card.append(clinicalNode('h4', title), clinicalMetadata('Type', kind === 'record' ? (item.record_type_label || item.record_type) : (item.report_type_label || item.report_type)), clinicalMetadata('Date', date));
    if (kind === 'record') card.append(clinicalMetadata('Notes', item.notes || 'No notes provided.'));
    if (kind === 'report') card.append(clinicalMetadata('Status', item.status_label || item.status), clinicalMetadata('Summary', item.summary || 'No summary provided.'));
    if (item.has_attachment) {
        card.append(clinicalMetadata('Attachment', `${item.attachment_name || 'Protected file'} (${item.attachment_content_type || 'validated type'}, ${item.attachment_size || 0} bytes)`));
        const download = clinicalNode('button', 'Download protected file', 'view-btn record-download');
        download.type = 'button';
        download.addEventListener('click', () => downloadClinicalFile(kind, item.id, item.attachment_name));
        card.append(download);
    }
    return card;
}

function renderClinicalRecords(patientName, records, reports) {
    clinicalPatient.textContent = `${patientName || 'Authorized patient'} — appointment-scoped access`;
    clearClinicalContent();
    if (!records.length && !reports.length) {
        clinicalStatus('No authorized clinical records or reports were found for this appointment-scoped patient.');
        return;
    }
    const list = clinicalNode('div', undefined, 'doctor-clinical-record-list');
    records.forEach(record => list.append(renderClinicalRecordCard(record, 'record')));
    reports.forEach(report => list.append(renderClinicalRecordCard(report, 'report')));
    clinicalContent.append(list);
}

async function downloadClinicalFile(kind, id, filename) {
    try {
        const path = kind === 'record' ? `/api/doctor/medical-records/${id}/download/` : `/api/doctor/reports/${id}/download/`;
        const response = await apiRequest(path);
        if (response.status === 401) {
            window.location.href = '../auth/login.html';
            return;
        }
        if (!response.ok) throw new Error(response.status === 403 ? 'You are not authorized to download this file.' : 'The protected file is unavailable.');
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = filename || 'protected-clinical-file';
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        URL.revokeObjectURL(url);
    } catch (error) {
        showToast(error.message || 'Unable to download the protected file.');
    }
}

let phase26CurrentPatientId = null;
let phase26CurrentPatientName = '';
let phase26CurrentRecords = [];
let phase26CurrentAppointments = [];

const phase26Workflow = document.getElementById('phase26ClinicalWorkflow');
const phase26Form = document.getElementById('phase26ClinicalForm');
const phase26Type = document.getElementById('phase26WorkflowType');
const phase26Appointment = document.getElementById('phase26AppointmentId');
const phase26RecordLink = document.getElementById('phase26MedicalRecordId');
const phase26RecordFields = document.getElementById('phase26RecordFields');
const phase26ReportFields = document.getElementById('phase26ReportFields');
const phase26PrescriptionFields = document.getElementById('phase26PrescriptionFields');
const phase26WorkflowStatus = document.getElementById('phase26WorkflowStatus');
const phase26SubmitButton = document.getElementById('phase26Submit');

function phase26Field(id) {
    return document.getElementById(id)?.value.trim() || '';
}

function phase26SetStatus(message, isError = false) {
    if (!phase26WorkflowStatus) return;
    phase26WorkflowStatus.textContent = message || '';
    phase26WorkflowStatus.hidden = !message;
    phase26WorkflowStatus.classList.toggle('is-error', Boolean(message) && isError);
}

function phase26Option(value, label) {
    const option = document.createElement('option');
    option.value = String(value);
    option.textContent = label;
    return option;
}

function phase26PopulateLinks(records, appointments) {
    if (phase26Appointment) {
        phase26Appointment.replaceChildren(phase26Option('', 'No appointment link'));
        appointments.forEach(appointment => {
            const date = displayDate(appointment.scheduled_date);
            const reason = appointment.reason || 'Appointment';
            phase26Appointment.appendChild(phase26Option(appointment.id, `${date} — ${reason}`));
        });
    }
    if (phase26RecordLink) {
        phase26RecordLink.replaceChildren(phase26Option('', 'No record link'));
        records.forEach(record => phase26RecordLink.appendChild(phase26Option(record.id, `${record.occurred_on || 'Record'} — ${record.diagnosis || 'Medical record'}`)));
    }
}

function phase26SetDates() {
    const today = new Date().toISOString().slice(0, 10);
    ['phase26RecordDate', 'phase26ReportDate', 'phase26IssuedOn', 'phase26StartDate'].forEach(id => {
        const element = document.getElementById(id);
        if (element && !element.value) element.value = today;
    });
}

function phase26ToggleFields() {
    const type = phase26Type?.value || 'record';
    if (phase26RecordFields) phase26RecordFields.hidden = type !== 'record';
    if (phase26ReportFields) phase26ReportFields.hidden = type !== 'report';
    if (phase26PrescriptionFields) phase26PrescriptionFields.hidden = type !== 'prescription';
    phase26SetStatus('');
}

function phase26SyncWorkflow(records, appointments) {
    phase26CurrentRecords = records;
    phase26CurrentAppointments = appointments;
    if (phase26Workflow) phase26Workflow.hidden = !phase26CurrentPatientId;
    phase26PopulateLinks(records, appointments);
    phase26SetDates();
    phase26ToggleFields();
}

function phase26Payload() {
    const workflow = phase26Type?.value || 'record';
    const appointmentId = phase26Field('phase26AppointmentId');
    if (!phase26CurrentPatientId) {
        phase26SetStatus('Select an authorized patient before creating a clinical entry.', true);
        return null;
    }
    if (workflow === 'record') {
        const diagnosis = phase26Field('phase26Diagnosis');
        const occurredOn = phase26Field('phase26RecordDate');
        if (!diagnosis || !occurredOn) {
            phase26SetStatus('Record title and occurrence date are required.', true);
            return null;
        }
        return {
            endpoint: '/api/doctor/medical-records/',
            payload: {
                patient_id: phase26CurrentPatientId,
                ...(appointmentId ? { appointment_id: Number(appointmentId) } : {}),
                record_type: phase26Field('phase26RecordType'),
                occurred_on: occurredOn,
                diagnosis,
                notes: phase26Field('phase26RecordNotes'),
            },
        };
    }
    if (workflow === 'report') {
        const title = phase26Field('phase26ReportTitle');
        const reportDate = phase26Field('phase26ReportDate');
        if (!title || !reportDate) {
            phase26SetStatus('Report title and report date are required.', true);
            return null;
        }
        const findingLabel = phase26Field('phase26FindingLabel');
        const findingValue = phase26Field('phase26FindingValue');
        if (Boolean(findingLabel) !== Boolean(findingValue)) {
            phase26SetStatus('Provide both a finding label and value, or leave both blank.', true);
            return null;
        }
        return {
            endpoint: '/api/doctor/reports/',
            payload: {
                patient_id: phase26CurrentPatientId,
                ...(appointmentId ? { appointment_id: Number(appointmentId) } : {}),
                ...(phase26Field('phase26MedicalRecordId') ? { medical_record_id: Number(phase26Field('phase26MedicalRecordId')) } : {}),
                title,
                report_type: phase26Field('phase26ReportType'),
                laboratory_name: phase26Field('phase26Laboratory'),
                report_date: reportDate,
                status: phase26Field('phase26ReportStatus'),
                summary: phase26Field('phase26ReportSummary'),
                interpretation: phase26Field('phase26Interpretation'),
                findings: findingLabel ? [{ label: findingLabel, value: findingValue, is_normal: Boolean(document.getElementById('phase26FindingNormal')?.checked), sort_order: 0 }] : [],
            },
        };
    }
    const medicine = phase26Field('phase26Medicine');
    const dosage = phase26Field('phase26Dosage');
    const frequency = phase26Field('phase26Frequency');
    const issuedOn = phase26Field('phase26IssuedOn');
    const startDate = phase26Field('phase26StartDate');
    if (!medicine || !dosage || !frequency || !issuedOn || !startDate) {
        phase26SetStatus('Medicine, dosage, frequency, issued date, and start date are required.', true);
        return null;
    }
    return {
        endpoint: '/api/doctor/prescriptions/',
        payload: {
            patient_id: phase26CurrentPatientId,
            status: phase26Field('phase26PrescriptionStatus'),
            issued_on: issuedOn,
            start_date: startDate,
            ...(phase26Field('phase26EndDate') ? { end_date: phase26Field('phase26EndDate') } : {}),
            items: [{ medicine, dosage, frequency, duration: phase26Field('phase26Duration'), instructions: phase26Field('phase26Instructions'), side_effects: phase26Field('phase26SideEffects') }],
        },
    };
}

async function submitPhase26ClinicalEntry(event) {
    event.preventDefault();
    if (phase26Form?.dataset.submitting === 'true') return;
    const request = phase26Payload();
    if (!request) return;
    phase26Form.dataset.submitting = 'true';
    if (phase26SubmitButton) {
        phase26SubmitButton.disabled = true;
        phase26SubmitButton.textContent = 'Saving…';
    }
    phase26SetStatus('Saving authorized clinical entry…', false);
    try {
        const response = await apiRequest(request.endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request.payload),
        });
        const payload = await response.json().catch(() => ({}));
        if (response.status === 401) {
            window.location.href = '../auth/login.html';
            return;
        }
        if (response.status === 403) throw new Error('You are not authorized to create this clinical entry.');
        if (!response.ok) throw new Error(errorMessage(payload, 'Unable to save the clinical entry.'));
        phase26SetStatus('Clinical entry saved. Refreshing the authorized patient view…', false);
        await openClinicalRecords(phase26CurrentPatientId, phase26CurrentPatientName);
    } catch (error) {
        phase26SetStatus(error.message || 'Unable to save the clinical entry.', true);
    } finally {
        if (phase26Form) phase26Form.dataset.submitting = 'false';
        if (phase26SubmitButton) {
            phase26SubmitButton.disabled = false;
            phase26SubmitButton.textContent = 'Save clinical entry';
        }
    }
}

async function openClinicalRecords(patientId, patientName) {
    phase26CurrentPatientId = patientId;
    phase26CurrentPatientName = patientName || 'Authorized patient';
    clinicalModal.classList.add('open');
    clinicalModal.setAttribute('aria-hidden', 'false');
    clinicalPatient.textContent = `${phase26CurrentPatientName} — appointment-scoped access`;
    phase26SyncWorkflow([], []);
    clinicalStatus('Loading authorized clinical records…');
    try {
        const [recordsResponse, reportsResponse, appointmentsResponse] = await Promise.all([
            apiRequest(`/api/doctor/medical-records/?patient_id=${encodeURIComponent(patientId)}`),
            apiRequest(`/api/doctor/reports/?patient_id=${encodeURIComponent(patientId)}`),
            apiRequest('/api/doctor/appointments/'),
        ]);
        if ([recordsResponse, reportsResponse, appointmentsResponse].some(response => response.status === 401)) {
            window.location.href = '../auth/login.html';
            return;
        }
        if ([recordsResponse, reportsResponse, appointmentsResponse].some(response => !response.ok)) throw new Error('Unable to load authorized clinical workflow data.');
        const records = await recordsResponse.json();
        const reports = await reportsResponse.json();
        const appointments = (await appointmentsResponse.json()).filter(item => String(item.patient_id) === String(patientId));
        renderClinicalRecords(phase26CurrentPatientName, Array.isArray(records) ? records : [], Array.isArray(reports) ? reports : []);
        phase26SyncWorkflow(Array.isArray(records) ? records : [], Array.isArray(appointments) ? appointments : []);
    } catch (error) {
        phase26SyncWorkflow([], []);
        clinicalStatus(error.message || 'Unable to load authorized clinical records.', true);
    }
}

phase26Type?.addEventListener('change', phase26ToggleFields);
phase26Form?.addEventListener('submit', submitPhase26ClinicalEntry);
phase26Form?.addEventListener('reset', () => setTimeout(() => { phase26SetDates(); phase26ToggleFields(); }, 0));

document.querySelector('#patientTable tbody')?.addEventListener('click', event => {
    const button = event.target.closest('.patient-summary-btn');
    if (button) openClinicalRecords(button.dataset.patientId, button.dataset.patientName);
});

document.getElementById('closeDoctorClinicalRecordsModal')?.addEventListener('click', () => {
    clinicalModal.classList.remove('open');
    clinicalModal.setAttribute('aria-hidden', 'true');
});
clinicalModal?.addEventListener('click', event => {
    if (event.target === clinicalModal) {
        clinicalModal.classList.remove('open');
        clinicalModal.setAttribute('aria-hidden', 'true');
    }
});

document.getElementById('viewPatients')?.addEventListener('click', () => showToast('The dashboard lists all authorized patients currently supported by the backend.'));
document.getElementById('addPatientBtn')?.addEventListener('click', () => showToast('Adding patients is deferred because no patient-management API exists.'));

function clearAiReports() {
    const list = document.getElementById('aiReportsList');
    if (list) list.replaceChildren();
}

function setAiReportsStatus(message, isError = false) {
    const status = document.getElementById('aiReportsStatus');
    if (!status) return;
    status.textContent = message || '';
    status.hidden = !message;
    status.classList.toggle('is-error', Boolean(message) && isError);
}

function renderAiReport(report) {
    const item = document.createElement('article');
    item.className = 'ai-report-card';
    item.setAttribute('role', 'listitem');
    const heading = document.createElement('h4');
    heading.textContent = report.prediction_label || 'Academic result';
    const metadata = document.createElement('p');
    metadata.textContent = `${report.created_at || ''} • ${report.model_version || ''} • ${report.preprocessing_version || ''}`;
    const probability = document.createElement('p');
    probability.textContent = `Model probability: ${report.model_probability ?? 'not available'}`;
    const probabilityNote = document.createElement('p');
    probabilityNote.textContent = report.probability_note || 'Model probability is not diagnostic confidence or clinical certainty.';
    probabilityNote.className = 'ai-report-responsibility';
    const disclaimer = document.createElement('p');
    disclaimer.textContent = report.disclaimer || 'Academic/development-only output; not a diagnosis or medical advice.';
    disclaimer.className = 'ai-report-disclaimer';
    const responsibility = document.createElement('p');
    responsibility.textContent = report.clinician_responsibility || 'The clinician remains responsible for interpretation and decisions.';
    responsibility.className = 'ai-report-responsibility';
    item.append(heading, metadata, probability, probabilityNote, disclaimer, responsibility);
    const explanation = report.explanation;
    if (explanation && Array.isArray(explanation.features)) {
        const explanationHeading = document.createElement('h5');
        explanationHeading.textContent = 'Model feature contributions';
        const explanationList = document.createElement('ul');
        explanationList.className = 'ai-report-explanation';
        explanation.features.forEach(feature => {
            const row = document.createElement('li');
            row.textContent = `${feature.feature}: ${feature.contribution >= 0 ? '+' : ''}${Number(feature.contribution).toFixed(4)} logit units (${feature.direction})`;
            explanationList.appendChild(row);
        });
        item.append(explanationHeading, explanationList);
    }
    return item;
}

async function loadAiReports() {
    const list = document.getElementById('aiReportsList');
    const button = document.getElementById('viewAiReportsButton');
    if (!list || !button) return;
    button.disabled = true;
    list.hidden = false;
    clearAiReports();
    setAiReportsStatus('Loading authorized academic reports…');
    try {
        const response = await apiRequest('/api/ai/reports/');
        const payload = await response.json().catch(() => []);
        if (response.status === 401) {
            window.location.href = '../auth/login.html';
            return;
        }
        if (response.status === 403) {
            setAiReportsStatus('Prediction reports are not available for this account.', true);
            return;
        }
        if (!response.ok || !Array.isArray(payload)) throw new Error('Unable to load academic reports.');
        if (!payload.length) {
            setAiReportsStatus('No authorized academic prediction reports are available.');
            return;
        }
        setAiReportsStatus('');
        payload.forEach(report => list.appendChild(renderAiReport(report)));
    } catch (error) {
        setAiReportsStatus(error.message || 'Unable to load academic reports.', true);
    } finally {
        button.disabled = false;
        button.setAttribute('aria-expanded', String(!list.hidden));
    }
}

document.getElementById('viewAiReportsButton')?.addEventListener('click', loadAiReports);

const AI_ENDPOINT = '/api/ai/heart-risk/predict/';
const AI_MODEL_VERSION = 'uci-heart-disease-logreg-v1.0.0';
const AI_NUMERIC_FIELDS = new Set(['age', 'trestbps', 'chol', 'thalach', 'oldpeak']);
const AI_INTEGER_FIELDS = new Set(['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'ca', 'thal']);
const AI_SUPPORT_DOMAINS = {
    age: [29, 77], trestbps: [94, 200], chol: [126, 564], thalach: [71, 202], oldpeak: [0, 6.2],
};
const AI_CATEGORICAL_DOMAINS = {
    sex: [0, 1], cp: [1, 2, 3, 4], fbs: [0, 1], restecg: [0, 1, 2], exang: [0, 1],
    slope: [1, 2, 3], ca: [0, 1, 2, 3], thal: [3, 6, 7],
};

function setAiMessage(message, isError = true) {
    const element = document.getElementById('aiValidationMessage');
    if (!element) return;
    element.textContent = message || '';
    element.classList.toggle('is-error', Boolean(message) && isError);
    element.classList.toggle('is-info', Boolean(message) && !isError);
}

const AI_FEATURE_ORDER = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'];
const AI_EXPLANATION_DIRECTIONS = new Set(['supports_predicted_class', 'opposes_predicted_class', 'neutral']);

function clearAiResult() {
    const result = document.getElementById('aiPredictionResult');
    const explanation = document.getElementById('aiExplanation');
    const explanationList = document.getElementById('aiExplanationList');
    result?.replaceChildren();
    explanationList?.replaceChildren();
    if (result) result.hidden = true;
    if (explanation) explanation.hidden = true;
}

function addAiResultLine(container, label, value, className = '') {
    const line = document.createElement('p');
    if (className) line.className = className;
    const labelElement = document.createElement('strong');
    labelElement.textContent = `${label}: `;
    line.append(labelElement, document.createTextNode(String(value)));
    container.appendChild(line);
}

function explanationDirectionText(direction) {
    return {
        supports_predicted_class: 'supports the predicted class',
        opposes_predicted_class: 'opposes the predicted class',
        neutral: 'neutral for the predicted class',
    }[direction] || 'not available';
}

function renderAiExplanation(explanation) {
    const section = document.getElementById('aiExplanation');
    const list = document.getElementById('aiExplanationList');
    if (!section || !list || !explanation?.features?.length) return false;
    list.replaceChildren();
    const maxMagnitude = Math.max(...explanation.features.map(item => Math.abs(item.contribution)), 1e-12);
    const meta = document.createElement('p');
    meta.className = 'ai-explanation-meta';
    meta.textContent = `Method: ${explanation.method}. Output space: ${explanation.output_space}. Base value: ${Number(explanation.base_value).toFixed(4)} logit units.`;
    list.appendChild(meta);
    explanation.features.forEach(item => {
        const row = document.createElement('div');
        row.className = `ai-contribution-row ai-contribution-${item.direction}`;
        row.setAttribute('role', 'listitem');
        const label = document.createElement('div');
        label.className = 'ai-contribution-label';
        const feature = document.createElement('strong');
        feature.textContent = item.feature;
        const value = document.createElement('span');
        value.textContent = `value ${item.value}`;
        label.append(feature, value);
        const direction = document.createElement('span');
        direction.className = 'ai-contribution-direction';
        direction.textContent = explanationDirectionText(item.direction);
        const track = document.createElement('div');
        track.className = 'ai-contribution-track';
        track.setAttribute('aria-hidden', 'true');
        const bar = document.createElement('span');
        bar.className = 'ai-contribution-bar';
        bar.style.width = `${Math.max(0, Math.min(100, Math.abs(item.contribution) / maxMagnitude * 100))}%`;
        track.appendChild(bar);
        const amount = document.createElement('span');
        amount.className = 'ai-contribution-amount';
        amount.textContent = `${item.contribution >= 0 ? '+' : ''}${item.contribution.toFixed(4)} logit units`;
        row.append(label, direction, track, amount);
        list.appendChild(row);
    });
    section.hidden = false;
    return true;
}

function renderAiResult(payload) {
    const result = document.getElementById('aiPredictionResult');
    if (!result) return;
    result.replaceChildren();
    const heading = document.createElement('strong');
    heading.className = 'ai-result-title';
    heading.textContent = 'Academic AI Risk Classification';
    result.appendChild(heading);
    addAiResultLine(result, 'Classification', payload.prediction);
    addAiResultLine(result, 'Model probability', payload.model_probability);
    addAiResultLine(result, 'Model', payload.model);
    addAiResultLine(result, 'Status', payload.status);
    const disclaimer = document.createElement('p');
    disclaimer.className = 'ai-result-disclaimer';
    disclaimer.textContent = payload.disclaimer;
    result.appendChild(disclaimer);
    const decisionBoundary = document.createElement('p');
    decisionBoundary.className = 'ai-decision-boundary';
    decisionBoundary.textContent = 'Doctor decision boundary: This is informational academic output. The doctor remains responsible for clinical interpretation and decision-making.';
    result.appendChild(decisionBoundary);
    result.hidden = false;
    renderAiExplanation(payload.explanation);
}

function validateAiExplanation(explanation) {
    if (!explanation || explanation.method !== 'logistic_regression_native_coefficient_contribution' || explanation.output_space !== 'logit') return false;
    if (typeof explanation.preprocessing !== 'string' || typeof explanation.disclaimer !== 'string' || !Number.isFinite(explanation.base_value)) return false;
    if (!explanation.disclaimer.toLowerCase().includes('model')) return false;
    if (!Array.isArray(explanation.features) || explanation.features.length !== AI_FEATURE_ORDER.length) return false;
    return explanation.features.every((item, index) => item.feature === AI_FEATURE_ORDER[index] && typeof item.value === 'number' && Number.isFinite(item.value) && typeof item.contribution === 'number' && Number.isFinite(item.contribution) && AI_EXPLANATION_DIRECTIONS.has(item.direction));
}

function validateAiResponse(payload) {
    const probability = payload?.model_probability;
    return Boolean(
        payload && payload.model === AI_MODEL_VERSION &&
        ['label_absent', 'label_present'].includes(payload.prediction) &&
        typeof probability === 'number' && Number.isFinite(probability) && probability >= 0 && probability <= 1 &&
        payload.status === 'academic_development_only' &&
        typeof payload.disclaimer === 'string' && payload.disclaimer.length > 0 &&
        validateAiExplanation(payload.explanation)
    );
}

function collectAiPayload(form) {
    const payload = {};
    [...AI_NUMERIC_FIELDS, ...AI_INTEGER_FIELDS].forEach(field => {
        const rawValue = form.elements[field]?.value.trim();
        payload[field] = AI_INTEGER_FIELDS.has(field) ? Number.parseInt(rawValue, 10) : Number.parseFloat(rawValue);
    });
    return payload;
}

function validateAiPayload(payload) {
    const errors = [];
    AI_NUMERIC_FIELDS.forEach(field => {
        const value = payload[field];
        if (!Number.isFinite(value)) errors.push(`${field} is required.`);
        const domain = AI_SUPPORT_DOMAINS[field];
        if (Number.isFinite(value) && (value < domain[0] || value > domain[1])) errors.push(`${field} must be between ${domain[0]} and ${domain[1]}.`);
    });
    AI_INTEGER_FIELDS.forEach(field => {
        const value = payload[field];
        if (!Number.isInteger(value)) errors.push(`${field} must use an approved integer code.`);
        if (Number.isInteger(value) && !AI_CATEGORICAL_DOMAINS[field].includes(value)) errors.push(`${field} uses an invalid source code.`);
    });
    return errors;
}

function aiErrorMessage(status) {
    if (status === 400) return 'Invalid academic model input. Check the required values and source codes.';
    if (status === 403) return 'You are not authorized to use this academic AI tool.';
    if (status === 429) return 'The AI service rate limit was reached. Please try again later.';
    if (status === 500 || status === 503) return 'The AI service is currently unavailable. Please try again later.';
    return 'The AI service returned an unexpected response.';
}

async function submitAiPrediction(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const submitButton = document.getElementById('aiSubmitBtn');
    const resetButton = document.getElementById('aiResetBtn');
    if (form.dataset.submitting === 'true') return;

    clearAiResult();
    setAiMessage('');
    const payload = collectAiPayload(form);
    const validationErrors = validateAiPayload(payload);
    if (validationErrors.length > 0) {
        setAiMessage(validationErrors[0]);
        return;
    }

    form.dataset.submitting = 'true';
    form.setAttribute('aria-busy', 'true');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Analyzing…';
    }
    if (resetButton) resetButton.disabled = true;
    setAiMessage('Analyzing academic model input…', false);

    try {
        const response = await apiRequest(AI_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const responsePayload = await response.json().catch(() => ({}));
        if (!response.ok) {
            setAiMessage(aiErrorMessage(response.status));
            return;
        }
        if (!validateAiResponse(responsePayload)) {
            setAiMessage('The AI service returned an invalid response. Please try again later.');
            return;
        }
        setAiMessage('');
        renderAiResult(responsePayload);
    } catch (error) {
        setAiMessage('The backend is unavailable. Please try again later.');
    } finally {
        form.dataset.submitting = 'false';
        form.removeAttribute('aria-busy');
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = 'Run Academic Classification';
        }
        if (resetButton) resetButton.disabled = false;
    }
}

function resetAiForm() {
    const form = document.getElementById('doctorAiForm');
    if (!form || form.dataset.submitting === 'true') return;
    form.reset();
    setAiMessage('');
    clearAiResult();
}

const aiButton = document.getElementById('aiButton');
const aiForm = document.getElementById('doctorAiForm');
aiButton?.addEventListener('click', () => {
    const isHidden = aiForm?.hasAttribute('hidden');
    if (!aiForm) return;
    aiForm.hidden = !isHidden;
    aiButton.setAttribute('aria-expanded', String(isHidden));
    if (isHidden) aiForm.querySelector('input, select, button')?.focus();
});
aiForm?.addEventListener('submit', submitAiPrediction);
document.getElementById('aiResetBtn')?.addEventListener('click', resetAiForm);
document.querySelector('.notification')?.addEventListener('click', () => showToast('Notifications are deferred because no notification API exists.'));

document.addEventListener('DOMContentLoaded', loadDoctorDashboard);
