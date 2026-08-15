# Phase 7 Patient-Module Audit
## Patient APIs, ownership, and deferred functionality

**Status:** Audit completed before implementation. The audit uses the existing Phase 5 models, Phase 6 session authentication, current patient HTML/JavaScript/CSS, and the supplied Phase 7 requirements. No patient data was created outside automated tests.

## 1. Existing patient models

| Model | Ownership relationship | Existing fields relevant to Phase 7 |
|---|---|---|
| `accounts.User` | Authenticated Django session user | Email, first/last name, phone, date of birth, gender, role, active state |
| `accounts.PatientProfile` | One-to-one with `User` | Blood group, address, timestamps |
| `accounts.PatientPreferences` | One-to-one with `PatientProfile` | Notification flags, notification method, theme, font size, timestamps |
| `appointments.Appointment` | Foreign key to `PatientProfile` | Date/time, status, reason, notes, doctor |
| `medical_records.MedicalRecord` | Foreign key to `PatientProfile` | Type, date, diagnosis, notes, optional attachment |
| `prescriptions.Prescription` | Foreign key to `PatientProfile` | Status, issued/start/end dates, doctor and child items |
| `reports.MedicalReport` | Foreign key to `PatientProfile` | Title, type, laboratory, date, status, summary, interpretation, findings |

No model change is required for Phase 7.

## 2. Existing authentication relationship

Phase 6 authenticates the custom `accounts.User` through a Django session. A patient account is related to exactly one `PatientProfile` through `User.patient_profile`. Patient API ownership will always derive from `request.user.patient_profile`; no patient ID from the URL, query string, request body, hidden form field, localStorage, or frontend JavaScript will select the owner.

The existing `IsPatient` permission requires an authenticated active user with the persisted `patient` role. The new patient endpoints will use both `IsAuthenticated` and `IsPatient`, then safely handle a missing `PatientProfile` relationship with HTTP 403.

## 3. Existing APIs

Before Phase 7, the backend exposed only:

```text
GET  /api/health/
GET  /api/auth/csrf/
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
GET  /api/auth/me/
```

There were no patient profile, settings, dashboard, appointment, record, prescription, report, or AI APIs.

## 4. Patient frontend audit

| Page | Current data and behavior | Phase 7 decision |
|---|---|---|
| `patient-dashboard.html` / `patient-dashboard.js` | Shows static counts, activity, quick links, notifications, and placeholder actions. It does not fetch an API. The count cards correspond to existing appointment, medical record, and prescription models. | Connect only a small read-only dashboard summary endpoint for the three existing counts. Health status, activity details, notifications, and AI actions remain deferred/static. |
| `patient-settings.html` / `patient-settings.js` | Profile tab edits first/last name, email display, phone, date of birth, gender, blood group, and address through localStorage. Notification tab edits five notification flags and method. Appearance tab edits theme and font size. Password, 2FA, logout-all, photo upload, and account deletion are placeholders. | Connect profile GET/PATCH and settings GET/PATCH for fields already represented by Phase 5 models. Email remains read-only because it is the authentication identifier. Password/2FA/danger-zone/photo features remain deferred. |
| `patient-appointments.html` / `patient-appointments.js` | Displays and mutates static in-memory appointment data; booking UI includes doctor, date, time, reason, and details. | Defer the complete appointment API, booking, cancellation, rescheduling, availability, and doctor workflow to Phase 8. The Phase 7 dashboard endpoint may count existing persisted upcoming appointments only. |
| `patient-medical-records.html` / `patient-medical-records.js` | Displays static records and locally adds upload-like rows; fields include type, date, doctor, diagnosis, notes, and file. | Defer the complete medical-record API, uploads, downloads, and clinical file authorization. The dashboard endpoint may count persisted records only. |
| `patient-prescriptions.html` / `patient-prescriptions.js` | Displays static prescriptions and local refill placeholder. | Defer the complete prescription API and refill workflow. The dashboard endpoint may count persisted active/refill-needed prescriptions only. |
| `patient-reports.html` / `patient-reports.js` | Displays static reports, findings, upload-like form, and download placeholder. | Defer the complete reports API, file upload/download, and report workflow. |
| `patient-ai-insights.html` / `patient-ai-insights.js` | Performs local/demo symptom matching and explicitly states it is not a diagnosis. | Leave unchanged. AI, prediction, recommendation, chatbot, RAG, and AI APIs remain deferred. |

The seven patient CSS files are present and will not be changed.

## 5. APIs justified by Phase 7

Phase 7 implements only these endpoints:

| Method | URL | Purpose |
|---|---|---|
| `GET` | `/api/patient/profile/` | Return the authenticated patient’s safe profile fields. |
| `PUT/PATCH` | `/api/patient/profile/` | Update permitted profile fields owned by the authenticated patient. |
| `GET` | `/api/patient/settings/` | Return persisted patient preference fields. |
| `PUT/PATCH` | `/api/patient/settings/` | Update persisted preference fields only. |
| `GET` | `/api/patient/dashboard/` | Return only authenticated-patient counts supported by existing models. |

No endpoint accepts a patient identifier as an ownership selector. Query/body IDs are ignored or rejected as unknown fields. No appointment, record, prescription, report, doctor, or AI endpoint is created.

## 6. Profile update policy

The profile serializer allows only first name, last name, phone, date of birth, gender, blood group, and address. Email is returned read-only and cannot be changed through this endpoint because it is the authentication identifier. Role, password, password hash, primary keys, patient ownership, permissions, active state, staff state, and session state are not exposed or writable.

Settings updates allow only the fields already present in `PatientPreferences`: notification flags, notification method, theme, and font size. Password, 2FA, account deletion, logout-all, photo upload, and security fields are not included.

## 7. Dashboard summary policy

The dashboard endpoint returns:

```json
{
  "upcoming_appointment_count": 0,
  "medical_record_count": 0,
  "active_prescription_count": 0
}
```

Counts are derived from the authenticated patient’s related rows. No static values, sample production data, patient IDs, names, medical details, or cross-patient aggregates are returned. Health status, activity feed, notification feed, appointment details, reports, AI insights, and other future features remain outside this summary.

## 8. Deferred functionality

Phase 7 deliberately defers complete appointment booking/cancellation/scheduling, doctor availability, medical-record APIs and file handling, prescriptions and refill workflows, reports and findings APIs, AI and medical recommendations, chatbot/RAG, notifications, password changes, 2FA, account deletion, logout-all, payment, deployment, and doctor functionality.

## 9. Security test requirements

Automated tests will verify authenticated patient access, unauthenticated rejection, doctor rejection, missing-profile handling, cross-patient IDOR resistance, writable-field validation, protected-field rejection, dashboard scoping, settings ownership, sensitive-field absence, Phase 6 regression, and health endpoint continuity.
