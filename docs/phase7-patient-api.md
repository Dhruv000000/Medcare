# MediCare Phase 7 Patient APIs

## Scope

Phase 7 adds only authenticated patient profile, patient settings, and read-only patient dashboard summary APIs. It does not add appointment booking, clinical record workflows, prescription workflows, reports, AI, doctor APIs, or database migrations.

## Authentication and ownership

Every endpoint requires a Django session authenticated through Phase 6. Every endpoint also requires the `patient` role through the existing `IsPatient` permission. The patient owner is derived from `request.user.patient_profile`.

No endpoint accepts a patient ID as an ownership selector. A `patient_id` query parameter does not change the selected patient, and `patient_id`, `user_id`, `role`, password, permission, and security fields are rejected from profile/settings updates.

## Endpoint reference

### `GET /api/patient/profile/`

| Property | Contract |
|---|---|
| Authentication | Required Django session |
| Role | `patient` only |
| Purpose | Return the current authenticated patient’s safe profile fields |
| Request body | None |
| Response | Email, first/last name, phone, date of birth, gender, role, blood group, address |
| Errors | 403 unauthenticated/wrong role/missing patient profile |

Example response uses fake values only:

```json
{
  "email": "test.patient@example.test",
  "first_name": "Test",
  "last_name": "Patient",
  "phone": "9876543210",
  "date_of_birth": "1990-01-01",
  "gender": "Other",
  "role": "patient",
  "blood_group": "unknown",
  "address": ""
}
```

Passwords, hashes, internal IDs, session values, and secrets are not returned.

### `PATCH /api/patient/profile/`

`PUT` is also accepted as the same controlled update operation. The authenticated patient may update only the fields already represented by the existing settings UI:

```json
{
  "first_name": "Updated",
  "last_name": "Patient",
  "phone": "9876543212",
  "date_of_birth": "1990-01-01",
  "gender": "Other",
  "blood_group": "A+",
  "address": "Updated test address"
}
```

Email is read-only because it is the authentication identifier. Role, password, password hash, primary keys, patient ownership, active/staff state, permissions, and session fields cannot be modified. Invalid phone, name, date, choice, protected, or unknown fields return HTTP 400.

### `GET /api/patient/settings/`

| Property | Contract |
|---|---|
| Authentication | Required Django session |
| Role | `patient` only |
| Purpose | Return persisted patient notification and appearance preferences |
| Request body | None |
| Response | Existing `PatientPreferences` fields only |
| Errors | 403 unauthenticated/wrong role/missing patient profile |

### `PATCH /api/patient/settings/`

`PUT` is also accepted. Only existing preference fields are writable:

```json
{
  "appointment_notifications": true,
  "laboratory_notifications": true,
  "prescription_notifications": true,
  "health_tips": false,
  "newsletter": false,
  "notification_method": "email",
  "theme": "light",
  "font_size": "medium"
}
```

Unknown fields and identifiers are rejected with HTTP 400. Password, two-factor authentication, deletion, logout-all, and other security operations are not part of this endpoint.

### `GET /api/patient/dashboard/`

| Property | Contract |
|---|---|
| Authentication | Required Django session |
| Role | `patient` only |
| Purpose | Return the minimum count summary supported by the existing dashboard and Phase 5 models |
| Request body | None |
| Response | Counts for the authenticated patient’s upcoming appointments, medical records, and active/refill-needed prescriptions |
| Errors | 403 unauthenticated/wrong role/missing patient profile |

Example response:

```json
{
  "upcoming_appointment_count": 0,
  "medical_record_count": 0,
  "active_prescription_count": 0
}
```

The response is computed from the current session owner. It does not return appointment details, clinical data, prescriptions, reports, static sample values, or another patient’s aggregate.

## Frontend integration

The existing patient dashboard receives only the three summary counts through `frontend/js/patient/patient-dashboard.js`. Stable IDs were added to the existing count elements; no visual structure or CSS changed.

The existing patient settings page receives profile and preference values through `frontend/js/patient/patient-settings.js`. Profile, notification, and appearance saves use the shared Phase 6 credentialed API helper. Existing localStorage values remain only as presentation fallback/cosmetic state; ownership and persisted data come from the backend.

Appointments, medical records, prescriptions, reports, and AI pages remain static/demo pages in Phase 7. Their existing UI remains unchanged.

## Security behavior

The endpoints use session authentication and `IsPatient`. The backend never trusts IDs from JavaScript, URLs, query strings, bodies, hidden fields, or localStorage. Cross-patient access is explicitly tested. No passwords or sensitive authentication fields are serialized. CSRF handling is provided by the existing Phase 6 session architecture.

## Windows validation

After configuring the user’s existing Windows PostgreSQL and recreating the Windows virtual environment:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py test
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Serve the frontend from a second PowerShell window at the configured local origin:

```powershell
cd ..
py -m http.server 8010 --directory frontend
```

Register a fake patient through the existing registration page, log in, verify the profile/settings/dashboard API requests in the browser network panel, edit permitted profile/settings fields, confirm logout, and verify that a doctor or unauthenticated browser cannot access patient endpoints. Do not use real healthcare information or expose PostgreSQL outside the local computer.

## Deferred functionality

Phase 8 should address the complete appointment system. Later clinical-data phases should address medical records, prescriptions, and reports. AI, chatbot, RAG, notifications, password operations, account deletion, and doctor APIs remain deferred.
