(() => {
    // Explicit override wins. Otherwise, when served from the documented local
    // dev frontend origin, target the local dev backend port; when served from
    // any other origin (e.g. the deployed backend serving this same frontend),
    // default to same-origin so no override is needed after deployment.
    const API_BASE_URL = window.MEDICARE_API_BASE_URL || (
        ["127.0.0.1", "localhost"].includes(window.location.hostname) && window.location.port === "8010"
            ? "http://127.0.0.1:8000"
            : window.location.origin
    );
    const LOGIN_PATH = "../auth/login.html";

    function getCookie(name) {
        const prefix = `${name}=`;
        return document.cookie
            .split(";")
            .map((cookie) => cookie.trim())
            .find((cookie) => cookie.startsWith(prefix))
            ?.slice(prefix.length) || "";
    }

    function getExpectedRole() {
        const path = window.location.pathname.toLowerCase();
        if (path.includes("/patient/")) return "patient";
        if (path.includes("/doctor/")) return "doctor";
        if (path.includes("/admin/")) return "administrator";
        return null;
    }

    function getDashboardPath(role) {
        if (role === "patient") return "../patient/patient-dashboard.html";
        if (role === "doctor") return "../doctor/doctor-dashboard.html";
        if (role === "administrator") return "../admin/admin-dashboard.html";
        return "../public/index.html";
    }

    function applyUser(user) {
        if (!user) return;
        const fullName = [user.first_name, user.last_name].filter(Boolean).join(" ") || user.email;
        const initials = fullName
            .split(/\s+/)
            .map((part) => part[0])
            .join("")
            .slice(0, 2)
            .toUpperCase();

        ["sidebarName", "topbarName", "doctorName", "adminName"].forEach((id) => {
            const element = document.getElementById(id);
            if (element) element.textContent = fullName;
        });
        const patientWelcomeHeading = document.getElementById("patientWelcomeHeading");
        if (patientWelcomeHeading) patientWelcomeHeading.textContent = `Good morning, ${fullName}`;
        ["sidebarAvatar", "topbarAvatar"].forEach((id) => {
            const element = document.getElementById(id);
            if (element) element.textContent = initials;
        });

        // Cosmetic compatibility only. Access decisions never use localStorage.
        localStorage.setItem("userName", fullName);
        localStorage.setItem("userEmail", user.email);
        localStorage.setItem("userRole", user.role);
    }

    async function getCurrentUser() {
        const response = await fetch(`${API_BASE_URL}/api/auth/me/`, {
            credentials: "include",
            headers: { Accept: "application/json" },
        });
        if (!response.ok) return null;
        const payload = await response.json();
        return payload.user || null;
    }

    async function apiRequest(path, options = {}) {
        const method = (options.method || "GET").toUpperCase();
        const headers = {
            Accept: "application/json",
            ...(options.headers || {}),
        };
        if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
            const csrfResponse = await fetch(`${API_BASE_URL}/api/auth/csrf/`, {
                credentials: "include",
                headers: { Accept: "application/json" },
            });
            const csrfPayload = await csrfResponse.json();
            headers["X-CSRFToken"] = csrfPayload.csrfToken || getCookie("csrftoken");
        }
        return fetch(`${API_BASE_URL}${path}`, {
            ...options,
            method,
            credentials: "include",
            headers,
        });
    }

    async function logout(redirectPath = LOGIN_PATH) {
        try {
            const csrfResponse = await fetch(`${API_BASE_URL}/api/auth/csrf/`, {
                credentials: "include",
                headers: { Accept: "application/json" },
            });
            const csrfPayload = await csrfResponse.json();
            await fetch(`${API_BASE_URL}/api/auth/logout/`, {
                method: "POST",
                credentials: "include",
                headers: {
                    Accept: "application/json",
                    "X-CSRFToken": csrfPayload.csrfToken || getCookie("csrftoken"),
                },
            });
        } finally {
            localStorage.removeItem("userRole");
            localStorage.removeItem("userName");
            localStorage.removeItem("userEmail");
            window.location.href = redirectPath;
        }
    }

    async function protectPage() {
        const expectedRole = getExpectedRole();
        if (!expectedRole) return;

        const user = await getCurrentUser().catch(() => null);
        if (!user) {
            window.location.href = LOGIN_PATH;
            return;
        }

        if (user.role !== expectedRole) {
            window.location.href = getDashboardPath(user.role);
            return;
        }

        applyUser(user);
    }

    document.addEventListener("click", (event) => {
        const logoutLink = event.target.closest(".logout");
        if (!logoutLink) return;

        event.preventDefault();
        event.stopImmediatePropagation();
        if (window.confirm("Are you sure you want to logout?")) {
            logout(logoutLink.getAttribute("href") || LOGIN_PATH);
        }
    }, true);

    window.MediCareAuth = {
        API_BASE_URL,
        getCookie,
        getCurrentUser,
        apiRequest,
        applyUser,
        logout,
        protectPage,
    };

    protectPage();
})();
