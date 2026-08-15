function loadUserInfo() {
    const name = localStorage.getItem('userName') || 'Patient';
    const initials = name.split(' ').map(part => part[0]).join('').toUpperCase().slice(0, 2);
    ['sidebarName', 'topbarName'].forEach(id => {
        const element = document.getElementById(id);
        if (element) element.textContent = name;
    });
    ['sidebarAvatar', 'topbarAvatar'].forEach(id => {
        const element = document.getElementById(id);
        if (element) element.textContent = initials;
    });
}

function initTheme() {
    const saved = localStorage.getItem('medicare-theme');
    if (saved === 'dark') {
        document.body.classList.add('dark');
        updateThemeIcon(true);
    }
    const button = document.getElementById('themeToggle');
    if (button) {
        button.addEventListener('click', () => {
            document.body.classList.toggle('dark');
            const dark = document.body.classList.contains('dark');
            localStorage.setItem('medicare-theme', dark ? 'dark' : 'light');
            updateThemeIcon(dark);
        });
    }
}

function updateThemeIcon(isDark) {
    const button = document.getElementById('themeToggle');
    const icon = button && button.querySelector('i');
    if (icon) icon.className = isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
}

function initLogout() {
    const logoutBtn = document.querySelector('.logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', event => {
            event.preventDefault();
            if (confirm('Are you sure you want to logout?') && window.MediCareAuth) {
                window.MediCareAuth.logout('../auth/login.html');
            }
        });
    }
}

loadUserInfo();
initTheme();
initLogout();

let medicalRecords = [];
let selectedRecord = null;
const recordsTableBody = document.getElementById('recordsTableBody');
const recordsMobileContainer = document.getElementById('recordsMobileContainer');
const searchInput = document.getElementById('searchInput');
const typeFilter = document.getElementById('typeFilter');
const detailModal = document.getElementById('detailModal');
const detailContent = document.getElementById('detailContent');
const btnDownloadRecord = document.getElementById('btnDownloadRecord');
const toast = document.getElementById('toast');

function text(value) {
    return String(value ?? '');
}

function node(tag, value, className) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (value !== undefined) element.textContent = text(value);
    return element;
}

function icon(className) {
    const element = document.createElement('i');
    element.className = className;
    return element;
}

function clear(element) {
    while (element && element.firstChild) element.removeChild(element.firstChild);
}

function displayRecordType(record) {
    return record.record_type_label || record.record_type || 'Other';
}

function displayDoctor(record) {
    return record.doctor_name || 'Not specified';
}

function getBadgeClass(type) {
    if (type === 'Lab Test') return 'badge-primary';
    if (type === 'Imaging') return 'badge-warning';
    if (type === 'Consultation') return 'badge-success';
    if (type === 'Prescription') return 'badge-muted';
    return 'badge-muted';
}

function getRecordIcon(type) {
    if (type === 'Lab Test') return 'fa-flask';
    if (type === 'Imaging') return 'fa-x-ray';
    if (type === 'Consultation') return 'fa-stethoscope';
    if (type === 'Prescription') return 'fa-pills';
    return 'fa-file-medical';
}

function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    window.setTimeout(() => toast.classList.remove('show'), 3000);
}

function renderEmptyState(message = 'No records found', detail = 'Try adjusting your search or filters.') {
    clear(recordsTableBody);
    clear(recordsMobileContainer);
    const row = node('tr');
    const cell = node('td');
    cell.colSpan = 5;
    cell.className = 'empty-state';
    cell.append(icon('fa-regular fa-folder-open'), node('h3', message), node('p', detail));
    row.append(cell);
    recordsTableBody.append(row);
    const card = node('div', undefined, 'empty-state');
    card.append(icon('fa-regular fa-folder-open'), node('h3', message), node('p', detail));
    recordsMobileContainer.append(card);
}

function makeTypeCell(type) {
    const cell = node('div', undefined, 'type-cell');
    const typeIcon = node('div', undefined, `type-icon type-${type.replace(/\s+/g, '-')}`);
    typeIcon.append(icon(`fa-solid ${getRecordIcon(type)}`));
    cell.append(typeIcon, node('span', type, `badge ${getBadgeClass(type)}`));
    return cell;
}

function makeViewButton(record) {
    const button = node('button', 'View Details', 'btn-secondary');
    button.type = 'button';
    button.addEventListener('click', () => window.viewRecordDetails(record.id));
    return button;
}

