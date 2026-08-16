function apiRequest(path, options = {}) {
    if (window.MediCareAuth?.apiRequest) return window.MediCareAuth.apiRequest(path, options);
    return fetch(path, options);
}

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
    window.alert('This feature will be available after a validated backend workflow is implemented.');
}

const MAX_HISTORY_TURNS = 12;
const MAX_STORED_TURNS = 30;
const GREETING = "Hi, I'm the MediCare AI Symptom Assistant. Describe what you're feeling — for example, symptoms, how long you've had them, and their severity — and I'll share general information and self-care guidance.";

function chatStorageKey() {
    const email = localStorage.getItem('userEmail') || 'anonymous';
    return `medicare-symptom-chat-history:${email}`;
}

function loadChatHistory() {
    try {
        const raw = localStorage.getItem(chatStorageKey());
        const parsed = raw ? JSON.parse(raw) : [];
        return Array.isArray(parsed) ? parsed : [];
    } catch {
        return [];
    }
}

function saveChatHistory(history) {
    try {
        localStorage.setItem(chatStorageKey(), JSON.stringify(history.slice(-MAX_STORED_TURNS)));
    } catch {
        // Storage unavailable or full; conversation simply won't persist across reloads.
    }
}

let chatHistory = loadChatHistory();

function appendChatBubble(role, text, { error = false } = {}) {
    const messages = document.getElementById('chatMessages');
    if (!messages) return null;
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}${error ? ' error' : ''}`;
    const content = document.createElement('div');
    content.className = 'chat-bubble-content';
    content.textContent = text;
    bubble.appendChild(content);
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
    return bubble;
}

function appendTypingBubble() {
    const messages = document.getElementById('chatMessages');
    if (!messages) return null;
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble assistant typing';
    const content = document.createElement('div');
    content.className = 'chat-bubble-content';
    content.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
    bubble.appendChild(content);
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
    return bubble;
}

async function sendSymptomMessage(message) {
    const input = document.getElementById('chatInput');
    const sendButton = document.getElementById('chatSendBtn');
    appendChatBubble('user', message);
    chatHistory.push({ role: 'user', content: message });
    saveChatHistory(chatHistory);
    if (input) input.value = '';
    if (input) input.disabled = true;
    if (sendButton) sendButton.disabled = true;

    const typingBubble = appendTypingBubble();
    try {
        const response = await apiRequest('/api/ai/symptom-chat/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message,
                history: chatHistory.slice(-MAX_HISTORY_TURNS - 1, -1),
            }),
        });
        const payload = await response.json().catch(() => ({}));
        typingBubble?.remove();
        if (!response.ok) {
            throw new Error(payload.detail || 'The symptom assistant could not respond. Please try again.');
        }
        appendChatBubble('assistant', payload.reply);
        chatHistory.push({ role: 'assistant', content: payload.reply });
        saveChatHistory(chatHistory);
    } catch (error) {
        typingBubble?.remove();
        appendChatBubble('assistant', error.message || 'Something went wrong. Please try again.', { error: true });
    } finally {
        if (input) { input.disabled = false; input.focus(); }
        if (sendButton) sendButton.disabled = false;
    }
}

function renderChatHistory() {
    const messages = document.getElementById('chatMessages');
    if (!messages) return;
    messages.replaceChildren();
    if (!chatHistory.length) {
        appendChatBubble('assistant', GREETING);
        return;
    }
    chatHistory.forEach(turn => appendChatBubble(turn.role, turn.content));
}

function clearChatConversation() {
    chatHistory = [];
    saveChatHistory(chatHistory);
    renderChatHistory();
}

loadUserInfo();
initTheme();

document.addEventListener('DOMContentLoaded', () => {
    const healthMeter = document.getElementById('healthMeterFill');
    if (healthMeter) healthMeter.style.width = '0%';

    renderChatHistory();

    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    if (chatForm) {
        chatForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const message = chatInput?.value.trim();
            if (!message) return;
            sendSymptomMessage(message);
        });
    }

    document.getElementById('chatClearBtn')?.addEventListener('click', () => {
        if (window.confirm('Clear this conversation? This cannot be undone.')) clearChatConversation();
    });

    document.querySelectorAll('.learn-more-btn').forEach(button => button.addEventListener('click', showDeferredMessage));
    const chartContainer = document.getElementById('healthChartBars');
    if (chartContainer) {
        const trendsNotice = document.createElement('p');
        trendsNotice.style.cssText = 'font-size: 13px; color: var(--text-secondary);';
        trendsNotice.textContent = 'Health trends will be available after a validated backend analytics workflow is implemented.';
        chartContainer.replaceChildren(trendsNotice);
    }
});
