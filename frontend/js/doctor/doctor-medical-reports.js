/* DOCTOR MEDICAL REPORTS PAGE — relies on shared helpers loaded by doctor-dashboard.js */

let allReports = [];

function renderReportsTable(reports) {
    const tbody = document.querySelector('#doctorReportsTable tbody');
    if (!tbody) return;
    while (tbody.firstChild) tbody.removeChild(tbody.firstChild);
    if (!reports.length) {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = 6;
        cell.className = 'empty-state';
        cell.textContent = 'No authorized reports found.';
        row.appendChild(cell);
        tbody.appendChild(row);
        return;
    }
    reports.forEach(report => {
        const row = document.createElement('tr');

        const patientCell = document.createElement('td');
        patientCell.textContent = report.patient_name || 'Patient';

        const titleCell = document.createElement('td');
        titleCell.textContent = report.title || 'Medical report';

        const typeCell = document.createElement('td');
        typeCell.textContent = report.report_type_label || report.report_type || '—';

        const dateCell = document.createElement('td');
        dateCell.textContent = displayDate(report.report_date);

        const statusCell = document.createElement('td');
        const statusBadge = document.createElement('span');
        statusBadge.className = `status ${report.status}`;
        statusBadge.textContent = report.status_label || displayStatus(report.status);
        statusCell.appendChild(statusBadge);

        const actionCell = document.createElement('td');
        if (report.has_attachment) {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'view-btn';
            button.dataset.reportId = String(report.id);
            button.dataset.filename = report.attachment_name || 'report';
            button.textContent = 'Download';
            actionCell.appendChild(button);
        } else {
            actionCell.textContent = '—';
        }

        row.append(patientCell, titleCell, typeCell, dateCell, statusCell, actionCell);
        tbody.appendChild(row);
    });
}

function applyReportFilters() {
    const query = document.getElementById('reportSearch')?.value.toLowerCase().trim() || '';
    const filtered = allReports.filter(report => {
        if (!query) return true;
        return (report.patient_name || '').toLowerCase().includes(query) ||
            (report.title || '').toLowerCase().includes(query);
    });
    renderReportsTable(filtered);
}

async function loadReportsList() {
    try {
        const response = await apiRequest('/api/doctor/reports/');
        if (response.status === 401) {
            window.location.href = '../auth/login.html';
            return;
        }
        const payload = await response.json().catch(() => []);
        if (!response.ok) throw new Error(errorMessage(payload, 'Unable to load reports.'));
        allReports = Array.isArray(payload) ? payload : [];
        applyReportFilters();
    } catch (error) {
        const tbody = document.querySelector('#doctorReportsTable tbody');
        if (tbody) {
            tbody.replaceChildren();
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = 6;
            cell.className = 'empty-state';
            cell.textContent = error.message || 'Unable to load reports.';
            row.appendChild(cell);
            tbody.appendChild(row);
        }
        showToast(error.message || 'Unable to load reports.');
    }
}

async function downloadDoctorReport(id, filename) {
    try {
        const response = await apiRequest(`/api/doctor/reports/${id}/download/`);
        if (response.status === 401) {
            window.location.href = '../auth/login.html';
            return;
        }
        if (!response.ok) throw new Error(response.status === 403 ? 'You are not authorized to download this file.' : 'The protected file is unavailable.');
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = filename || 'report';
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        URL.revokeObjectURL(url);
    } catch (error) {
        showToast(error.message || 'Unable to download the report.');
    }
}

document.querySelector('#doctorReportsTable')?.addEventListener('click', event => {
    const button = event.target.closest('[data-report-id]');
    if (!button) return;
    downloadDoctorReport(button.dataset.reportId, button.dataset.filename);
});

document.getElementById('reportSearch')?.addEventListener('input', applyReportFilters);

document.addEventListener('DOMContentLoaded', loadReportsList);
