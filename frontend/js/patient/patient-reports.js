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

let reports = [];
let selectedReport = null;
const reportsGrid = document.getElementById('reportsGrid');
const filterSearch = document.getElementById('filterSearch');
const filterType = document.getElementById('filterType');
const filterStatus = document.getElementById('filterStatus');
const statTotal = document.getElementById('statTotal');
const statNormal = document.getElementById('statNormal');
const statNeedsAttention = document.getElementById('statNeedsAttention');
const viewModal = document.getElementById('viewReportModal');
const viewContent = document.getElementById('viewReportContent');
const toastContainer = document.getElementById('toastContainer');
const downloadReportControl = document.getElementById('btnDownloadReport');

function node(tag, value, className) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (value !== undefined) element.textContent = String(value ?? '');
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

function displayType(report) {
    return report.report_type_label || report.report_type || 'Other';
}

function displayStatus(report) {
    return report.status_label || report.status || 'Pending';
}

function displayDoctor(report) {
    return report.doctor_name || 'Not specified';
}

function reportVisuals(type) {
    if (type === 'Blood Test') return { icon: 'fa-droplet', color: '#dc2626' };
    if (type === 'Imaging') return { icon: 'fa-lungs', color: '#0b5ed7' };
    if (type === 'ECG') return { icon: 'fa-heart-pulse', color: '#16a34a' };
    if (type === 'Urine Test') return { icon: 'fa-flask', color: '#d97706' };
    return { icon: 'fa-file-lines', color: '#0b5ed7' };
}

function statusBadge(status) {
    const badgeClass = status === 'Normal' ? 'badge-success' : status === 'Abnormal' ? 'badge-danger' : status === 'Pending' ? 'badge-warning' : 'badge-muted';
    const badge = node('span', undefined, `badge ${badgeClass}`);
    const statusIcon = status === 'Normal' ? 'fa-check' : status === 'Abnormal' ? 'fa-triangle-exclamation' : 'fa-clock';
    badge.append(icon(`fa-solid ${statusIcon}`), node('span', status));
    return badge;
}

function showToast(message) {
    const toast = node('div', undefined, 'toast');
    const info = icon('fa-solid fa-circle-info');
    info.style.color = 'var(--success)';
    info.style.fontSize = '16px';
    toast.append(info, node('span', message));
    toastContainer.append(toast);
    window.setTimeout(() => { if (toast.parentElement) toast.remove(); }, 3000);
}

function renderEmpty(message = 'No reports found', detail = 'Try adjusting your search or filters.') {
    clear(reportsGrid);
    const state = node('div', undefined, 'empty-state');
    state.style.gridColumn = '1 / -1';
    state.append(icon('fa-solid fa-folder-open'), node('h3', message), node('p', detail));
    reportsGrid.append(state);
}

function makeReportCard(report) {
    const type = displayType(report);
    const visual = reportVisuals(type);
    const card = node('div', undefined, 'report-card');
    const status = node('div', undefined, 'report-status');
    status.append(statusBadge(displayStatus(report)));
    const header = node('div', undefined, 'report-header');
    const reportIcon = node('div', undefined, 'report-icon');
    reportIcon.style.backgroundColor = `${visual.color}20`;
    reportIcon.style.color = visual.color;
    reportIcon.append(icon(`fa-solid ${visual.icon}`));
    const title = node('div', undefined, 'report-title');
    const heading = node('h3', report.title || 'Untitled report');
    const ordered = node('p');
    ordered.append(icon('fa-solid fa-user-doctor'), node('span', ` Ordered by ${displayDoctor(report)}`));
    title.append(heading, ordered);
    header.append(reportIcon, title);
    const summary = node('div', report.summary || 'No summary provided.', 'report-summary');
    const footer = node('div', undefined, 'report-footer');
    const reportDate = node('div', undefined, 'report-date');
    reportDate.append(icon('fa-regular fa-calendar'), node('span', ` ${report.report_date || ''}`));
    const viewButton = node('button', 'View Report', 'btn-secondary');
    viewButton.type = 'button';
    viewButton.addEventListener('click', () => window.viewReport(report.id));
    footer.append(reportDate, viewButton);
    card.append(status, header, summary, footer);
    return card;
}

function renderReports() {
    const searchTerm = (filterSearch.value || '').toLowerCase();
    const typeValue = filterType.value;
    const statusValue = filterStatus.value;
    const filtered = reports.filter(report => {
        const type = displayType(report);
        const status = displayStatus(report);
        const searchable = `${report.title || ''} ${displayDoctor(report)} ${type}`.toLowerCase();
        return searchable.includes(searchTerm) && (typeValue === 'All' || type === typeValue) && (statusValue === 'All' || status === statusValue);
    });
    statTotal.textContent = String(reports.length);
    statNormal.textContent = String(reports.filter(report => displayStatus(report) === 'Normal').length);
    statNeedsAttention.textContent = String(reports.filter(report => displayStatus(report) === 'Abnormal').length);
    if (!filtered.length) {
        renderEmpty();
        return;
    }
    clear(reportsGrid);
    filtered.forEach(report => reportsGrid.append(makeReportCard(report)));
}

