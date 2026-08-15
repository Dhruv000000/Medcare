// =========================================================
// SHARED UTILITIES
// =========================================================

function loadUserInfo() {
    const name = localStorage.getItem('userName') || 'Patient';
    const initials = name.split(' ').map(part => part[0]).join('').toUpperCase().slice(0, 2);
    ['sidebarName', 'topbarName'].forEach(id => {
        const element = document.getElementById(id);
        if (element) element.textContent = name;
    });
    ['sidebarAvatar', 'topbarAvatar', 'profileAvatarLarge'].forEach(id => {
        const element = document.getElementById(id);
        if (element) element.textContent = initials;
    });
}

function updateThemeIcon(isDark) {
    const icon = document.getElementById('themeToggle')?.querySelector('i');
    if (icon) icon.className = isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
}

function updateThemeCards(theme) {
    document.querySelectorAll('.theme-card').forEach(card => card.classList.toggle('active', card.dataset.theme === theme));
}

function applyAppearance(theme, fontSize) {
    const isDark = theme === 'dark';
    document.body.classList.toggle('dark', isDark);
    updateThemeIcon(isDark);
    updateThemeCards(theme);
    document.documentElement.className = fontSize && fontSize !== 'medium' ? `font-${fontSize}` : '';
    const font = document.querySelector(`input[name="fontSize"][value="${fontSize || 'medium'}"]`);
    if (font) font.checked = true;
}

function initTheme() {
    const savedTheme = localStorage.getItem('medicare-theme') || 'light';
    const savedFont = localStorage.getItem('medicare-font-size') || 'medium';
    applyAppearance(savedTheme, savedFont);
    document.getElementById('themeToggle')?.addEventListener('click', () => {
        const theme = document.body.classList.contains('dark') ? 'light' : 'dark';
        applyAppearance(theme, document.querySelector('input[name="fontSize"]:checked')?.value || savedFont);
        localStorage.setItem('medicare-theme', theme);
    });
}

function showToast(message) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

function getErrorMessage(payload, fallback) {
    if (payload?.detail) return payload.detail;
    const messages = Object.values(payload || {}).flatMap(value => Array.isArray(value) ? value : [value]).filter(Boolean);
    return messages.join(' ') || fallback;
}

function setFormBusy(form, busy) {
    form?.querySelectorAll('button, input, select, textarea').forEach(element => {
        if (element.type !== 'hidden') element.disabled = busy;
    });
}

async function apiJson(path, options = {}) {
    const response = await window.MediCareAuth.apiRequest(path, options);
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
        if (response.status === 401) {
            window.location.href = '../auth/login.html';
            throw new Error('Your session has expired. Please sign in again.');
        }
        if (response.status === 403) throw new Error('You are not authorized to perform this action.');
        throw new Error(getErrorMessage(payload, 'The server could not complete the request.'));
    }
    return payload;
}

async function loadPatientSettingsFromApi() {
    try {
        const [profile, settings] = await Promise.all([
            apiJson('/api/patient/profile/'),
            apiJson('/api/patient/settings/'),
        ]);
        document.getElementById('firstName').value = profile.first_name || '';
        document.getElementById('lastName').value = profile.last_name || '';
        document.getElementById('email').value = profile.email || '';
        document.getElementById('email').readOnly = true;
        document.getElementById('phone').value = profile.phone || '';
        document.getElementById('dob').value = profile.date_of_birth || '';
        document.getElementById('gender').value = profile.gender || '';
        document.getElementById('bloodGroup').value = profile.blood_group || 'unknown';
        document.getElementById('address').value = profile.address || '';
        document.getElementById('notifAppointment').checked = Boolean(settings.appointment_notifications);
        document.getElementById('notifLab').checked = Boolean(settings.laboratory_notifications);
        document.getElementById('notifPrescription').checked = Boolean(settings.prescription_notifications);
        document.getElementById('notifTips').checked = Boolean(settings.health_tips);
        document.getElementById('notifNewsletter').checked = Boolean(settings.newsletter);
        const method = document.querySelector(`input[name="notifMethod"][value="${settings.notification_method}"]`);
        if (method) method.checked = true;
        applyAppearance(settings.theme, settings.font_size);
        localStorage.setItem('medicare-theme', settings.theme);
        localStorage.setItem('medicare-font-size', settings.font_size);
    } catch (error) {
        showToast(error.message || 'Unable to load patient settings.');
    }
}

