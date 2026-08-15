// AI Health Insights remains intentionally deferred in Phase 10.

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
    const welcome = document.getElementById('welcomeMsg');
    if (welcome) welcome.textContent = `Welcome back, ${name}`;
}

function updateThemeIcon(isDark) {
    const icon = document.getElementById('themeToggle')?.querySelector('i');
    if (icon) icon.className = isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
}

function initTheme() {
    const saved = localStorage.getItem('medicare-theme') || 'light';
    document.body.classList.toggle('dark', saved === 'dark');
    updateThemeIcon(saved === 'dark');
    document.getElementById('themeToggle')?.addEventListener('click', () => {
        const isDark = !document.body.classList.contains('dark');
        document.body.classList.toggle('dark', isDark);
        localStorage.setItem('medicare-theme', isDark ? 'dark' : 'light');
        updateThemeIcon(isDark);
    });
}

function showDeferredMessage() {
    const resultsArea = document.getElementById('analysisResultsArea');
    const resultsContainer = document.getElementById('resultsContainer');
    if (resultsArea) resultsArea.style.display = 'block';
    if (!resultsContainer) return;

    const message = document.createElement('p');
    message.style.cssText = 'font-size: 13px; color: var(--text-secondary);';
    message.textContent = 'Patient-facing AI risk classification is not available in this release because the current backend policy authorizes only active doctors and administrators. No prediction request was sent. Please consult a qualified healthcare professional for medical concerns.';
    resultsContainer.replaceChildren(message);
}

loadUserInfo();
initTheme();

document.addEventListener('DOMContentLoaded', () => {
    const healthMeter = document.getElementById('healthMeterFill');
    if (healthMeter) healthMeter.style.width = '0%';
    const symptomInput = document.getElementById('symptomInput');
    const addButton = document.getElementById('addSymptomBtn');
    const analyzeButton = document.getElementById('analyzeSymptomsBtn');
    const quickSymptoms = document.getElementById('quickSymptomsContainer');
    const selectedSymptoms = document.getElementById('selectedSymptoms');
    const deferredSymptoms = document.createElement('p');
    deferredSymptoms.style.cssText = 'font-size: 13px; color: var(--text-secondary); margin-top: 12px;';
    deferredSymptoms.textContent = 'Symptom analysis is deferred until a reviewed backend clinical-safety workflow is available.';
    quickSymptoms?.replaceChildren(deferredSymptoms);
    if (symptomInput) symptomInput.disabled = true;
    if (addButton) addButton.disabled = true;
    if (selectedSymptoms) {
        const deferredNotice = document.createElement('span');
        deferredNotice.style.cssText = 'font-size: 13px; color: var(--text-secondary);';
        deferredNotice.textContent = 'No AI analysis is active.';
        selectedSymptoms.replaceChildren(deferredNotice);
    }
    if (analyzeButton) {
        analyzeButton.disabled = false;
        analyzeButton.addEventListener('click', showDeferredMessage);
    }
    document.querySelectorAll('.learn-more-btn').forEach(button => button.addEventListener('click', showDeferredMessage));
    const chartContainer = document.getElementById('healthChartBars');
    if (chartContainer) {
        const trendsNotice = document.createElement('p');
        trendsNotice.style.cssText = 'font-size: 13px; color: var(--text-secondary);';
        trendsNotice.textContent = 'Health trends will be available after a validated backend analytics workflow is implemented.';
        chartContainer.replaceChildren(trendsNotice);
    }
    showDeferredMessage();
});
