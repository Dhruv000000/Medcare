/* DOCTOR PRESCRIPTIONS PAGE — relies on shared helpers loaded by doctor-dashboard.js */

let allPrescriptions = [];

function renderPrescriptionsTable(prescriptions) {
    const tbody = document.querySelector('#doctorPrescriptionsTable tbody');
    if (!tbody) return;
    while (tbody.firstChild) tbody.removeChild(tbody.firstChild);
    if (!prescriptions.length) {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = 5;
        cell.className = 'empty-state';
        cell.textContent = 'No authorized prescriptions found.';
        row.appendChild(cell);
        tbody.appendChild(row);
        return;
    }
    prescriptions.forEach(prescription => {
        const row = document.createElement('tr');

        const patientCell = document.createElement('td');
        patientCell.textContent = prescription.patient_name || 'Patient';

        const medicinesCell = document.createElement('td');
        const items = Array.isArray(prescription.items) ? prescription.items : [];
        medicinesCell.textContent = items.length
            ? items.map(item => `${item.medicine} (${item.dosage})`).join(', ')
            : '—';

        const issuedCell = document.createElement('td');
        issuedCell.textContent = displayDate(prescription.issued_on);

        const rangeCell = document.createElement('td');
        rangeCell.textContent = `${displayDate(prescription.start_date)} – ${prescription.end_date ? displayDate(prescription.end_date) : 'ongoing'}`;

        const statusCell = document.createElement('td');
        const statusBadge = document.createElement('span');
        statusBadge.className = `status ${prescription.status}`;
        statusBadge.textContent = prescription.status_label || displayStatus(prescription.status);
        statusCell.appendChild(statusBadge);

        row.append(patientCell, medicinesCell, issuedCell, rangeCell, statusCell);
        tbody.appendChild(row);
    });
}

function applyPrescriptionFilters() {
    const query = document.getElementById('prescriptionSearch')?.value.toLowerCase().trim() || '';
    const filtered = allPrescriptions.filter(prescription => {
        if (!query) return true;
        const medicines = (prescription.items || []).map(item => item.medicine || '').join(' ').toLowerCase();
        return (prescription.patient_name || '').toLowerCase().includes(query) || medicines.includes(query);
    });
    renderPrescriptionsTable(filtered);
}

async function loadPrescriptionsList() {
    try {
        const response = await apiRequest('/api/doctor/prescriptions/');
        if (response.status === 401) {
            window.location.href = '../auth/login.html';
            return;
        }
        const payload = await response.json().catch(() => []);
        if (!response.ok) throw new Error(errorMessage(payload, 'Unable to load prescriptions.'));
        allPrescriptions = Array.isArray(payload) ? payload : [];
        applyPrescriptionFilters();
    } catch (error) {
        const tbody = document.querySelector('#doctorPrescriptionsTable tbody');
        if (tbody) {
            tbody.replaceChildren();
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = 5;
            cell.className = 'empty-state';
            cell.textContent = error.message || 'Unable to load prescriptions.';
            row.appendChild(cell);
            tbody.appendChild(row);
        }
        showToast(error.message || 'Unable to load prescriptions.');
    }
}

document.getElementById('prescriptionSearch')?.addEventListener('input', applyPrescriptionFilters);

document.addEventListener('DOMContentLoaded', loadPrescriptionsList);
