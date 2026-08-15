// =========================================================
// SHARED UTILITIES
// =========================================================

function loadUserInfo() {
    const name = localStorage.getItem('userName') || 'Patient';
    const initials = name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
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
            const isDark = document.body.classList.contains('dark');
            localStorage.setItem('medicare-theme', isDark ? 'dark' : 'light');
            updateThemeIcon(isDark);
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

// =========================================================
// PRESCRIPTIONS DATA & LOGIC
// =========================================================

let prescriptions = [];
let prescriptionSummaries = [];
let currentTab = 'active';

function statusLabel(prescription) {
    return prescription.status_label || prescription.status || 'Active';
}

function displayDoctor(prescription) {
    return prescription.doctor_name || 'Not specified';
}

function daysBetween(startDate, endDate) {
    if (!startDate || !endDate) return { total: 1, used: 0 };
    const start = new Date(`${startDate}T00:00:00`);
    const end = new Date(`${endDate}T00:00:00`);
    const today = new Date();
    const total = Math.max(1, Math.round((end - start) / 86400000) + 1);
    const used = Math.min(total, Math.max(0, Math.round((today - start) / 86400000) + 1));
    return { total, used };
}

function flattenPrescriptions(data) {
    return data.flatMap(prescription => {
        const items = prescription.items && prescription.items.length ? prescription.items : [{}];
        return items.map((item, index) => {
            const startDate = item.start_date || prescription.start_date;
            const endDate = item.end_date || prescription.end_date;
            const progress = daysBetween(startDate, endDate);
            return {
                id: `${prescription.id}-${item.id || index}`,
                prescriptionId: prescription.id,
                medicine: item.medicine || 'Prescription',
                dosage: item.dosage || '',
                frequency: item.frequency || '',
                duration: item.duration || '',
                startDate,
                endDate,
                doctor: displayDoctor(prescription),
                status: statusLabel(prescription),
                daysTotal: progress.total,
                daysUsed: statusLabel(prescription) === 'Completed' ? progress.total : progress.used,
                instructions: item.instructions || 'No instructions provided.',
                sideEffects: item.side_effects || 'No side effects recorded.'
            };
        });
    });
}

function updateStats() {
    const stats = {
        Active: prescriptionSummaries.filter(p => statusLabel(p) === 'Active').length,
        Completed: prescriptionSummaries.filter(p => statusLabel(p) === 'Completed').length,
        'Refill Needed': prescriptionSummaries.filter(p => statusLabel(p) === 'Refill Needed').length
    };
    document.getElementById('statActive').textContent = stats.Active;
    document.getElementById('statCompleted').textContent = stats.Completed;
    document.getElementById('statRefill').textContent = stats['Refill Needed'];
}

function makeIcon(className) {
    const icon = document.createElement('i');
    icon.className = className;
    return icon;
}

function makeTextElement(tagName, className, text) {
    const element = document.createElement(tagName);
    if (className) element.className = className;
    element.textContent = text;
    return element;
}

function renderPrescriptions() {
    const grid = document.getElementById('prescriptionsGrid');
    const search = (document.getElementById('prescriptionsSearch').value || '').toLowerCase();
    const status = document.getElementById('statusFilter').value;
    const filtered = prescriptions.filter(p => {
        const matchesSearch = `${p.medicine} ${p.doctor}`.toLowerCase().includes(search);
        const matchesStatus = status === 'All' || p.status === status;
        const matchesTab = currentTab === 'all' || p.status === 'Active' || p.status === 'Refill Needed';
        return matchesSearch && matchesStatus && matchesTab;
    });

    grid.replaceChildren();
    updateStats();
    if (filtered.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'empty-state';
        empty.style.gridColumn = '1 / -1';
        empty.appendChild(makeIcon('fa-solid fa-pills'));
        empty.appendChild(makeTextElement('h3', '', 'No prescriptions found'));
        empty.appendChild(makeTextElement('p', '', 'Try adjusting your search or filters.'));
        grid.appendChild(empty);
        return;
    }

    filtered.forEach(p => {
        const remainingDays = Math.max(0, p.daysTotal - p.daysUsed);
        const progressPct = Math.min(100, Math.max(0, (p.daysUsed / Math.max(1, p.daysTotal)) * 100));
        let statusClass = 'badge-success';
        let iconClass = 'active-icon';
        if (p.status === 'Completed') {
            statusClass = 'badge-primary';
            iconClass = 'completed-icon';
        } else if (p.status === 'Refill Needed') {
            statusClass = 'badge-warning';
            iconClass = 'refill-icon';
        }
        let progressColor = 'progress-good';
        if (p.status === 'Completed') progressColor = 'progress-completed';
        else if (100 - progressPct < 25) progressColor = 'progress-low';
        else if (100 - progressPct < 50) progressColor = 'progress-medium';

        const card = document.createElement('div');
        card.className = 'prescription-card';
        const header = document.createElement('div');
        header.className = 'presc-header';
        const medInfo = document.createElement('div');
        medInfo.className = 'presc-med-info';
        const icon = document.createElement('div');
        icon.className = `presc-icon ${iconClass}`;
        icon.appendChild(makeIcon('fa-solid fa-pills'));
        const titles = document.createElement('div');
        titles.className = 'presc-titles';
        const title = document.createElement('h3');
        title.appendChild(document.createTextNode(`${p.medicine} `));
        const dosage = makeTextElement('span', '', p.dosage);
        dosage.style.cssText = 'font-size: 13px; font-weight: 400; color: var(--text-secondary)';
        title.appendChild(dosage);
        titles.appendChild(title);
        titles.appendChild(makeTextElement('p', '', p.frequency));
        medInfo.append(icon, titles);
        header.append(medInfo, makeTextElement('span', `badge ${statusClass}`, p.status));

        const body = document.createElement('div');
        body.className = 'presc-body';
        const doctorRow = document.createElement('div');
        doctorRow.className = 'presc-detail-row';
        doctorRow.append(makeIcon('fa-solid fa-user-doctor'));
        const doctorText = makeTextElement('span', '', 'Prescribed by: ');
        doctorText.appendChild(makeTextElement('strong', '', p.doctor));
        doctorRow.appendChild(doctorText);
        const durationRow = document.createElement('div');
        durationRow.className = 'presc-detail-row';
        durationRow.append(makeIcon('fa-regular fa-calendar-days'));
        const durationText = makeTextElement('span', '', 'Duration: ');
        durationText.appendChild(makeTextElement('strong', '', p.duration || 'Not specified'));
        durationText.appendChild(document.createTextNode(` (${p.startDate || ''} to ${p.endDate || ''})`));
        durationRow.appendChild(durationText);
        const progressSection = document.createElement('div');
        progressSection.className = 'progress-section';
        const progressHeader = document.createElement('div');
        progressHeader.className = 'progress-header';
        progressHeader.append(makeTextElement('span', '', 'Course Progress'), makeTextElement('span', '', p.status === 'Completed' ? 'Completed' : `${remainingDays} days left`));
        const progressWrap = document.createElement('div');
        progressWrap.className = 'progress-bar-wrap';
        const progressFill = document.createElement('div');
        progressFill.className = `progress-bar-fill ${progressColor}`;
        progressFill.style.width = `${progressPct}%`;
        progressWrap.appendChild(progressFill);
        progressSection.append(progressHeader, progressWrap);
        body.append(doctorRow, durationRow, progressSection);

        const footer = document.createElement('div');
        footer.className = 'presc-footer';
        if (p.status === 'Refill Needed') {
            const refillButton = document.createElement('button');
            refillButton.className = 'btn-primary';
            refillButton.type = 'button';
            refillButton.append(makeIcon('fa-solid fa-rotate'), document.createTextNode(' Request Refill'));
            refillButton.addEventListener('click', () => window.requestRefill(p.medicine));
            footer.appendChild(refillButton);
        }
        const detailsButton = document.createElement('button');
        detailsButton.className = 'btn-secondary';
        detailsButton.type = 'button';
        detailsButton.textContent = 'View Details';
        detailsButton.addEventListener('click', () => window.viewDetails(p.id));
        footer.appendChild(detailsButton);
        card.append(header, body, footer);
        grid.appendChild(card);
    });
}

window.viewDetails = function(id) {
    const p = prescriptions.find(item => item.id === id);
    if (!p) return;
    let iconClass = 'active-icon';
    if (p.status === 'Completed') iconClass = 'completed-icon';
    if (p.status === 'Refill Needed') iconClass = 'refill-icon';
    const modalContent = document.getElementById('modalContent');
    modalContent.replaceChildren();
    const header = document.createElement('div');
    header.className = 'modal-presc-header';
    const icon = document.createElement('div');
    icon.className = `presc-icon ${iconClass}`;
    icon.style.cssText = 'width: 55px; height: 55px; font-size: 24px;';
    icon.appendChild(makeIcon('fa-solid fa-pills'));
    const titleGroup = document.createElement('div');
    titleGroup.appendChild(makeTextElement('h3', '', p.medicine));
    titleGroup.firstChild.style.cssText = 'font-size: 18px; margin-bottom: 2px;';
    const subtitle = makeTextElement('p', '', `${p.dosage} • ${p.frequency}`);
    subtitle.style.cssText = 'color: var(--text-secondary); font-size: 14px;';
    titleGroup.appendChild(subtitle);
    header.append(icon, titleGroup);
    const instructions = document.createElement('div');
    instructions.className = 'modal-detail-block';
    instructions.append(makeTextElement('h4', '', "Doctor's Instructions"), makeTextElement('p', '', p.instructions));
    const sideEffects = document.createElement('div');
    sideEffects.className = 'modal-detail-block';
    sideEffects.style.cssText = 'background: var(--warning-soft); border-color: rgba(217, 119, 6, 0.2);';
    const sideTitle = makeTextElement('h4', '', 'Possible Side Effects');
    sideTitle.style.color = 'var(--warning)';
    sideEffects.append(sideTitle, makeTextElement('p', '', p.sideEffects));
    const metadata = document.createElement('div');
    metadata.style.cssText = 'display: grid; grid-template-columns: 1fr 1fr; gap: 15px;';
    const prescriber = document.createElement('div');
    prescriber.className = 'modal-detail-block';
    const prescriberText = makeTextElement('p', '', '');
    prescriberText.append(makeIcon('fa-solid fa-user-doctor'), document.createTextNode(' '), document.createTextNode(p.doctor));
    prescriber.append(makeTextElement('h4', '', 'Prescriber'), prescriberText);
    const timeline = document.createElement('div');
    timeline.className = 'modal-detail-block';
    const timelineText = makeTextElement('p', '', '');
    timelineText.append(makeIcon('fa-regular fa-calendar'), document.createTextNode(` ${p.startDate || ''} to ${p.endDate || ''}`));
    timeline.append(makeTextElement('h4', '', 'Timeline'), timelineText);
    metadata.append(prescriber, timeline);
    modalContent.append(header, instructions, sideEffects, metadata);
    document.getElementById('detailsModal').classList.add('open');
};

window.closeDetailsModal = function() {
    document.getElementById('detailsModal').classList.remove('open');
};

window.requestRefill = function(medicine) {
    showToast(`Refill request for ${medicine} is deferred until a refill workflow is implemented.`, 'success');
};

function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.append(makeIcon('fa-solid fa-circle-info'), makeTextElement('span', '', message));
    container.appendChild(toast);
    setTimeout(() => { if (toast.parentNode) toast.parentNode.removeChild(toast); }, 3000);
}