function detailRow(label, value) {
    const row = node('div', undefined, 'report-detail-row');
    row.append(node('strong', label), node('span', value));
    return row;
}

window.viewReport = function(id) {
    const report = reports.find(item => item.id === id);
    if (!report) return;
    selectedReport = report;
    clear(viewContent);
    const meta = node('div', undefined, 'report-meta-header');
    const titleBlock = node('div');
    titleBlock.append(node('h4', report.title || 'Untitled report'), node('p', `${displayType(report)} • ${report.laboratory_name || 'Laboratory not specified'}`));
    const headerLine = node('div');
    headerLine.append(titleBlock, statusBadge(displayStatus(report)));
    meta.append(headerLine);
    const doctorLine = node('p');
    doctorLine.append(icon('fa-solid fa-user-doctor'), node('span', ` ${displayDoctor(report)} • ${report.report_date || ''}`));
    meta.append(doctorLine);
    viewContent.append(meta);
    const findings = report.findings || [];
    if (findings.length) {
        const findingList = node('div', undefined, 'findings-list');
        findings.forEach(finding => {
            const item = node('div', undefined, finding.is_normal ? 'finding-item' : 'finding-item abnormal');
            item.append(node('span', finding.label || '', 'finding-label'));
            const value = node('span', finding.value || '', 'finding-value');
            if (!finding.is_normal) value.append(icon('fa-solid fa-triangle-exclamation'));
            item.append(value);
            findingList.append(item);
        });
        viewContent.append(findingList);
    } else {
        viewContent.append(node('p', 'No specific findings structured yet.', 'report-empty-findings'));
    }
    const interpretation = node('div', undefined, 'interpretation-box');
    interpretation.append(node('strong', 'Doctor\'s Note'), node('p', report.interpretation || 'No interpretation provided.'));
    viewContent.append(interpretation);
    viewContent.append(detailRow('Attachment', report.has_attachment ? `${report.attachment_name || 'Protected file'} (${report.attachment_content_type || 'validated type'}, ${report.attachment_size || 0} bytes)` : 'No attachment'));
    downloadReportControl.disabled = !report.has_attachment;
    downloadReportControl.setAttribute('aria-disabled', String(!report.has_attachment));
    viewModal.classList.add('open');
};

async function downloadSelectedReport() {
    if (!selectedReport || !selectedReport.has_attachment) {
        showToast('No protected file is attached to this report.');
        return;
    }
    try {
        const response = await window.MediCareAuth.apiRequest(`/api/patient/reports/${selectedReport.id}/download/`);
        if (response.status === 401) {
            window.location.href = '../auth/login.html';
            return;
        }
        if (!response.ok) throw new Error(response.status === 403 ? 'You are not authorized to download this file.' : 'The protected file is unavailable.');
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = selectedReport.attachment_name || 'medical-report-file';
        document.body.append(anchor);
        anchor.click();
        anchor.remove();
        URL.revokeObjectURL(url);
    } catch (error) {
        showToast(error.message || 'Unable to download the protected file.');
    }
}

function setupModals() {
    const closeView = document.getElementById('closeViewModal');
    const uploadModal = document.getElementById('uploadReportModal');
    const btnUpload = document.getElementById('btnUploadReport');
    const closeUpload = document.getElementById('closeUploadModal');
    const btnCancelUpload = document.getElementById('btnCancelUpload');
    const uploadForm = document.getElementById('uploadReportForm');
    closeView.addEventListener('click', () => viewModal.classList.remove('open'));
    downloadReportControl.addEventListener('click', downloadSelectedReport);
    btnUpload.addEventListener('click', () => showToast('Patient clinical uploads are not enabled by the current policy.'));
    closeUpload.addEventListener('click', () => uploadModal.classList.remove('open'));
    btnCancelUpload.addEventListener('click', () => uploadModal.classList.remove('open'));
    uploadForm.addEventListener('submit', event => {
        event.preventDefault();
        uploadModal.classList.remove('open');
        showToast('Patient clinical uploads are not enabled by the current policy.');
    });
    window.addEventListener('click', event => {
        if (event.target === viewModal) viewModal.classList.remove('open');
        if (event.target === uploadModal) uploadModal.classList.remove('open');
    });
}

async function loadReports() {
    renderEmpty('Loading reports…', 'Retrieving your authorized reports.');
    try {
        const response = await window.MediCareAuth.apiRequest('/api/patient/reports/');
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '../auth/login.html';
                return;
            }
            if (response.status === 403) throw new Error('You are not authorized to view reports.');
            throw new Error('Unable to load reports.');
        }
        reports = await response.json();
        renderReports();
    } catch (error) {
        reports = [];
        renderEmpty('Unable to load reports', 'Please try again later.');
        showToast(error.message || 'Unable to load reports.');
    }
}

filterSearch.addEventListener('input', renderReports);
filterType.addEventListener('change', renderReports);
filterStatus.addEventListener('change', renderReports);
setupModals();
loadReports();