async function saveProfile() {
    const payload = {
        first_name: document.getElementById('firstName').value.trim(),
        last_name: document.getElementById('lastName').value.trim(),
        phone: document.getElementById('phone').value.trim(),
        date_of_birth: document.getElementById('dob').value || null,
        gender: document.getElementById('gender').value,
        blood_group: document.getElementById('bloodGroup').value,
        address: document.getElementById('address').value.trim(),
    };
    return apiJson('/api/patient/profile/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
}

async function saveSettings(payload) {
    return apiJson('/api/patient/settings/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
}

function setupTabs() {
    const tabs = document.querySelectorAll('.settings-tab');
    const panes = document.querySelectorAll('.tab-pane');
    tabs.forEach(tab => tab.addEventListener('click', () => {
        tabs.forEach(item => item.classList.remove('active'));
        panes.forEach(pane => pane.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab)?.classList.add('active');
    }));
}

function setupProfileForm() {
    const form = document.getElementById('profileForm');
    form?.addEventListener('submit', async event => {
        event.preventDefault();
        setFormBusy(form, true);
        try {
            const profile = await saveProfile();
            const currentUser = await window.MediCareAuth.getCurrentUser();
            if (currentUser) window.MediCareAuth.applyUser(currentUser);
            if (profile) loadUserInfo();
            showToast('Profile updated successfully.');
        } catch (error) {
            showToast(error.message || 'Unable to save profile.');
        } finally {
            setFormBusy(form, false);
            document.getElementById('email').readOnly = true;
        }
    });
    document.getElementById('changePhotoBtn')?.addEventListener('click', () => showToast('Photo upload is deferred until a backend file workflow is available.'));
}

function setupSecurityForm() {
    const form = document.getElementById('passwordForm');
    const twoFactorToggle = document.getElementById('twoFactorToggle');
    document.querySelectorAll('.toggle-password').forEach(icon => icon.addEventListener('click', () => {
        const input = document.getElementById(icon.dataset.target);
        if (!input) return;
        const visible = input.type === 'text';
        input.type = visible ? 'password' : 'text';
        icon.classList.toggle('fa-eye-slash', visible);
        icon.classList.toggle('fa-eye', !visible);
    }));
    const newPassword = document.getElementById('newPassword');
    newPassword?.addEventListener('input', () => {
        const value = newPassword.value;
        const strengthFill = document.getElementById('strengthFill');
        const strengthLabel = document.getElementById('strengthLabel');
        const strong = value.length >= 10 && /[A-Z]/.test(value) && /[a-z]/.test(value) && /[0-9]/.test(value) && /[^A-Za-z0-9]/.test(value);
        const medium = value.length >= 8;
        const width = strong ? '100%' : medium ? '66%' : value ? '33%' : '0%';
        const color = strong ? '#16a34a' : medium ? '#d97706' : '#dc2626';
        if (strengthFill) { strengthFill.style.width = width; strengthFill.style.backgroundColor = value ? color : 'transparent'; }
        if (strengthLabel) { strengthLabel.textContent = `Strength: ${value ? (strong ? 'Strong' : medium ? 'Medium' : 'Weak') : 'None'}`; strengthLabel.style.color = value ? color : 'var(--text-secondary)'; }
    });
    form?.addEventListener('submit', event => {
        event.preventDefault();
        showToast('Password changes are deferred because no password-update API exists in this release.');
    });
    twoFactorToggle?.addEventListener('change', () => {
        twoFactorToggle.checked = !twoFactorToggle.checked;
        showToast('Two-factor authentication is deferred because no backend workflow exists in this release.');
    });
}

function setupNotificationForm() {
    document.getElementById('saveNotifBtn')?.addEventListener('click', async () => {
        const button = document.getElementById('saveNotifBtn');
        button.disabled = true;
        try {
            await saveSettings({
                appointment_notifications: document.getElementById('notifAppointment').checked,
                laboratory_notifications: document.getElementById('notifLab').checked,
                prescription_notifications: document.getElementById('notifPrescription').checked,
                health_tips: document.getElementById('notifTips').checked,
                newsletter: document.getElementById('notifNewsletter').checked,
                notification_method: document.querySelector('input[name="notifMethod"]:checked')?.value || 'email',
            });
            showToast('Notification preferences saved.');
        } catch (error) {
            showToast(error.message || 'Unable to save notification preferences.');
        } finally {
            button.disabled = false;
        }
    });
}

function setupAppearance() {
    document.querySelectorAll('.theme-card').forEach(card => card.addEventListener('click', () => {
        const font = document.querySelector('input[name="fontSize"]:checked')?.value || 'medium';
        applyAppearance(card.dataset.theme, font);
    }));
    document.querySelectorAll('input[name="fontSize"]').forEach(radio => radio.addEventListener('change', () => {
        applyAppearance(document.body.classList.contains('dark') ? 'dark' : 'light', radio.value);
    }));
    document.getElementById('saveAppearanceBtn')?.addEventListener('click', async () => {
        const button = document.getElementById('saveAppearanceBtn');
        button.disabled = true;
        try {
            const theme = document.body.classList.contains('dark') ? 'dark' : 'light';
            const fontSize = document.querySelector('input[name="fontSize"]:checked')?.value || 'medium';
            await saveSettings({ theme, font_size: fontSize });
            localStorage.setItem('medicare-theme', theme);
            localStorage.setItem('medicare-font-size', fontSize);
            showToast('Appearance settings saved.');
        } catch (error) {
            showToast(error.message || 'Unable to save appearance settings.');
        } finally {
            button.disabled = false;
        }
    });
}

function setupDeferredActions() {
    document.getElementById('logoutAllBtn')?.addEventListener('click', () => showToast('Logout-all-devices is deferred because no backend endpoint exists.'));
    document.getElementById('deleteAccountBtn')?.addEventListener('click', () => showToast('Account deletion is unavailable in this release. No account was changed.'));
}

loadUserInfo();
initTheme();

document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    setupProfileForm();
    setupSecurityForm();
    setupNotificationForm();
    setupAppearance();
    setupDeferredActions();
    loadPatientSettingsFromApi();
});