async function loadPrescriptions() {
    const grid = document.getElementById('prescriptionsGrid');
    grid.replaceChildren();
    const loading = document.createElement('div');
    loading.className = 'empty-state';
    loading.style.gridColumn = '1 / -1';
    loading.appendChild(makeTextElement('p', '', 'Loading prescriptions…'));
    grid.appendChild(loading);
    try {
        const response = await window.MediCareAuth.apiRequest('/api/patient/prescriptions/');
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '../auth/login.html';
                return;
            }
            if (response.status === 403) throw new Error('You are not authorized to view prescriptions.');
            throw new Error('Unable to load prescriptions.');
        }
        prescriptionSummaries = await response.json();
        prescriptions = flattenPrescriptions(prescriptionSummaries);
        renderPrescriptions();
    } catch (error) {
        prescriptionSummaries = [];
        prescriptions = [];
        renderPrescriptions();
        showToast(error.message || 'Unable to load prescriptions.', 'info');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.tab').forEach(tab => tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(item => item.classList.remove('active'));
        tab.classList.add('active');
        currentTab = tab.dataset.tab;
        renderPrescriptions();
    }));
    document.getElementById('prescriptionsSearch').addEventListener('input', renderPrescriptions);
    document.getElementById('statusFilter').addEventListener('change', renderPrescriptions);
    document.getElementById('closeModal').addEventListener('click', closeDetailsModal);
    document.getElementById('detailsModal').addEventListener('click', event => {
        if (event.target.id === 'detailsModal') closeDetailsModal();
    });
    renderPrescriptions();
    loadPrescriptions();
});
