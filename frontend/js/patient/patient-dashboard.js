// =========================================================
// MEDICARE - PATIENT DASHBOARD
// =========================================================

const body = document.body;
const themeToggle = document.getElementById('themeToggle');
const searchInput = document.querySelector('.search-box input');
const notificationButton = document.querySelector('.notification');
const recentActivityList = document.getElementById('recentActivityList');

function escapeHTML(value) {
    return String(value ?? '').replace(/[&<>'"]/g, character => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[character]));
}

function getErrorMessage(payload, fallback) {
    if (payload?.detail) return payload.detail;
    const messages = Object.values(payload || {}).flatMap(value => Array.isArray(value) ? value : [value]).filter(Boolean);
    return messages.join(' ') || fallback;
}

function showDashboardMessage(message) {
    if (recentActivityList) {
        recentActivityList.innerHTML = `<div class="activity-item"><div class="activity-content"><strong>${escapeHTML(message)}</strong><span>Please try again later.</span></div></div>`;
    }
}

function formatActivityDate(value) {
    if (!value) return '—';
    return new Date(`${value}T00:00:00`).toLocaleDateString(undefined, { day: '2-digit', month: 'short', year: 'numeric' });
}

function renderRecentActivity(activity) {
    if (!recentActivityList) return;
    if (!activity.length) {
        recentActivityList.innerHTML = '<div class="activity-item"><div class="activity-content"><strong>No recent activity</strong><span>Your recent backend activity will appear here.</span></div></div>';
        return;
    }
    recentActivityList.innerHTML = activity.map(item => `
        <div class="activity-item">
            <div class="activity-icon"><i class="fa-solid ${escapeHTML(item.icon)}"></i></div>
            <div class="activity-content"><strong>${escapeHTML(item.title)}</strong><span>${escapeHTML(item.subtitle)}</span></div>
            <small>${escapeHTML(formatActivityDate(item.activity_date))}</small>
        </div>
    `).join('');
}

function renderDashboard(summary) {
    const values = {
        upcomingAppointmentCount: summary.upcoming_appointment_count ?? 0,
        medicalRecordCount: summary.medical_record_count ?? 0,
        activePrescriptionCount: summary.active_prescription_count ?? 0,
    };
    Object.entries(values).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    });
    const healthStatus = document.getElementById('patientHealthStatus');
    if (healthStatus) {
        healthStatus.textContent = 'Not available';
        healthStatus.classList.remove('health-good');
    }
    renderRecentActivity(summary.recent_activity || []);
}

async function loadPatientDashboard() {
    if (!window.MediCareAuth?.apiRequest) {
        showDashboardMessage('Dashboard unavailable');
        return;
    }
    ['upcomingAppointmentCount', 'medicalRecordCount', 'activePrescriptionCount'].forEach(id => {
        const element = document.getElementById(id);
        if (element) element.textContent = '…';
    });
    showDashboardMessage('Loading recent activity…');
    try {
        const response = await window.MediCareAuth.apiRequest('/api/patient/dashboard/');
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '../auth/login.html';
                return;
            }
            if (response.status === 403) throw new Error('You are not authorized to view this dashboard.');
            throw new Error(getErrorMessage(payload, 'Unable to load patient dashboard.'));
        }
        renderDashboard(payload);
    } catch (error) {
        showDashboardMessage(error.message || 'Unable to connect to the server.');
    }
}

function initTheme() {
    const savedTheme = localStorage.getItem('medicare-theme');
    const isDark = savedTheme === 'dark';
    body.classList.toggle('dark', isDark);
    updateThemeIcon(isDark);
    themeToggle?.addEventListener('click', () => {
        const nextDark = !body.classList.contains('dark');
        body.classList.toggle('dark', nextDark);
        localStorage.setItem('medicare-theme', nextDark ? 'dark' : 'light');
        updateThemeIcon(nextDark);
    });
}

function updateThemeIcon(isDark) {
    const icon = themeToggle?.querySelector('i');
    if (icon) icon.className = isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
}

searchInput?.addEventListener('input', () => {
    const searchTerm = searchInput.value.toLowerCase().trim();
    recentActivityList?.querySelectorAll('.activity-item').forEach(item => {
        item.style.display = item.textContent.toLowerCase().includes(searchTerm) ? '' : 'none';
    });
});

notificationButton?.addEventListener('click', () => {
    const dot = notificationButton.querySelector('.notification-dot');
    if (dot) dot.style.display = 'none';
    showDashboardMessage('Notifications are not available in this release.');
});

initTheme();
loadPatientDashboard();

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.stat-card, .card').forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(10px)';
        setTimeout(() => {
            element.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 60);
    });
});
