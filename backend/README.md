# MediCare Backend

This directory contains the **Django 5.2.17 and Django REST Framework 3.18.0 backend**. Phase 5 established the custom user and domain model foundation. Phase 6 adds secure session-based authentication and authorization while preserving the existing frontend and leaving all business APIs and AI deferred.

## Environment boundary

The project was developed in an isolated Ubuntu sandbox at `/home/ubuntu/audit_project/medicare_phase2`. The project-local `backend/venv/` is not portable to Windows and must be recreated after downloading the project. PostgreSQL was not installed in the sandbox, and no claim is made that the sandbox connected to the user’s Windows PostgreSQL server.

## Windows setup

Read [`docs/local-postgresql-setup.md`](../docs/local-postgresql-setup.md) for the complete Windows procedure. It covers PostgreSQL 18.6 at `localhost:5432`, creation of `medicare_db` and `medicare_app`, local password entry, `backend/.env`, Windows virtual-environment setup, migrations, connection verification, server startup, authentication testing, and `/api/health/` testing.

The password-free SQL template remains at:

```text
database/scripts/create_medicare_db.sql
```

It must be executed only on the user’s Windows PostgreSQL installation. It was not executed in the sandbox.

## Backend setup on Windows

From `backend\` in PowerShell:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

The requirements are intentionally minimal:

```text
Django==5.2.17
djangorestframework==3.18.0
psycopg[binary]==3.3.4
```

## Database configuration

Django reads the following variables from `backend/.env` for local development:

```text
DB_NAME=medicare_db
DB_USER=medicare_app
DB_PASSWORD=local-only-password
DB_HOST=localhost
DB_PORT=5432
FRONTEND_ALLOWED_ORIGINS=http://127.0.0.1:8010,http://localhost:8010
ADMIN_REGISTRATION_CODE=
```

The real password must be entered only in the ignored local `backend/.env`. No real password is stored in the project, documentation, reports, or archive. If all five `DB_*` values are present, Django selects PostgreSQL. Without them, the sandbox-safe SQLite fallback remains available for non-destructive checks.

## Phase 6 authentication architecture

Phase 6 uses Django session authentication with Django’s standard `authenticate()`, `login()`, `logout()`, password hashing, password validators, session middleware, and CSRF protection. This is the simplest secure fit for the traditional HTML/CSS/Vanilla JavaScript frontend and avoids unnecessary JWT/token-storage complexity.

The existing `accounts.User` model is used. It has email identity and the persisted roles `patient`, `doctor`, and `administrator`. No second user model was created.

## Authentication endpoints

```text
GET  /api/auth/csrf/
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
GET  /api/auth/me/
GET  /api/health/
```

`/api/auth/register/` validates and creates patient or doctor accounts; public administrator registration remains disabled unless a local `ADMIN_REGISTRATION_CODE` is explicitly configured. Passwords are hashed with Django and never returned.

`/api/auth/login/` verifies credentials and the selected role, creates a server-side session, and returns safe identity data. Invalid and wrong-role attempts use a generic error. `/api/auth/logout/` invalidates the session. `/api/auth/me/` returns only safe profile data for an authenticated user.

The reusable permission classes `IsPatient`, `IsDoctor`, and `IsAdministrator` are available for future APIs. No appointment, medical-record, prescription, report, or AI endpoint was added in Phase 6.

## Phase 7 patient APIs

Phase 7 adds the patient-only API namespace:

```text
GET    /api/patient/profile/
PUT    /api/patient/profile/
PATCH  /api/patient/profile/
GET    /api/patient/settings/
PUT    /api/patient/settings/
PATCH  /api/patient/settings/
GET    /api/patient/dashboard/
```

Each endpoint requires an authenticated session, the `patient` role, and an associated `PatientProfile`. Ownership is derived from `request.user.patient_profile`; patient IDs supplied by the frontend, query string, URL, body, hidden fields, or localStorage are not trusted. Profile and settings serializers explicitly reject protected or unknown fields. The dashboard endpoint returns only authenticated-patient counts for existing models.

Read [`docs/phase7-patient-api.md`](../docs/phase7-patient-api.md) and [`docs/phase7-patient-module-audit.md`](../docs/phase7-patient-module-audit.md) for the endpoint contracts, frontend integration, tests, and deferred boundaries.

## Phase 8 doctor and appointment APIs

Phase 8 adds the following role-scoped endpoints:

```text
GET  /api/doctor/profile/
GET  /api/doctor/dashboard/
GET  /api/doctor/appointments/
GET  /api/doctor/appointments/<id>/
POST /api/doctor/appointments/<id>/transition/
GET  /api/patient/doctors/
GET  /api/patient/appointments/
POST /api/patient/appointments/
GET  /api/patient/appointments/<id>/
POST /api/patient/appointments/<id>/cancel/
```

Doctor endpoints require an authenticated session, the `doctor` role, and an associated `DoctorProfile`. Patient appointment endpoints require an authenticated session, the `patient` role, and an associated `PatientProfile`. Ownership is derived from `request.user`; submitted patient IDs, doctor ownership IDs, hidden fields, URL owner selectors, and localStorage values are not trusted.

Appointments use the controlled lifecycle `pending`, `confirmed`, `rejected`, `cancelled`, and `completed`. Valid transitions are `pending → confirmed/rejected/cancelled` and `confirmed → cancelled/completed`. The patient/date/time and doctor/date/time uniqueness constraints plus application checks prevent obvious double booking. Phase 8 does not expose clinical records, reports, prescriptions, AI, or doctor patient-management APIs.

Read [`docs/phase8-doctor-appointment-api.md`](../docs/phase8-doctor-appointment-api.md) and [`docs/phase8-doctor-appointment-audit.md`](../docs/phase8-doctor-appointment-audit.md) for endpoint contracts, transitions, security tests, frontend integration, and Windows validation.

## Local frontend integration

The shared frontend client is:

```text
frontend/js/auth/auth-client.js
```

It uses `fetch()` with `credentials: "include"`, obtains CSRF tokens, protects patient and doctor pages by calling `/api/auth/me/`, updates cosmetic display values, and invalidates sessions through the logout endpoint. Access decisions do not rely on localStorage. The existing page markup, styles, sidebar, cards, forms, and navigation design remain unchanged.

The local static frontend should be served on an origin listed in `FRONTEND_ALLOWED_ORIGINS`, such as `http://127.0.0.1:8010`. The default API base is `http://127.0.0.1:8000`; it can be overridden by defining `window.MEDICARE_API_BASE_URL` before the auth scripts load.

## Phase boundary

No PostgreSQL server was installed in the sandbox. No database or role was created there. Phase 8 implements doctor profile/dashboard and patient-doctor appointment management only. Clinical records, prescriptions, reports, diagnosis, treatment plans, AI, chatbot, RAG, payment, notification, deployment, and doctor patient-management APIs remain deferred.
