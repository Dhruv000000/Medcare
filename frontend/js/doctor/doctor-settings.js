/* DOCTOR SETTINGS PAGE (read-only profile) — relies on shared helpers loaded by doctor-dashboard.js */

function renderDoctorProfileTable(doctor) {
    const container = document.getElementById('doctorProfileTable');
    if (!container) return;
    const rows = [
        ['Name', `Dr. ${doctor.first_name || ''} ${doctor.last_name || ''}`.trim()],
        ['Email', doctor.email || '—'],
        ['Specialization', doctor.specialization || '—'],
        ['License ID', doctor.license_id || '—'],
        ['Contact details', doctor.contact_details || '—'],
    ];
    const table = document.createElement('table');
    const tbody = document.createElement('tbody');
    rows.forEach(([label, value]) => {
        const row = document.createElement('tr');
        const th = document.createElement('th');
        th.textContent = label;
        const td = document.createElement('td');
        td.textContent = value;
        row.append(th, td);
        tbody.appendChild(row);
    });
    table.appendChild(tbody);
    container.replaceChildren(table);
}

async function loadDoctorProfilePage() {
    const container = document.getElementById('doctorProfileTable');
    try {
        const response = await apiRequest('/api/doctor/profile/');
        if (response.status === 401) {
            window.location.href = '../auth/login.html';
            return;
        }
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(errorMessage(payload, 'Unable to load your profile.'));
        renderDoctorProfileTable(payload);
    } catch (error) {
        if (container) {
            const status = document.createElement('p');
            status.className = 'clinical-records-status is-error';
            status.textContent = error.message || 'Unable to load your profile.';
            container.replaceChildren(status);
        }
        showToast(error.message || 'Unable to load your profile.');
    }
}

document.addEventListener('DOMContentLoaded', loadDoctorProfilePage);
