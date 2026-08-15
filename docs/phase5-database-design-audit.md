# Phase 5 Database Design Audit
## MediCare database models and migration plan

**Status:** Design audit completed before model implementation. This document is based on the supplied MediCare requirements, the organized Phase 2 frontend, the Phase 3 Django foundation, and the Phase 4 PostgreSQL preparation. It does not create sample patient data and does not connect to the user’s Windows PostgreSQL server.

## 1. Evidence reviewed

The audit reviewed the supplied MediCare requirements, all 11 organized HTML pages, the patient and doctor JavaScript modules, the existing Django backend, the Phase 4 PostgreSQL configuration, and the Phase 4 Windows setup documentation.

| Evidence | Database-relevant findings |
|---|---|
| `frontend/pages/auth/register.html` and `frontend/js/auth/register.js` | Shared identity fields include first name, last name, email, phone, date of birth, gender, role, optional doctor license ID, and optional admin code. The browser stores only display identity/role in localStorage; it does not create a backend account. |
| `frontend/js/patient/patient-settings.js` | Patient profile fields include first name, last name, email, phone, date of birth, gender, blood group, and address. Notification preferences include appointment, lab, prescription, tips, newsletter, and email/SMS/both method. Theme and font size are presentation preferences. |
| `frontend/js/patient/patient-appointments.js` | Appointment data uses doctor name, specialization, date, time, status, reason, and notes. Booking UI selects a doctor, date, time, and reason. |
| `frontend/js/patient/patient-medical-records.js` | Medical record data uses type, date, doctor, diagnosis, notes, and a frontend icon. Upload UI also exposes doctor, diagnosis, type, date, notes, and an optional file. |
| `frontend/js/patient/patient-prescriptions.js` | Prescription data uses medicine, dosage, frequency, duration, start/end dates, doctor, status, instructions, side effects, and progress counters. The repeated medicine structure justifies a prescription header plus item model rather than a list in one text field. |
| `frontend/js/patient/patient-reports.js` | Report data uses title, type, doctor, lab, date, status, summary, findings with label/value/normal flag, interpretation, and an uploaded file. |
| `frontend/pages/doctor/doctor-dashboard.html` | Doctor-facing patient summaries display patient name, display ID, age, condition, last visit, and status. Schedule cards display patient, time, and visit purpose. These are views of patients and appointments, not separate dashboard entities. |
| `frontend/js/patient/patient-ai-insights.js` | Symptom analysis is local/demo logic with a disclaimer that it is not a medical diagnosis. No runtime API, model, prediction persistence, or AI result storage is present. |
| Phase 4 backend | Django 5.2.17, DRF 3.18.0, psycopg, environment-based PostgreSQL configuration, and the existing `/api/health/` endpoint are present. No business models exist. |

## 2. Authentication foundation decision

A custom Django user model is appropriate **now**, even though authentication is Phase 6 work. The registration UI already has role-aware identity fields and the intended login identifier is an email address. Deferring the user-model decision until after migrations would create avoidable migration risk.

Phase 5 therefore creates a minimal `accounts.User` model based on `AbstractBaseUser` and `PermissionsMixin`. It provides email identity, role, shared profile fields, staff flags required by Django’s framework, and a manager for future authentication work. It does not implement login, registration, JWT, sessions, password-reset flows, role permissions, or API endpoints.

The admin-code input is not stored as an account field because it is a registration/invitation credential, not durable user profile data. A future authentication phase may define a controlled invitation or provisioning mechanism.

## 3. Proposed models and justification

| Model | Why required now | Evidence and scope decision |
|---|---|---|
| `accounts.User` | Stable identity foundation for future email login and role-aware records | Required by registration fields and future authentication boundary. No authentication flow is implemented. |
| `accounts.PatientProfile` | Stores patient-specific blood group and address while sharing identity data through User | Required by patient settings. Only fields demonstrated by the UI are included. |
| `accounts.DoctorProfile` | Stores specialization and license identifier for doctors referenced by appointments, records, prescriptions, and reports | Required by doctor registration and all doctor-facing clinical records. Availability scheduling is deferred because the current UI does not expose persisted availability. |
| `accounts.PatientPreferences` | Persists notification choices and presentation preferences currently held in localStorage | Directly supported by patient settings. It contains no medical data. |
| `appointments.Appointment` | Represents the patient-doctor booking and schedule relationship | Required by the appointment page and doctor schedule. It stores date, time, status, reason, notes, and timestamps. |
| `medical_records.MedicalRecord` | Represents patient clinical records shown and uploaded in the records page | Required by the records UI. It supports optional doctor and appointment links and an optional attachment. |
| `prescriptions.Prescription` | Represents the prescription event/header and its patient-doctor relationship | Required by the prescriptions page. Header status and dates are separated from medicines. |
| `prescriptions.PrescriptionItem` | Stores one or more medicines per prescription in a normalized structure | Required because the UI exposes medication, dosage, frequency, duration, instructions, and side effects; it avoids arbitrary serialized lists. |
| `reports.MedicalReport` | Represents uploaded or received medical reports with patient, doctor, lab, interpretation, and status | Required by the reports page and its upload form. Optional attachment is included for the demonstrated file upload. |
| `reports.ReportFinding` | Stores report finding label/value/normal status as child rows | Required because reports contain repeated findings rather than one fixed set of measurements. |

