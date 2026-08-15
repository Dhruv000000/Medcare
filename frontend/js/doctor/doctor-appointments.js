/* DOCTOR APPOINTMENTS PAGE — relies on shared helpers loaded by doctor-dashboard.js */

function renderAppointmentActions(appointment) {
    const container = document.createElement('div');
    container.className = 'action-bar';
    const actionsByStatus = {
        pending: [['confirm', 'Confirm'], ['reject', 'Reject']],
        confirmed: [['complete', 'Complete'], ['cancel', 'Cancel']],
    };
    (actionsByStatus[appointment.status] || []).forEach(([action, label]) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = action;
        button.dataset.appointmentId = String(appointment.id);
        button.dataset.action = action;
        button.textContent = label;
        container.appendChild(button);
    });
    if (!container.children.length) {
        container.textContent = '—';
    }
    return container;
}

function renderAppointmentsTable(appointments) {
    const tbody = document.querySelector('#doctorAppointmentsTable tbody');
    if (!tbody) return;
    while (tbody.firstChild) tbody.removeChild(tbody.firstChild);
    if (!appointments.length) {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = 6;
        cell.className = 'empty-state';
        cell.textContent = 'No appointments match the current filters.';
        row.appendChild(cell);
        tbody.appendChild(row);
        return;
    }
    appointments.forEach(appointment => {
        const row = document.createElement('tr');

        const patientCell = document.createElement('td');
        patientCell.textContent = appointment.patient_name || 'Patient';

        const dateCell = document.createElement('td');
        dateCell.textContent = displayDate(appointment.scheduled_date);

        const timeCell = document.createElement('td');
        timeCell.textContent = displayTime(appointment.scheduled_time);

        const reasonCell = document.createElement('td');
        reasonCell.textContent = appointment.reason || '—';

        const statusCell = document.createElement('td');
        const statusBadge = document.createElement('span');
        statusBadge.className = `status ${appointment.status}`;
        statusBadge.textContent = appointment.status_label || displayStatus(appointment.status);
        statusCell.appendChild(statusBadge);

        const actionCell = document.createElement('td');
        actionCell.appendChild(renderAppointmentActions(appointment));

        row.append(patientCell, dateCell, timeCell, reasonCell, statusCell, actionCell);
        tbody.appendChild(row);
    });
}

let allAppointments = [];

function applyAppointmentFilters() {
    const query = document.getElementById('appointmentSearch')?.value.toLowerCase().trim() || '';
    const filtered = allAppointments.filter(appointment => {
        if (!query) return true;
        return (appointment.patient_name || '').toLowerCase().includes(query) ||
            (appointment.reason || '').toLowerCase().includes(query);
    });
    renderAppointmentsTable(filtered);
}

async function loadAppointmentsList() {
    const tbody = document.querySelector('#doctorAppointmentsTable tbody');
    if (tbody) {
        tbody.replaceChildren();
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = 6;
        cell.className = 'empty-state';
        cell.textContent = 'Loading appointments…';
        row.appendChild(cell);
        tbody.appendChild(row);
    }
    try {
        const status = document.getElementById('appointmentStatusFilter')?.value || '';
        const response = await apiRequest(`/api/doctor/appointments/${status ? `?status=${encodeURIComponent(status)}` : ''}`);
        if (response.status === 401) {
            window.location.href = '../auth/login.html';
            return;
        }
        const payload = await response.json().catch(() => []);
        if (!response.ok) throw new Error(errorMessage(payload, 'Unable to load appointments.'));
        allAppointments = Array.isArray(payload) ? payload : [];
        applyAppointmentFilters();
    } catch (error) {
        const errTbody = document.querySelector('#doctorAppointmentsTable tbody');
        if (errTbody) {
            errTbody.replaceChildren();
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = 6;
            cell.className = 'empty-state';
            cell.textContent = error.message || 'Unable to load appointments.';
            row.appendChild(cell);
            errTbody.appendChild(row);
        }
        showToast(error.message || 'Unable to load appointments.');
    }
}

async function transitionDoctorAppointment(id, action) {
    try {
        const response = await apiRequest(`/api/doctor/appointments/${id}/transition/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action }),
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(errorMessage(payload, 'Unable to update appointment.'));
        showToast(`Appointment ${displayStatus(payload.status).toLowerCase()}.`);
        await loadAppointmentsList();
    } catch (error) {
        showToast(error.message || 'Unable to update appointment.');
    }
}

document.querySelector('#doctorAppointmentsTable')?.addEventListener('click', event => {
    const button = event.target.closest('[data-action]');
    if (!button) return;
    transitionDoctorAppointment(button.dataset.appointmentId, button.dataset.action);
});

document.getElementById('appointmentSearch')?.addEventListener('input', applyAppointmentFilters);
document.getElementById('appointmentStatusFilter')?.addEventListener('change', loadAppointmentsList);

document.addEventListener('DOMContentLoaded', loadAppointmentsList);
