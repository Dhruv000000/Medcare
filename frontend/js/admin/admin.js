(() => {
    const auth = window.MediCareAuth;
    if (!auth) return;

    const page = document.body.dataset.adminPage || "dashboard";
    const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (character) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
    }[character]));
    const formatDate = (value) => value ? new Date(`${value}T00:00:00`).toLocaleDateString() : "—";
    const setMessage = (message, type = "") => {
        const element = document.getElementById("adminMessage");
        if (!element) return;
        element.textContent = message || "";
        element.className = `toast ${type}`.trim();
    };
    const requestJson = async (path, options = {}) => {
        const response = await auth.apiRequest(path, options);
        const payload = await response.json().catch(() => ({}));
        if (response.status === 401) {
            window.location.href = "../auth/login.html";
            throw new Error("Your session has expired. Please sign in again.");
        }
        if (response.status === 403) throw new Error("Administrator authorization is required.");
        if (!response.ok) {
            const detail = payload.detail || Object.values(payload).flatMap((value) => Array.isArray(value) ? value : [value]).filter(Boolean).join(" ");
            throw new Error(detail || "The request could not be completed.");
        }
        return payload;
    };
    const setAdminIdentity = async () => {
        const user = await auth.getCurrentUser();
        if (!user || user.role !== "administrator") return;
        auth.applyUser(user);
        const fullName = [user.first_name, user.last_name].filter(Boolean).join(" ") || user.email;
        const avatar = fullName.split(/\s+/).map((part) => part[0]).join("").slice(0, 2).toUpperCase();
        const avatarElement = document.getElementById("adminAvatar");
        if (avatarElement) avatarElement.textContent = avatar;
    };
    const tableMessage = (id, message, className = "empty-state") => {
        const element = document.getElementById(id);
        if (element) element.innerHTML = `<div class="${className}">${escapeHtml(message)}</div>`;
    };
    const renderAppointments = (id, appointments, compact = false) => {
        const element = document.getElementById(id);
        if (!element) return;
        if (!appointments.length) {
            tableMessage(id, "No appointments match the current filters.");
            return;
        }
        element.innerHTML = `<table><thead><tr><th>Patient</th><th>Doctor</th><th>Date</th><th>Status</th>${compact ? "" : "<th>Reason</th>"}</tr></thead><tbody>${appointments.map((item) => `<tr><td><strong>${escapeHtml(item.patient_name || "Unknown")}</strong></td><td>${escapeHtml(item.doctor_name || "Unknown")}</td><td>${formatDate(item.scheduled_date)} ${escapeHtml(item.scheduled_time || "")}</td><td><span class="status ${escapeHtml(item.status)}">${escapeHtml(item.status_label || item.status)}</span></td>${compact ? "" : `<td>${escapeHtml(item.reason || "—")}</td>`}</tr>`).join("")}</tbody></table>`;
    };
    const renderPatients = (items) => {
        const element = document.getElementById("patientTable");
        if (!element) return;
        document.getElementById("patientCount").textContent = `${items.length} patient${items.length === 1 ? "" : "s"}`;
        if (!items.length) {
            tableMessage("patientTable", "No patient accounts match the current search.");
            return;
        }
        element.innerHTML = `<table><thead><tr><th>Patient</th><th>Email</th><th>Phone</th><th>Joined</th><th>Status</th><th>Action</th></tr></thead><tbody>${items.map((item) => `<tr><td><strong>${escapeHtml(`${item.first_name || ""} ${item.last_name || ""}`.trim() || "Unnamed patient")}</strong></td><td>${escapeHtml(item.email)}</td><td>${escapeHtml(item.phone)}</td><td>${escapeHtml(new Date(item.date_joined).toLocaleDateString())}</td><td><span class="status ${item.is_active ? "active" : "inactive"}">${item.is_active ? "Active" : "Inactive"}</span></td><td><button class="table-action ${item.is_active ? "deactivate" : ""}" data-status-user="${item.user_id}" data-next-status="${!item.is_active}">${item.is_active ? "Deactivate" : "Activate"}</button></td></tr>`).join("")}</tbody></table>`;
    };
    const renderDoctors = (items) => {
        const element = document.getElementById("doctorTable");
        if (!element) return;
        document.getElementById("doctorCount").textContent = `${items.length} doctor${items.length === 1 ? "" : "s"}`;
        if (!items.length) {
            tableMessage("doctorTable", "No doctor accounts match the current search.");
            return;
        }
        element.innerHTML = `<table><thead><tr><th>Doctor</th><th>Specialization</th><th>License</th><th>Email</th><th>Status</th><th>Action</th></tr></thead><tbody>${items.map((item) => `<tr><td><strong>${escapeHtml(`${item.first_name || ""} ${item.last_name || ""}`.trim() || "Unnamed doctor")}</strong></td><td>${escapeHtml(item.specialization || "—")}</td><td>${escapeHtml(item.license_id || "—")}</td><td>${escapeHtml(item.email)}</td><td><span class="status ${item.is_active ? "active" : "inactive"}">${item.is_active ? "Active" : "Inactive"}</span></td><td><button class="table-action ${item.is_active ? "deactivate" : ""}" data-status-user="${item.user_id}" data-next-status="${!item.is_active}">${item.is_active ? "Deactivate" : "Activate"}</button></td></tr>`).join("")}</tbody></table>`;
    };
    const loadDashboard = async () => {
        const payload = await requestJson("/api/admin/dashboard/");
        ["totalPatients", "totalDoctors", "totalAppointments", "activeUsers", "pendingAppointments", "completedAppointments", "cancelledAppointments", "inactiveUsers"].forEach((id) => {
            const key = id.replace(/[A-Z]/g, (match) => `_${match.toLowerCase()}`);
            const element = document.getElementById(id);
            if (element) element.textContent = payload[key] ?? "0";
        });
        const summary = document.getElementById("appointmentSummary");
        if (summary) summary.textContent = `${payload.total_appointments} total appointment${payload.total_appointments === 1 ? "" : "s"}`;
        renderAppointments("recentAppointments", payload.recent_appointments || [], true);
    };
    const loadPatients = async () => {
        const query = document.getElementById("patientSearch")?.value.trim();
        const payload = await requestJson(`/api/admin/patients/${query ? `?q=${encodeURIComponent(query)}` : ""}`);
        renderPatients(payload);
    };
    const loadDoctors = async () => {
        const query = document.getElementById("doctorSearch")?.value.trim();
        const payload = await requestJson(`/api/admin/doctors/${query ? `?q=${encodeURIComponent(query)}` : ""}`);
        renderDoctors(payload);
    };
    const loadAppointments = async () => {
        const query = document.getElementById("appointmentSearch")?.value.trim();
        const status = document.getElementById("appointmentStatus")?.value;
        const params = new URLSearchParams();
        if (query) params.set("q", query);
        if (status) params.set("status", status);
        const payload = await requestJson(`/api/admin/appointments/${params.toString() ? `?${params}` : ""}`);
        document.getElementById("appointmentCount").textContent = `${payload.length} appointment${payload.length === 1 ? "" : "s"}`;
        renderAppointments("appointmentTable", payload, false);
    };
    const loadProfile = async () => {
        const payload = await requestJson("/api/admin/profile/");
        const element = document.getElementById("adminProfile");
        if (!element) return;
        element.innerHTML = `<table><tbody><tr><th>Name</th><td>${escapeHtml(`${payload.first_name || ""} ${payload.last_name || ""}`.trim() || "—")}</td></tr><tr><th>Email</th><td>${escapeHtml(payload.email)}</td></tr><tr><th>Phone</th><td>${escapeHtml(payload.phone || "—")}</td></tr><tr><th>Role</th><td>${escapeHtml(payload.role_label || payload.role)}</td></tr><tr><th>Account status</th><td>${payload.is_active ? "Active" : "Inactive"}</td></tr><tr><th>Joined</th><td>${escapeHtml(new Date(payload.date_joined).toLocaleDateString())}</td></tr></tbody></table>`;
    };
    const loadPage = async () => {
        try {
            await setAdminIdentity();
            if (page === "dashboard") await loadDashboard();
            if (page === "patients") await loadPatients();
            if (page === "doctors") await loadDoctors();
            if (page === "appointments") await loadAppointments();
            if (page === "profile") await loadProfile();
        } catch (error) {
            setMessage(error.message, "error");
            ["recentAppointments", "patientTable", "doctorTable", "appointmentTable", "adminProfile"].forEach((id) => {
                if (document.getElementById(id)) tableMessage(id, error.message, "error-state");
            });
        }
    };
    document.addEventListener("click", async (event) => {
        const statusButton = event.target.closest("[data-status-user]");
        if (!statusButton) return;
        statusButton.disabled = true;
        try {
            await requestJson(`/api/admin/users/${statusButton.dataset.statusUser}/status/`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ is_active: statusButton.dataset.nextStatus === "true" }) });
            setMessage("Account status updated.", "success");
            if (page === "patients") await loadPatients();
            if (page === "doctors") await loadDoctors();
        } catch (error) {
            setMessage(error.message, "error");
            statusButton.disabled = false;
        }
    });
    document.getElementById("patientSearchButton")?.addEventListener("click", () => loadPatients().catch((error) => setMessage(error.message, "error")));
    document.getElementById("doctorSearchButton")?.addEventListener("click", () => loadDoctors().catch((error) => setMessage(error.message, "error")));
    document.getElementById("appointmentSearchButton")?.addEventListener("click", () => loadAppointments().catch((error) => setMessage(error.message, "error")));
    document.addEventListener("DOMContentLoaded", loadPage);
})();