## 4. Fields and relationships

### `accounts.User`

The custom user includes `email` as a unique login identifier, `first_name`, `last_name`, `phone`, `date_of_birth`, `gender`, and `role` choices of patient, doctor, or administrator. It also includes `is_active`, `is_staff`, and `date_joined` for Django compatibility and future authentication. Password hashing is provided by Django’s base class, but no password flow is exposed in Phase 5.

### `accounts.PatientProfile`

A one-to-one profile belongs to one User and stores `blood_group` and `address`. The user role is intended to be patient, but role enforcement is deferred to authentication/authorization. The profile uses cascade deletion because it has no meaning without its identity account.

### `accounts.DoctorProfile`

A one-to-one profile belongs to one User and stores `specialization` and an optional unique `license_id`. The current doctor UI requires specialization and the registration form exposes a license identifier. Appointment availability is intentionally deferred.

### `accounts.PatientPreferences`

A one-to-one patient-owned record stores notification booleans for appointments, laboratory reports, prescriptions, tips, and newsletters; a preferred notification method; theme; font size; and timestamps. Defaults mirror the current UI defaults without creating a user-specific sample row.

### `appointments.Appointment`

An appointment belongs to one `PatientProfile` and one `DoctorProfile`. It stores `scheduled_date`, `scheduled_time`, `status`, `reason`, `notes`, `created_at`, and `updated_at`. A composite uniqueness constraint prevents duplicate doctor/date/time slots in the foundation. Deleting a patient is protected because clinical scheduling history should not disappear silently; deleting a doctor is also protected. The current UI’s “Upcoming” display is a derived presentation state from schedule/status rather than a separate database status.

### `medical_records.MedicalRecord`

A record belongs to one patient and may reference one doctor and one appointment. It stores `record_type`, `occurred_on`, `diagnosis`, `notes`, optional `attachment`, `created_at`, and `updated_at`. Patient deletion is protected; doctor and appointment deletion are set to null so the record remains auditable if those related objects are retired.

### `prescriptions.Prescription` and `PrescriptionItem`

A prescription belongs to one patient and one doctor and stores `status`, `issued_on`, `start_date`, `end_date`, `created_at`, and `updated_at`. Each prescription has one or more `PrescriptionItem` rows. An item stores medicine name, dosage, frequency, duration text, start/end dates, instructions, and side effects. The header is protected from patient/doctor deletion; items cascade from their prescription.

### `reports.MedicalReport` and `ReportFinding`

A report belongs to one patient and may reference one doctor, one appointment, and one medical record. It stores title, report type, laboratory/provider name, report date, status, summary, interpretation, optional attachment, and timestamps. Findings are child rows with label, value, and `is_normal`. Patient deletion is protected; optional clinical references are set null. Findings cascade from their report.

## 5. Deferred models and features

The following are intentionally **not** created in Phase 5 because the current frontend provides no persisted contract or because the feature belongs to a later phase:

| Deferred area | Reason |
|---|---|
| Authentication/session/JWT models | Phase 6; custom User foundation is created, but no flow or API is implemented. |
| Administrator profile | Admin UI is missing; the role field is sufficient foundation. |
| Availability/doctor schedule model | Current UI shows appointments but does not expose persisted recurring availability. |
| AIInsight, Prediction, ChatConversation, ChatMessage | AI page is local/demo UI with no runtime service or persistence contract. |
| AuditLog | Required for production healthcare governance, but no backend actions/auth boundary exist yet to define reliable event semantics. |
| Medicine catalog and drug interactions | No backend/API contract exists; prescription items store only the medication text currently shown. |
| Separate diagnosis/condition model | Doctor dashboard condition text is a derived summary and no stable diagnosis workflow exists yet. |
| Dashboard counters/alerts | These are derived aggregates, not independent entities. |

## 6. Integrity and privacy principles

The model layer uses explicit primary keys, foreign keys, one-to-one profiles, normalized prescription items and report findings, meaningful `related_name` values, timestamps, protected deletion for patient-owned clinical history, optional relationships where the UI permits missing context, and only justified indexes/constraints.

No real patient data, credentials, sample rows, phone numbers, addresses, or medical records will be inserted. Frontend demo values are evidence only and will not be migrated into the database.

## 7. Application structure

The implementation will use focused Django apps rather than one large model file:

```text
backend/apps/
├── accounts/
├── appointments/
├── medical_records/
├── prescriptions/
├── reports/
└── health/
```

No REST endpoints, serializers, services, permissions, frontend integration, or authentication views will be added in Phase 5.

## 8. Migration and environment boundary

Migrations will be generated as project files in the new apps. They will be validated with Django checks and migration consistency commands in the sandbox without connecting to the user’s Windows PostgreSQL. The user must run the migrations locally after receiving the updated project and configuring `backend/.env`.

> Phase 5 creates the database structure and migration files only. It does not create or modify the user’s Windows database from the sandbox.
