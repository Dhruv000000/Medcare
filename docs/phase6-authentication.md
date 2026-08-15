# MediCare Phase 6 Authentication

## Architecture

MediCare uses **Django session authentication** with the existing Phase 5 custom `accounts.User` model. The browser sends requests with `credentials: "include"`, Django stores the authenticated session server-side, and CSRF protection covers state-changing requests. JWT was intentionally not added because the existing application is a traditional HTML/CSS/Vanilla JavaScript frontend rather than a standalone token-driven SPA.

The sandbox implementation is compatible with the user’s Windows PostgreSQL configuration but does not connect to that Windows machine. It can use the safe SQLite fallback for tests and smoke checks.

## User model and roles

The existing `accounts.User` model remains the only user model. Its email field is the login identifier, and its persisted roles are:

| Persisted role | Frontend label | Intended area |
|---|---|---|
| `patient` | Patient | Patient pages |
| `doctor` | Doctor | Doctor dashboard |
| `administrator` | Admin | Administrative area when a UI is added |

Doctor registration also creates a `DoctorProfile` with the submitted license ID. Patient registration creates `PatientProfile` and `PatientPreferences`. Administrator registration is disabled unless a local `ADMIN_REGISTRATION_CODE` is explicitly configured.

## Endpoints

```text
GET  /api/auth/csrf/
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
GET  /api/auth/me/
GET  /api/health/
```

The health endpoint remains unchanged. No appointment, medical-record, prescription, report, or AI endpoint was introduced.

### CSRF bootstrap

The frontend first requests `/api/auth/csrf/`. Django returns a CSRF token and sets the CSRF cookie. The frontend sends the token in `X-CSRFToken` on registration, login, and logout requests.

### Registration flow

The registration page keeps its existing fields and role selector. It sends first name, last name, email, phone, date of birth, gender, role, doctor license ID or administrator code where applicable, password, and confirmation password to Django. The serializer validates required values, email, phone, role, duplicate email, password confirmation, and Django password validators.

Django’s `set_password()` hashes the password. No plaintext password is stored, returned, written to localStorage, or included in documentation. Patient and doctor profile records are created in the same database transaction as the user.

### Login flow

The login page sends the typed identifier, password, and selected role to `/api/auth/login/`. Patients authenticate by email. Doctors may authenticate by email or by their persisted license ID. Django’s `authenticate()` verifies the password and `login()` creates the session. The server verifies the selected role after credential verification and returns a generic `Invalid email or password.` response for invalid credentials and wrong-role attempts.

The response includes safe identity and role data only. It never includes a password, password hash, session identifier, or secret. The existing redirect behavior is preserved for patient and doctor dashboards. The Admin role falls back to the public page because no Admin dashboard exists yet.

### Current-user flow

`/api/auth/me/` requires an authenticated session and returns the user’s ID, email, name, phone, date of birth, gender, role, role label, and safe patient/doctor profile fields. It never returns password-related fields.

The shared `frontend/js/auth/auth-client.js` calls this endpoint on patient and doctor pages. Unauthenticated users are sent to login. Authenticated users with the wrong role are sent to the correct role area. The client-side guard improves navigation but does not replace backend authorization.

### Logout flow

The frontend requests a CSRF token, posts to `/api/auth/logout/`, and Django invalidates the session with `logout()`. Only after the request is attempted does the frontend clear cosmetic localStorage display values and navigate to login. Refreshing the page cannot restore the invalidated Django session.

## Backend authorization

Reusable permission classes are provided in `apps.accounts.permissions`:

```python
IsPatient
IsDoctor
IsAdministrator
```

They require an authenticated, active user and check the persisted role. The classes are ready for later business APIs, but Phase 6 does not expose business endpoints.

## Frontend integration

The existing login and registration pages retain their HTML and CSS. Their JavaScript now performs backend requests while preserving role selection, validation feedback, password visibility controls, loading state, and redirects.

Patient and doctor pages load `auth-client.js` before their existing page-specific scripts. Existing page navigation remains ordinary anchor navigation. The authentication listener intercepts only logout links so it can invalidate the session; it does not apply broad `preventDefault()` handlers.

Local cross-origin requests are allowed only from the comma-separated `FRONTEND_ALLOWED_ORIGINS` setting. The default local origins are:

```text
http://127.0.0.1:8010
http://localhost:8010
```

The API base defaults to `http://127.0.0.1:8000` and can be overridden before the auth scripts load with `window.MEDICARE_API_BASE_URL`.

## Windows validation

On the user’s Windows computer, after PostgreSQL and the project virtual environment are configured:

```powershell
cd backend
Copy-Item .env.example .env
notepad .env
py -3.12 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py test apps.accounts -v 2
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

In a second PowerShell window, serve the frontend from the project root:

```powershell
cd ..
py -m http.server 8010 --directory frontend
```

Open:

```text
http://127.0.0.1:8010/pages/auth/register.html
http://127.0.0.1:8010/pages/auth/login.html
```

Use non-production test data. Confirm that an invalid password is rejected, a valid patient reaches patient pages, a valid doctor reaches the doctor dashboard, a wrong-role attempt is rejected, `/api/auth/me/` is safe, and logout invalidates access.

## Security considerations

Django’s password hashing and password validators are used. CSRF is enforced for registration, login, and logout. Session cookies are HTTP-only, and no token is stored in localStorage. Invalid login attempts use a generic message. Duplicate registration is rejected. Admin registration is disabled unless a server-side code is configured. Backend role permission classes are authoritative for future APIs. The local CORS middleware allows only explicitly configured origins and credentials; it does not use a wildcard origin.

## Deferred scope

Phase 6 does not implement appointment APIs, medical-record APIs, prescription APIs, report APIs, AI, chatbot, RAG, payment, notifications, deployment, or frontend redesign. The next phase should be approved explicitly before any of those areas are started.