function renderRecords() {
    const searchTerm = (searchInput.value || '').toLowerCase();
    const filterType = typeFilter.value;
    const filtered = medicalRecords.filter(record => {
        const type = displayRecordType(record);
        const searchable = `${record.diagnosis || ''} ${displayDoctor(record)} ${type}`.toLowerCase();
        return searchable.includes(searchTerm) && (filterType === 'All' || type === filterType);
    });
    if (!filtered.length) {
        renderEmptyState();
        return;
    }
    clear(recordsTableBody);
    clear(recordsMobileContainer);
    filtered.forEach(record => {
        const type = displayRecordType(record);
        const row = node('tr');
        const typeCell = node('td');
        typeCell.append(makeTypeCell(type));
        const dateCell = node('td', record.occurred_on || '');
        const doctorCell = node('td', displayDoctor(record));
        const diagnosisCell = node('td', record.diagnosis || '');
        const actionCell = node('td');
        actionCell.append(makeViewButton(record));
        row.append(typeCell, dateCell, doctorCell, diagnosisCell, actionCell);
        recordsTableBody.append(row);

        const card = node('div', undefined, 'record-card');
        const header = node('div', undefined, 'record-card-header');
        header.append(makeTypeCell(type));
        const body = node('div', undefined, 'record-card-body');
        const date = node('div');
        date.append(node('strong', 'Date: '), node('span', record.occurred_on || ''));
        const doctor = node('div');
        doctor.append(node('strong', 'Doctor: '), node('span', displayDoctor(record)));
        const diagnosis = node('div');
        diagnosis.append(node('strong', 'Diagnosis: '), node('span', record.diagnosis || ''));
        body.append(date, doctor, diagnosis);
        const actions = node('div', undefined, 'record-card-actions');
        actions.append(makeViewButton(record));
        card.append(header, body, actions);
        recordsMobileContainer.append(card);
    });
}

function addDetailRow(label, value) {
    const row = node('div', undefined, 'detail-row');
    row.append(node('div', label, 'detail-label'), node('div', value, 'detail-value'));
    return row;
}

window.viewRecordDetails = function(id) {
    const record = medicalRecords.find(item => item.id === id);
    if (!record) return;
    selectedRecord = record;
    clear(detailContent);
    const typeBadge = node('span', displayRecordType(record), `badge ${getBadgeClass(displayRecordType(record))}`);
    const typeRow = node('div', undefined, 'detail-row');
    typeRow.append(node('div', 'Record Type', 'detail-label'));
    const typeValue = node('div', undefined, 'detail-value');
    typeValue.append(typeBadge);
    typeRow.append(typeValue);
    detailContent.append(
        typeRow,
        addDetailRow('Date', record.occurred_on || ''),
        addDetailRow('Doctor', displayDoctor(record)),
        addDetailRow('Diagnosis / Reason', record.diagnosis || ''),
        addDetailRow('Notes', record.notes || 'No notes provided.'),
        addDetailRow('Attachment', record.has_attachment ? `${record.attachment_name || 'Protected file'} (${record.attachment_content_type || 'validated type'}, ${record.attachment_size || 0} bytes)` : 'No attachment')
    );
    if (btnDownloadRecord) {
        btnDownloadRecord.disabled = !record.has_attachment;
        btnDownloadRecord.setAttribute('aria-disabled', String(!record.has_attachment));
    }
    detailModal.classList.add('open');
};

async function downloadSelectedRecord() {
    if (!selectedRecord || !selectedRecord.has_attachment) {
        showToast('No protected file is attached to this record.');
        return;
    }
    btnDownloadRecord.disabled = true;
    try {
        const response = await window.MediCareAuth.apiRequest(`/api/patient/medical-records/${selectedRecord.id}/download/`);
        if (response.status === 401) {
            window.location.href = '../auth/login.html';
            return;
        }
        if (!response.ok) throw new Error(response.status === 403 ? 'You are not authorized to download this file.' : 'The protected file is unavailable.');
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = selectedRecord.attachment_name || 'medical-record-file';
        document.body.append(anchor);
        anchor.click();
        anchor.remove();
        URL.revokeObjectURL(url);
    } catch (error) {
        showToast(error.message || 'Unable to download the protected file.');
    } finally {
        btnDownloadRecord.disabled = false;
    }
}

function initModals() {
    const uploadModal = document.getElementById('uploadModal');
    const btnUploadRecord = document.getElementById('btnUploadRecord');
    const closeUploadModal = document.getElementById('closeUploadModal');
    const btnCancelUpload = document.getElementById('btnCancelUpload');
    const closeDetailModal = document.getElementById('closeDetailModal');
    const uploadForm = document.getElementById('uploadForm');
    btnUploadRecord.addEventListener('click', () => showToast('Patient clinical uploads are not enabled by the current policy.'));
    closeUploadModal.addEventListener('click', () => uploadModal.classList.remove('open'));
    btnCancelUpload.addEventListener('click', () => uploadModal.classList.remove('open'));
    closeDetailModal.addEventListener('click', () => detailModal.classList.remove('open'));
    uploadForm.addEventListener('submit', event => {
        event.preventDefault();
        uploadModal.classList.remove('open');
        showToast('Patient clinical uploads are not enabled by the current policy.');
    });
    btnDownloadRecord.addEventListener('click', downloadSelectedRecord);
}

async function loadMedicalRecords() {
    renderEmptyState('Loading medical records…', 'Retrieving your authorized records.');
    try {
        const response = await window.MediCareAuth.apiRequest('/api/patient/medical-records/');
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '../auth/login.html';
                return;
            }
            if (response.status === 403) throw new Error('You are not authorized to view medical records.');
            throw new Error('Unable to load medical records.');
        }
        medicalRecords = await response.json();
        renderRecords();
    } catch (error) {
        medicalRecords = [];
        renderEmptyState('Unable to load records', 'Please try again later.');
        showToast(error.message || 'Unable to load medical records.');
    }
}

searchInput.addEventListener('input', renderRecords);
typeFilter.addEventListener('change', renderRecords);
initModals();
loadMedicalRecords();
