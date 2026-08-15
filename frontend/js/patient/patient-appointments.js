// =========================================================
// SHARED UTILITIES
// =========================================================

function loadUserInfo() {
    const name = localStorage.getItem('userName') || 'Patient';
    const initials = name.split(' ').map((part) => part[0]).join('').toUpperCase().slice(0, 2);
    ['sidebarName', 'topbarName'].forEach((id) => {
        const element = document.getElementById(id);
        if (element) element.textContent = name;
    });
    ['sidebarAvatar', 'topbarAvatar'].forEach((id) => {
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
    const icon = button?.querySelector('i');
    if (icon) icon.className = isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
}

loadUserInfo();
initTheme();

// =========================================================
// PATIENT APPOINTMENTS API
// =========================================================

let appointments = [];
let doctors = [];
let selectedTime = null;
const timeSlots = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '14:00', '14:30', '15:00', '15:30'];

function apiRequest(path, options = {}) {
    if (window.MediCareAuth?.apiRequest) return window.MediCareAuth.apiRequest(path, options);
    return Promise.reject(new Error('Unable to connect to the server.'));
}

function escapeHTML(value) {
    return String(value ?? '').replace(/[&<>'"]/g, (character) => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[character]));
}

function statusLabel(status) {
    return {
        pending: 'Pending',
        confirmed: 'Confirmed',
        rejected: 'Rejected',
        cancelled: 'Cancelled',
        completed: 'Completed',
    }[status] || status;
}

function displayDate(value) {
    if (!value) return '—';
    return new Date(`${value}T00:00:00`).toLocaleDateString(undefined, {
        day: '2-digit', month: 'short', year: 'numeric'
    });
}

function displayTime(value) {
    if (!value) return '—';
    const [hours, minutes] = value.slice(0, 5).split(':').map(Number);
    const suffix = hours >= 12 ? 'PM' : 'AM';
    const displayHour = hours % 12 || 12;
    return `${String(displayHour).padStart(2, '0')}:${String(minutes).padStart(2, '0')} ${suffix}`;
}

function getErrorMessage(payload, fallback) {
    if (payload?.detail) return payload.detail;
    return Object.values(payload || {}).flatMap((value) => Array.isArray(value) ? value : [value]).join(' ') || fallback;
}

async function loadDoctors() {
    const select = document.getElementById('bookDoctor');
    try {
        const response = await apiRequest('/api/patient/doctors/');
        const payload = await response.json();
        if (!response.ok) throw new Error(getErrorMessage(payload, 'Unable to load doctors.'));
        doctors = payload;
        select.innerHTML = doctors.length
            ? doctors.map((doctor) => `<option value="${doctor.id}">${escapeHTML(doctor.name)} (${escapeHTML(doctor.specialization)})</option>`).join('')
            : '<option value="">No doctors available</option>';
    } catch (error) {
        select.innerHTML = '<option value="">Unable to load doctors</option>';
        showToast(error.message || 'Unable to load doctors.');
    }
}

async function loadAppointments() {
    const list = document.getElementById('appointmentsList');
    list.innerHTML = '<div class="empty-state"><p>Loading appointments...</p></div>';
    try {
        const response = await apiRequest('/api/patient/appointments/');
        const payload = await response.json();
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '../auth/login.html';
                return;
            }
            if (response.status === 403) throw new Error('You are not authorized to view appointments.');
            throw new Error(getErrorMessage(payload, 'Unable to load appointments.'));
        }
        appointments = payload;
        renderStats();
        renderAppointments();
    } catch (error) {
        list.innerHTML = '<div class="empty-state"><h3>Appointments unavailable</h3><p>Please try again later.</p></div>';
        showToast(error.message || 'Unable to load appointments.');
    }
}

function renderStats() {
    const upcoming = appointments.filter((appointment) => ['pending', 'confirmed'].includes(appointment.status)).length;
    const completed = appointments.filter((appointment) => appointment.status === 'completed').length;
    const cancelled = appointments.filter((appointment) => ['cancelled', 'rejected'].includes(appointment.status)).length;
    const statsGrid = document.getElementById('statsGrid');
    statsGrid.innerHTML = `
        <div class="stat-card"><div class="stat-icon upcoming"><i class="fa-solid fa-calendar-check"></i></div><div class="stat-info"><h3>${upcoming}</h3><p>Upcoming</p></div></div>
        <div class="stat-card"><div class="stat-icon completed"><i class="fa-solid fa-check-double"></i></div><div class="stat-info"><h3>${completed}</h3><p>Completed</p></div></div>
        <div class="stat-card"><div class="stat-icon cancelled"><i class="fa-solid fa-calendar-xmark"></i></div><div class="stat-info"><h3>${cancelled}</h3><p>Cancelled</p></div></div>
    `;
}

function renderAppointments() {
    const search = document.getElementById('filterSearch').value.toLowerCase().trim();
    const filter = document.getElementById('filterStatus').value;
    const list = document.getElementById('appointmentsList');
    const filtered = appointments.filter((appointment) => {
        const haystack = `${appointment.doctor_name} ${appointment.reason}`.toLowerCase();
        const statusMatches = filter === 'All' ||
            (filter === 'Upcoming' && ['pending', 'confirmed'].includes(appointment.status)) ||
            statusLabel(appointment.status) === filter;
        return haystack.includes(search) && statusMatches;
    });

    if (!filtered.length) {
        list.innerHTML = '<div class="empty-state"><i class="fa-solid fa-calendar-xmark"></i><h3>No appointments found</h3><p>Try adjusting your search or filters.</p></div>';
        return;
    }

    list.innerHTML = filtered.map((appointment) => {
        const label = statusLabel(appointment.status);
        const badgeClass = ['pending', 'confirmed'].includes(appointment.status) ? 'badge-primary' : appointment.status === 'completed' ? 'badge-success' : 'badge-danger';
        const actions = ['pending', 'confirmed'].includes(appointment.status)
            ? `<button class="btn-secondary" onclick="viewDetails(${appointment.id})">View Details</button><button class="btn-danger" onclick="cancelApt(${appointment.id})">Cancel</button>`
            : `<button class="btn-secondary" onclick="viewDetails(${appointment.id})">View Details</button>`;
        const initials = (appointment.doctor_name || 'DR').replace(/^Dr\. /, '').split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase();
        return `
            <div class="appointment-card status-${escapeHTML(appointment.status)}">
                <div class="apt-main-info"><div class="doc-avatar">${escapeHTML(initials)}</div><div class="doc-details"><h4>${escapeHTML(appointment.doctor_name)}</h4><p>${escapeHTML(appointment.doctor_specialization)}</p></div></div>
                <div class="apt-meta"><div class="apt-meta-item"><i class="fa-regular fa-calendar"></i><span>${escapeHTML(displayDate(appointment.scheduled_date))}</span></div><div class="apt-meta-item"><i class="fa-regular fa-clock"></i><span>${escapeHTML(displayTime(appointment.scheduled_time))}</span></div><span class="badge ${badgeClass}">${escapeHTML(label)}</span></div>
                <div class="apt-actions">${actions}</div>
            </div>`;
    }).join('');
}

function populateBookModal() {
    const timeGrid = document.getElementById('bookTimeSlots');
    timeGrid.innerHTML = timeSlots.map((time) => `<button type="button" class="time-slot" data-time="${time}">${time}</button>`).join('');
    timeGrid.querySelectorAll('.time-slot').forEach((slot) => {
        slot.addEventListener('click', () => {
            timeGrid.querySelectorAll('.time-slot').forEach((item) => item.classList.remove('selected'));
            slot.classList.add('selected');
            selectedTime = slot.dataset.time;
        });
    });
}

function openBookModal() {
    document.getElementById('bookModal').classList.add('open');
    document.getElementById('bookDate').value = '';
    document.getElementById('bookReason').value = '';
    selectedTime = null;
    document.querySelectorAll('.time-slot').forEach((slot) => slot.classList.remove('selected'));
}

function closeBookModal() {
    document.getElementById('bookModal').classList.remove('open');
}

async function handleBookAppointment() {
    const doctorId = document.getElementById('bookDoctor').value;
    const scheduledDate = document.getElementById('bookDate').value;
    const reason = document.getElementById('bookReason').value.trim();
    if (!doctorId || !scheduledDate || !selectedTime) {
        showToast('Please select doctor, date, and time.');
        return;
    }
    const submitButton = document.getElementById('btnConfirmBook');
    if (submitButton) submitButton.disabled = true;
    try {
        const response = await apiRequest('/api/patient/appointments/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ doctor_id: Number(doctorId), scheduled_date: scheduledDate, scheduled_time: selectedTime, reason }),
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(getErrorMessage(payload, 'Unable to book appointment.'));
        closeBookModal();
        showToast('Appointment request submitted.');
        await loadAppointments();
    } catch (error) {
        showToast(error.message || 'Unable to book appointment.');
    } finally {
        if (submitButton) submitButton.disabled = false;
    }
}

async function cancelApt(id) {
    if (!confirm('Are you sure you want to cancel this appointment?')) return;
    try {
        const response = await apiRequest(`/api/patient/appointments/${id}/cancel/`, { method: 'POST' });
        const payload = await response.json();
        if (!response.ok) throw new Error(getErrorMessage(payload, 'Unable to cancel appointment.'));
        showToast('Appointment cancelled.');
        await loadAppointments();
    } catch (error) {
        showToast(error.message || 'Unable to cancel appointment.');
    }
}

function rescheduleApt() {
    showToast('Rescheduling is not available yet.');
}

function viewDetails(id) {
    const appointment = appointments.find((item) => item.id === id);
    if (!appointment) return;
    const content = document.getElementById('detailsModalContent');
    content.innerHTML = `
        <div class="details-info">
            <div class="detail-item"><label>Doctor</label><p>${escapeHTML(appointment.doctor_name)} (${escapeHTML(appointment.doctor_specialization)})</p></div>
            <div class="detail-item"><label>Date & Time</label><p>${escapeHTML(displayDate(appointment.scheduled_date))} at ${escapeHTML(displayTime(appointment.scheduled_time))}</p></div>
            <div class="detail-item"><label>Status</label><p><span class="badge badge-success">${escapeHTML(statusLabel(appointment.status))}</span></p></div>
            <div class="detail-item"><label>Reason for Visit</label><p>${escapeHTML(appointment.reason || 'Not provided')}</p></div>
            <div class="detail-item"><label>Notes</label><p>${escapeHTML(appointment.notes || 'No notes available.')}</p></div>
        </div>`;
    document.getElementById('detailsModal').classList.add('open');
}

function closeDetailsModal() {
    document.getElementById('detailsModal').classList.remove('open');
}

function showToast(message) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('hiding');
        toast.addEventListener('animationend', () => toast.remove());
    }, 3000);
}

window.cancelApt = cancelApt;
window.rescheduleApt = rescheduleApt;
window.viewDetails = viewDetails;

document.addEventListener('DOMContentLoaded', async () => {
    populateBookModal();
    document.getElementById('filterSearch').addEventListener('input', renderAppointments);
    document.getElementById('filterStatus').addEventListener('change', renderAppointments);
    document.getElementById('btnBookAppointment').addEventListener('click', openBookModal);
    document.getElementById('closeBookModal').addEventListener('click', closeBookModal);
    document.getElementById('btnCancelBook').addEventListener('click', closeBookModal);
    document.getElementById('btnConfirmBook').addEventListener('click', handleBookAppointment);
    document.getElementById('closeDetailsModal').addEventListener('click', closeDetailsModal);
    document.getElementById('btnDismissDetails').addEventListener('click', closeDetailsModal);
    await Promise.all([loadDoctors(), loadAppointments()]);
});
