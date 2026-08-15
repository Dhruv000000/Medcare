# Phase 6 Authentication Audit
## MediCare authentication and authorization design

**Status:** Audit completed before implementation. This phase uses the existing Phase 5 custom-user foundation and does not create a competing user model.

## Existing user model

Phase 5 created `apps.accounts.User` using Django’s `AbstractBaseUser` and `PermissionsMixin`. It uses a unique email as `USERNAME_FIELD` and supports the roles `patient`, `doctor`, and `administrator`. It already contains Django password fields, `is_active`, `is_staff`, `date_joined`, and the related `PatientProfile` and `DoctorProfile` models.

This is the correct foundation for Phase 6. No replacement model or destructive identity migration is required.

## Existing roles

The existing registration and login interfaces display `Patient`, `Doctor`, and `Admin`. The persisted Phase 5 values are `patient`, `doctor`, and `administrator`. Phase 6 preserves these three roles and maps the display label `Admin` to the persisted `administrator` value. No additional roles are invented.

## Existing frontend login flow

`frontend/js/auth/login.js` currently performs only client-side validation. It accepts a valid-looking email/password combination, writes `userRole` and `userName` into `localStorage`, waits 700 ms, and redirects to a role-specific dashboard. It makes no backend request, performs no credential verification, does not create a Django session, does not handle CSRF, and does not reject nonexistent users.

The existing role selector changes labels and placeholders only. Doctor and Admin identifiers are not connected to a backend lookup. The current Admin target points to a future Admin dashboard that does not exist in the frontend.

## Existing frontend registration flow

`frontend/js/auth/register.js` validates names, email, ten-digit phone, date of birth, gender, password length, password confirmation, doctor license ID, and Admin code in the browser. It then displays a success message, stores display values in `localStorage`, and redirects to login. It never sends data to Django, checks duplicate accounts, hashes passwords, or creates a database user.

## Current backend authentication state

Before Phase 6, the backend had no authentication endpoints, no registration endpoint, no login endpoint, no logout endpoint, no current-user endpoint, no role permission classes, and no frontend integration. Django’s built-in session middleware was already present, but no view used it.

## Problems found

| Problem | Technical cause |
|---|---|
| Anyone can appear to log in | Login success is based on frontend validation only; no backend credential check exists. |
| Same/default account behavior | The browser stores only the typed display name/role in localStorage; there is no account lookup or persistent login identity. |
| Passwords are not securely persisted by the app | Registration never reaches Django, so no Django password hash is created. |
| Dashboard access is not protected | Patient pages have no backend guard. Doctor JavaScript checks only a mutable localStorage role. |
| Role separation is not authoritative | Role selection controls labels and redirects but is not checked against a server-side account. |
| Logout is incomplete | Frontend localStorage removal/redirect does not invalidate a server session because no server session exists. |
| Cross-origin local development is undefined | The static frontend preview and Django server use different local ports; CSRF and CORS handling were not configured. |

## Proposed authentication architecture

Phase 6 uses **Django session authentication** with Django’s standard password hashing and authentication mechanisms.

This is selected because the project uses traditional HTML/CSS/Vanilla JavaScript, the backend is Django, and the required login state is a browser session rather than a standalone public API token. Sessions avoid adding JWT complexity, token storage in localStorage, refresh-token handling, and another authentication dependency. Django’s `login()`, `logout()`, `authenticate()`, password validators, and CSRF protection provide the established security mechanisms.

The frontend will use `fetch()` with `credentials: "include"`. A CSRF endpoint will set the CSRF cookie before state-changing requests. A small development-only CORS middleware will allow only explicitly configured local frontend origins; it will not allow unrestricted origins.

## Authentication endpoints

```text
GET  /api/auth/csrf/
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
GET  /api/auth/me/
```

The existing `/api/health/` endpoint remains unchanged.

## Registration design

Registration accepts the existing form fields. The backend validates required identity fields, email format, password strength, password confirmation, role, duplicate email, and role-specific doctor license/Admin registration code rules. Passwords are passed to Django’s `set_password()` and are never stored or returned in plaintext.

Doctor registration creates both the custom User and DoctorProfile. Patient registration creates User, PatientProfile, and PatientPreferences. Administrator registration requires a server-side `ADMIN_REGISTRATION_CODE` environment variable; no hard-coded code is supplied. If the code is not configured, public Admin registration is refused rather than silently creating an administrative account.

## Login design

Login accepts an identifier, password, and selected role. Email is the primary identifier. For doctors, the existing Doctor ID/Email field can also resolve a DoctorProfile license ID to its user email before Django authentication. The backend then verifies the role against the authenticated user. Invalid credentials and wrong-role attempts receive a generic error and do not reveal whether an email exists.

Successful login creates a Django session and returns safe user identity and role data only. Passwords, hashes, session identifiers, and secrets are never returned.

## Authorization design

DRF permission classes will provide reusable `IsPatient`, `IsDoctor`, and `IsAdministrator` checks for future APIs. The current-user endpoint and logout endpoint require authentication. No appointment, record, prescription, report, or other business API is implemented in Phase 6.

Static dashboard pages cannot themselves enforce server authorization. Their minimal integration calls the protected current-user endpoint on load. Unauthenticated users are redirected to login; users with the wrong persisted role are redirected to the correct dashboard or login. Backend permissions remain authoritative for all future APIs.

## Scope exclusions

Phase 6 does not implement business APIs, patient/doctor/admin dashboards on the backend, appointment workflows, medical records APIs, prescriptions APIs, reports APIs, AI, chatbot, RAG, or frontend redesign. The existing visual design remains the source of truth.
