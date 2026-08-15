const roles = document.querySelectorAll(".role");
const roleText = document.getElementById("roleText");
const emailLabel = document.getElementById("emailLabel");
const username = document.getElementById("username");
const password = document.getElementById("password");
const togglePassword = document.getElementById("togglePassword");
const loginForm = document.getElementById("loginForm");
const usernameError = document.getElementById("usernameError");
const passwordError = document.getElementById("passwordError");
const loginButton = document.getElementById("loginButton");

let currentRole = "Patient";
const API_BASE_URL = window.MediCareAuth?.API_BASE_URL || window.MEDICARE_API_BASE_URL || "http://127.0.0.1:8000";

roles.forEach((role) => {
    role.addEventListener("click", function () {
        roles.forEach((item) => item.classList.remove("active"));
        this.classList.add("active");
        currentRole = this.dataset.role;
        roleText.textContent = currentRole;

        if (currentRole === "Patient") {
            emailLabel.textContent = "Email";
            username.placeholder = "Enter Email";
        } else if (currentRole === "Doctor") {
            emailLabel.textContent = "Doctor ID / Email";
            username.placeholder = "Enter Doctor ID or Email";
        } else {
            emailLabel.textContent = "Email";
            username.placeholder = "Enter Email";
        }

        clearValidation(username, usernameError);
        clearValidation(password, passwordError);
    });
});

if (togglePassword) {
    togglePassword.addEventListener("click", () => {
        const isPassword = password.type === "password";
        password.type = isPassword ? "text" : "password";
        togglePassword.classList.toggle("fa-eye", !isPassword);
        togglePassword.classList.toggle("fa-eye-slash", isPassword);
    });
}

function showError(input, errorElement, message) {
    input.classList.remove("input-success");
    input.classList.add("input-error");
    errorElement.textContent = message;
    errorElement.classList.add("show");
}

function showSuccess(input, errorElement) {
    input.classList.remove("input-error");
    input.classList.add("input-success");
    errorElement.textContent = "";
    errorElement.classList.remove("show");
}

function clearValidation(input, errorElement) {
    input.classList.remove("input-error", "input-success");
    errorElement.textContent = "";
    errorElement.classList.remove("show");
}

function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function getCsrfCookie() {
    return window.MediCareAuth?.getCookie("csrftoken") || document.cookie
        .split(";")
        .map((cookie) => cookie.trim())
        .find((cookie) => cookie.startsWith("csrftoken="))
        ?.slice("csrftoken=".length) || "";
}

async function getCsrfToken() {
    const response = await fetch(`${API_BASE_URL}/api/auth/csrf/`, {
        credentials: "include",
        headers: { Accept: "application/json" },
    });
    if (!response.ok) throw new Error("Unable to start a secure login session.");
    const payload = await response.json();
    return payload.csrfToken || getCsrfCookie();
}

function dashboardForRole(role) {
    if (role === "patient") return "../patient/patient-dashboard.html";
    if (role === "doctor") return "../doctor/doctor-dashboard.html";
    if (role === "administrator") return "../admin/admin-dashboard.html";
    return "../public/index.html";
}

function serverErrorMessage(payload) {
    if (payload?.detail) return payload.detail;
    return Object.values(payload || {})
        .flatMap((value) => Array.isArray(value) ? value : [value])
        .filter(Boolean)
        .join(" ") || "Unable to sign in. Please try again.";
}

username.addEventListener("input", () => {
    const value = username.value.trim();
    if (!value) {
        clearValidation(username, usernameError);
    } else if (currentRole === "Patient" && !validateEmail(value)) {
        showError(username, usernameError, "Please enter a valid email address.");
    } else {
        showSuccess(username, usernameError);
    }
});

password.addEventListener("input", () => {
    const value = password.value;
    if (!value) {
        clearValidation(password, passwordError);
    } else if (value.length < 8) {
        showError(password, passwordError, "Password must contain at least 8 characters.");
    } else {
        showSuccess(password, passwordError);
    }
});

if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const identifier = username.value.trim();
        const pass = password.value;
        let isValid = true;

        if (!identifier) {
            showError(username, usernameError, "Please enter your email or account ID.");
            isValid = false;
        } else if (currentRole === "Patient" && !validateEmail(identifier)) {
            showError(username, usernameError, "Please enter a valid email address.");
            isValid = false;
        } else {
            showSuccess(username, usernameError);
        }

        if (!pass) {
            showError(password, passwordError, "Please enter your password.");
            isValid = false;
        } else if (pass.length < 8) {
            showError(password, passwordError, "Password must contain at least 8 characters.");
            isValid = false;
        } else {
            showSuccess(password, passwordError);
        }

        if (!isValid) return;

        loginButton.disabled = true;
        loginButton.classList.add("loading");
        loginButton.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Signing in...';

        try {
            const csrfToken = await getCsrfToken();
            const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    Accept: "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({
                    identifier,
                    password: pass,
                    role: currentRole,
                }),
            });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(serverErrorMessage(payload));

            const user = payload.user;
            const fullName = [user?.first_name, user?.last_name].filter(Boolean).join(" ") || user?.email || identifier;
            localStorage.setItem("userName", fullName);
            localStorage.setItem("userEmail", user?.email || identifier);
            localStorage.setItem("userRole", user?.role || currentRole.toLowerCase());
            window.location.href = dashboardForRole(user?.role);
        } catch (error) {
            showError(username, usernameError, error.message || "Unable to sign in. Please try again.");
            loginButton.disabled = false;
            loginButton.classList.remove("loading");
            loginButton.innerHTML = `Login as <span id="roleText">${currentRole}</span>`;
        }
    });
}
