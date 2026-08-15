const roles = document.querySelectorAll(".role");
const doctorField = document.querySelector(".doctor-field");
const adminField = document.querySelector(".admin-field");
const registerForm = document.getElementById("registerForm");
const roleInput = document.getElementById("roleInput");
const formStatus = document.querySelector(".form-status");
const registerButton = document.getElementById("registerButton");
const togglePassword = document.getElementById("togglePassword");
const fields = {
    firstname: document.getElementById("firstname"),
    lastname: document.getElementById("lastname"),
    email: document.getElementById("email"),
    phone: document.getElementById("phone"),
    dob: document.getElementById("dob"),
    gender: document.getElementById("gender"),
    doctorID: document.getElementById("doctorID"),
    adminCode: document.getElementById("adminCode"),
    password: document.getElementById("password"),
    confirmPassword: document.getElementById("confirmPassword"),
};

let currentRole = "Patient";
const API_BASE_URL = window.MediCareAuth?.API_BASE_URL || window.MEDICARE_API_BASE_URL || "http://127.0.0.1:8000";

const showStatus = (message, success = false) => {
    if (!formStatus) return;
    formStatus.textContent = message;
    formStatus.classList.toggle("success", success);
};

const updateRoleFields = (selectedRole) => {
    currentRole = selectedRole;
    if (roleInput) roleInput.value = selectedRole;
    if (doctorField) doctorField.style.display = selectedRole === "Doctor" ? "block" : "none";
    if (adminField) adminField.style.display = selectedRole === "Admin" ? "block" : "none";
    if (selectedRole !== "Doctor" && fields.doctorID) fields.doctorID.value = "";
    if (selectedRole !== "Admin" && fields.adminCode) fields.adminCode.value = "";

    roles.forEach((role) => {
        const active = role.dataset.role === selectedRole;
        role.classList.toggle("active", active);
        role.setAttribute("aria-pressed", active ? "true" : "false");
    });
};

roles.forEach((role) => {
    role.addEventListener("click", () => updateRoleFields(role.dataset.role));
    role.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            updateRoleFields(role.dataset.role);
        }
    });
});

if (togglePassword) {
    togglePassword.addEventListener("click", () => {
        const isPassword = fields.password.type === "password";
        fields.password.type = isPassword ? "text" : "password";
        togglePassword.classList.toggle("fa-eye", !isPassword);
        togglePassword.classList.toggle("fa-eye-slash", isPassword);
    });
}

const validateName = (name) => /^[A-Za-z ]+$/.test(name);
const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
const validatePhone = (phone) => /^[0-9]{10}$/.test(phone);

function getCookie(name) {
    const prefix = `${name}=`;
    return document.cookie
        .split(";")
        .map((cookie) => cookie.trim())
        .find((cookie) => cookie.startsWith(prefix))
        ?.slice(prefix.length) || "";
}

async function getCsrfToken() {
    const response = await fetch(`${API_BASE_URL}/api/auth/csrf/`, {
        credentials: "include",
        headers: { Accept: "application/json" },
    });
    if (!response.ok) throw new Error("Unable to start a secure registration session.");
    const payload = await response.json();
    return payload.csrfToken || getCookie("csrftoken");
}

function serverErrorMessage(payload) {
    if (payload?.detail) return payload.detail;
    return Object.entries(payload || {})
        .flatMap(([field, value]) => {
            const messages = Array.isArray(value) ? value : [value];
            return messages.map((message) => `${field}: ${message}`);
        })
        .filter(Boolean)
        .join(" ") || "Registration failed. Please check your details.";
}

if (registerForm) {
    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        showStatus("");

        const firstName = fields.firstname.value.trim();
        const lastName = fields.lastname.value.trim();
        const email = fields.email.value.trim();
        const phone = fields.phone.value.trim();
        const dateOfBirth = fields.dob.value || null;
        const gender = fields.gender.value;
        const password = fields.password.value;
        const confirmPassword = fields.confirmPassword.value;
        const doctorID = fields.doctorID?.value.trim() || "";
        const adminCode = fields.adminCode?.value.trim() || "";

        if (!firstName || !lastName || !email || !phone || !dateOfBirth || !gender || !password || !confirmPassword) {
            showStatus("Please complete all required fields.");
            return;
        }
        if (!validateName(firstName) || !validateName(lastName)) {
            showStatus("Please enter valid first and last names.");
            return;
        }
        if (!validateEmail(email)) {
            showStatus("Please enter a valid email address.");
            fields.email.focus();
            return;
        }
        if (!validatePhone(phone)) {
            showStatus("Please enter a valid 10-digit phone number.");
            fields.phone.focus();
            return;
        }
        if (password.length < 8) {
            showStatus("Password must contain at least 8 characters.");
            fields.password.focus();
            return;
        }
        if (password !== confirmPassword) {
            showStatus("Passwords do not match.");
            fields.confirmPassword.focus();
            return;
        }
        if (currentRole === "Doctor" && !doctorID) {
            showStatus("Please enter your Medical License ID.");
            fields.doctorID.focus();
            return;
        }
        if (currentRole === "Admin" && !adminCode) {
            showStatus("Please enter the Admin Code.");
            fields.adminCode.focus();
            return;
        }

        registerButton.disabled = true;
        registerButton.classList.add("loading");
        registerButton.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Creating Account...';

        try {
            const csrfToken = await getCsrfToken();
            const response = await fetch(`${API_BASE_URL}/api/auth/register/`, {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    Accept: "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    email,
                    phone,
                    date_of_birth: dateOfBirth,
                    gender,
                    role: currentRole,
                    doctor_id: doctorID,
                    admin_code: adminCode,
                    password,
                    confirm_password: confirmPassword,
                }),
            });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(serverErrorMessage(payload));

            showStatus("Registration successful. Redirecting to login...", true);
            setTimeout(() => { window.location.href = "login.html"; }, 900);
        } catch (error) {
            showStatus(error.message || "Registration failed. Please try again.");
            registerButton.disabled = false;
            registerButton.classList.remove("loading");
            registerButton.textContent = "Create Account";
        }
    });
}

updateRoleFields(currentRole);
