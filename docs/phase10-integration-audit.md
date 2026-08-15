# Phase 10 Frontend–Backend Integration Audit
## End-to-end MediCare workflow

**Status:** Completed before implementation. The attached Phase 10 reference material was used as supporting requirements context. The current Phase 1–9 project implementation is the source of truth for endpoint names, response fields, permissions, and existing UI structure.

## 1. Phase 10 objective

Phase 10 connects the existing vanilla JavaScript frontend to the Django REST APIs implemented during Phases 6–9. The phase does not replace the authentication architecture, redesign the pages, add a frontend framework, install PostgreSQL, implement AI, or introduce deployment work.

The integration strategy is conservative: reuse the existing HTML/CSS, use the shared `auth-client.js` session and CSRF helper, update page scripts to consume actual backend responses, add only the smallest backend response extensions required to remove fabricated dashboard content, and leave unsupported functionality visibly deferred rather than pretending it succeeded.

## 2. Existing API contract used

| Frontend area | Existing endpoint(s) | Authentication and role | Phase 10 use |
|---|---|---|---|
| Login | `POST /api/auth/login/`, `GET /api/auth/csrf/` | Public endpoint with CSRF | Real session login and backend-derived role redirect |
| Registration | `POST /api/auth/register/`, `GET /api/auth/csrf/` | Public endpoint with CSRF | Real account/profile creation |
| Session/current user | `GET /api/auth/me/` | Authenticated session | Protected-page recognition and live user identity |
| Logout | `POST /api/auth/logout/`, `GET /api/auth/csrf/` | Authenticated session with CSRF | Session invalidation and redirect |
| Patient dashboard | `GET /api/patient/dashboard/` | Authenticated patient | Counts and recent backend activity |
| Patient profile/settings | `GET/PATCH /api/patient/profile/`, `GET/PATCH /api/patient/settings/` | Authenticated patient | Profile/preferences read and permitted updates |
| Patient appointments | `GET/POST /api/patient/appointments/`, `GET /api/patient/doctors/`, `POST /api/patient/appointments/<id>/cancel/` | Authenticated patient | Directory, list, booking, cancellation |
| Doctor dashboard | `GET /api/doctor/dashboard/` | Authenticated doctor | Live doctor profile, appointment counts, schedule, authorized-patient summary |
| Doctor appointments | `GET /api/doctor/appointments/`, `POST /api/doctor/appointments/<id>/transition/` | Authenticated doctor | Live list and server-side lifecycle actions |
| Patient clinical data | `GET /api/patient/medical-records/`, `/prescriptions/`, `/reports/` | Authenticated patient | Read-only own clinical data |
| Doctor clinical data | `GET/POST /api/doctor/medical-records/`, `/prescriptions/`, `/reports/` | Authenticated doctor | Authorized clinical creation/listing remains API-backed |

No endpoint is invented for password changes, two-factor authentication, account deletion, patient photo upload, refill persistence, notifications, AI, or file download.

## 3. Current frontend audit

The login and registration pages already call the real Phase 6 endpoints and send CSRF-protected JSON. The shared authentication client already checks `/api/auth/me/`, redirects unauthenticated or wrong-role users, exposes `apiRequest()`, and performs backend logout. Phase 10 will harden error handling and remove remaining page-local fake logout behavior without replacing this architecture.

The patient appointment page and doctor dashboard already call Phase 8 APIs. The patient clinical pages were connected during Phase 9. The largest remaining integration gaps are fabricated patient dashboard activity, a hard-coded patient health status, local/demo profile and settings initialization, fake password/2FA/account-deletion actions, static doctor patient rows, and the AI page’s client-side symptom-matching demo.

## 4. Phase 10 backend response extensions

The existing database models remain sufficient. No migration is planned. Two dashboard response extensions are justified because the existing HTML contains data panels that otherwise display fabricated values:

1. The patient dashboard will receive a bounded `recent_activity` array assembled from the authenticated patient’s own appointments, records, prescriptions, and reports. This removes hard-coded activity while preserving the existing card structure.
2. The doctor dashboard will receive a bounded `patient_count` and `authorized_patients` summary assembled from that doctor’s appointments. This removes hard-coded sample patient rows without creating a new patient-management model or unrestricted patient directory.

These additions preserve existing fields and are additive to the Phase 7/8 response contracts. Existing tests will be updated to assert the new documented fields.

## 5. Ownership and privacy

The backend remains the security boundary. Patient dashboard activity is filtered by the authenticated patient profile. Doctor authorized-patient summaries are filtered by the authenticated doctor’s appointments. Frontend IDs are used only as references for already authorized appointment actions; they are never treated as proof of ownership.

The Phase 9 clinical ownership rule remains unchanged: a doctor may access or create clinical data for a patient only when at least one appointment links the doctor and patient. No global clinical endpoint is added.

## 6. Settings decision

Profile and preferences remain connected to the existing patient APIs. The localStorage profile, notification, and fake default data will no longer be the primary source of truth. The page will load the backend values first and save only permitted fields through `PATCH` requests. Theme and font size may retain minimal browser state for immediate presentation, but backend preferences remain authoritative after loading.

The password-change, two-factor, photo-upload, logout-all, and delete-account controls have no corresponding backend endpoints. They will not claim success or clear local state. They will display a safe deferred message using the existing toast style.

## 7. Error/loading/empty-state decision

API-backed pages will show a lightweight existing-style loading message while collections are fetched, distinguish empty data from unavailable data, parse `detail` and field errors into user-readable messages, redirect on unauthenticated session failure, and show a safe authorization message on forbidden responses. Raw stack traces, database errors, internal paths, and response HTML will not be displayed.

Form submissions will disable the relevant submit control while a request is active, restore it after completion, and refresh the relevant collection from the backend after success. No page will use localStorage as a database.

## 8. AI boundary

The current AI Insights page is a client-side demonstration with hard-coded health scores, trends, recommendations, and symptom-to-condition scoring. Phase 10 will not connect it to medical data or an AI service. The symptom-analysis action will be converted to a safe deferred-state message, and fabricated results will not be generated. The page’s overall layout and educational/deferred presentation will remain intact.

## 9. Files expected to change

Backend changes are limited to the patient and doctor dashboard response serializers/views and their regression tests. Frontend changes are limited to shared auth error handling, patient dashboard, patient settings, patient appointment form handling, doctor dashboard rendering, and the AI page’s deferred behavior. Existing clinical-page API integrations will be retained and only adjusted where consistent loading/error behavior requires it. CSS and broad HTML restructuring are not planned.

## 10. Validation plan

The sandbox validation will use the project’s existing `backend/venv` and SQLite fallback. It will run Django checks, migration checks, the complete test suite, new Phase 10 integration tests, Python compilation, JavaScript syntax checks for all modified scripts, static API/reference checks, and local frontend path validation. Browser testing will be reported separately and will not be claimed unless actually performed.

The user’s Windows PostgreSQL 18.6 instance will not be installed, accessed, exposed, or represented as sandbox-tested. Windows validation instructions will be included in the completion report.

## References

[1]: ../backend/config/urls.py "Current API URL configuration"
[2]: ../backend/apps/accounts/views.py "Current session authentication views"
[3]: ../backend/apps/patient_api/views.py "Current patient profile/settings/dashboard API"
[4]: ../backend/apps/appointment_api/views.py "Current doctor and appointment API"
[5]: ../backend/apps/clinical_api/views.py "Current Phase 9 clinical API"
[6]: ../frontend/js/auth/auth-client.js "Shared frontend session and CSRF client"
[7]: ../frontend/js/patient/patient-dashboard.js "Current patient dashboard script"
[8]: ../frontend/js/patient/patient-settings.js "Current patient settings script"
[9]: ../frontend/js/doctor/doctor-dashboard.js "Current doctor dashboard script"
[10]: ../frontend/js/patient/patient-ai-insights.js "Current deferred AI demonstration script"
[11]: ../../upload/pasted_content_11.txt "Phase 10 reference requirements"
