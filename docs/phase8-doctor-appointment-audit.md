# Phase 8 Doctor and Appointment Audit
## Doctor backend and appointment management scope

**Status:** Audit completed before implementation. It uses the supplied Phase 8 requirements, the existing Phase 5/7 backend, the current doctor dashboard, the patient appointment page, the Phase 5 schema documentation, the Phase 6 authentication documentation, and the existing HTML/CSS/Vanilla JavaScript source.

## 1. Existing doctor model and relationship

The existing `accounts.DoctorProfile` model is the doctor record. It has a one-to-one relationship with the custom authenticated `accounts.User` model through `DoctorProfile.user`.

| Model | Relevant fields | Ownership rule |
|---|---|---|
| `User` | Email, name, phone, date of birth, gender, role, active state | Session identity; must have role `doctor` for doctor APIs |
| `DoctorProfile` | User, specialization, unique optional license ID, contact details, timestamps | Derived from `request.user.doctor_profile` |
| `PatientProfile` | User, blood group, address, timestamps | Derived from `request.user.patient_profile` for patient APIs |

Phase 6 doctor registration creates a `DoctorProfile` with the submitted license ID and a default specialization of `Unspecified`. Phase 8 will reuse this model and will not create a duplicate doctor identity model.

## 2. Existing appointment model

The existing `appointments.Appointment` model links `PatientProfile` and `DoctorProfile` and already contains the core scheduling fields:

| Field | Current meaning |
|---|---|
| `patient` | Patient owner; `PROTECT` on delete |
| `doctor` | Assigned doctor; `PROTECT` on delete |
| `scheduled_date` | Appointment date |
| `scheduled_time` | Appointment time |
| `status` | Existing choices: `upcoming`, `completed`, `cancelled` |
| `reason` | Optional purpose, max 255 characters |
| `notes` | Optional appointment notes |
| `created_at`, `updated_at` | Audit timestamps |

The existing database constraint prevents duplicate doctor/date/time slots. Phase 8 requires a controlled pending/confirmed/rejected/cancelled/completed lifecycle, so the smallest safe model change is to expand the status choices and add a patient/date/time conflict constraint. Existing field names and relationships remain unchanged.

## 3. Existing authentication and permissions

Phase 6 provides Django session authentication, CSRF protection, and `IsPatient`, `IsDoctor`, and `IsAdministrator` permission classes. Phase 8 will reuse those classes and derive doctor/patient ownership from the authenticated user.

No API will accept `patient_id` or `doctor_id` as an ownership selector. A patient may select a target doctor when creating an appointment, because the appointment must be assigned to a doctor, but the patient owner will always be set from `request.user.patient_profile`. A doctor may act only on appointments whose `doctor` equals `request.user.doctor_profile`.

## 4. Existing APIs before Phase 8

Before Phase 8, the backend exposed health, authentication, patient profile/settings/dashboard, and no doctor or appointment API:

```text
GET  /api/health/
GET  /api/auth/csrf/
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
GET  /api/auth/me/
GET/PATCH /api/patient/profile/
GET/PATCH /api/patient/settings/
GET  /api/patient/dashboard/
```

## 5. Doctor dashboard audit

| Existing dashboard area | Current behavior | Phase 8 decision |
|---|---|---|
| Doctor name/profile | Static name and specialization with localStorage override | Connect to authenticated doctor profile API |
| Total patients | Static `248` | Do not connect because no doctor-patient assignment model or supported doctor patient-list API exists in this phase |
| Today’s appointments | Static `12` and `4 remaining` | Connect to doctor dashboard summary derived from assigned appointments |
| Pending reports | Static `7` | Defer to Phase 9 clinical/report functionality |
| Critical alerts | Static `3` | Defer; no safe clinical alert model/API exists |
| Recent patients table | Static names, conditions, ages, IDs | Leave static/defer; complete patient/clinical management is not Phase 8 scope |
| Today’s schedule | Static three appointments | Connect to assigned doctor appointment list and render existing appointment cards |
| Appointment click | Alert with static details | Replace with safe backend-backed detail/status behavior only where needed |
| AI Clinical Insights | Static AI alert | Leave unchanged; AI is deferred |
| Add patient/View patients | Placeholder alerts | Leave deferred; no doctor patient-management API is authorized in Phase 8 |

## 6. Patient appointment-page audit

The existing patient page supports a list, search/status filters, a booking modal with doctor/date/time/reason, cancel buttons for upcoming items, reschedule placeholder, and a details modal. Its JavaScript uses six fake appointments and six fake doctors in memory.

Phase 8 will replace the fake appointment list, stats, doctor options, booking, cancellation, and details with backend requests. The existing HTML/CSS/modal structure will be reused. Rescheduling remains deferred unless the current UI and lifecycle can support it without inventing a new workflow; no reschedule endpoint is required for the minimum complete lifecycle.

## 7. Appointment lifecycle decision

The controlled statuses will be:

```text
pending
confirmed
rejected
cancelled
completed
```

Valid transitions:

| Current | Allowed next states |
|---|---|
| `pending` | `confirmed`, `rejected`, `cancelled` |
| `confirmed` | `cancelled`, `completed` |
| `rejected` | None |
| `cancelled` | None |
| `completed` | None |

Patients can create pending requests and cancel their own pending/confirmed appointments. Doctors can confirm or reject their assigned pending appointments, cancel assigned pending/confirmed appointments where authorized, and mark their assigned confirmed appointments completed. Arbitrary status assignment is rejected.

## 8. Double-booking and time validation

The existing doctor/date/time uniqueness constraint remains and will be supplemented with a patient/date/time uniqueness constraint. The API will also perform application-level conflict checks and catch database integrity conflicts.

Appointments must use the project timezone configuration. The current settings use `TIME_ZONE = "UTC"` with `USE_TZ = True`; API validation will compare the submitted date/time against the configured timezone-aware current time rather than hard-code a local Windows timezone.

## 9. APIs justified by Phase 8

The planned endpoints are:

| Method | URL | Purpose |
|---|---|---|
| `GET` | `/api/doctor/profile/` | Authenticated doctor’s safe profile |
| `GET` | `/api/doctor/dashboard/` | Assigned appointment summary counts and today’s appointment count |
| `GET` | `/api/patient/appointments/` | Current patient’s appointments with safe doctor fields and filters |
| `POST` | `/api/patient/appointments/` | Create a pending appointment for the authenticated patient |
| `GET` | `/api/patient/appointments/<id>/` | Retrieve one own appointment |
| `POST` | `/api/patient/appointments/<id>/cancel/` | Cancel one own pending/confirmed appointment |
| `GET` | `/api/doctor/appointments/` | Assigned doctor’s appointments with filters |
| `GET` | `/api/doctor/appointments/<id>/` | Retrieve one assigned appointment |
| `POST` | `/api/doctor/appointments/<id>/transition/` | Confirm, reject, cancel, or complete an assigned appointment through a validated transition |

No doctor patient-management, clinical-record, prescription, report, AI, or notification API is planned.

## 10. Deferred functionality

Phase 8 defers clinical records, prescriptions, reports, diagnosis, treatment plans, lab results, clinical notes, AI, chatbot/RAG, medical recommendations, doctor patient-management, complete deployment, payment, and notification workflows.

## 11. Security test requirements

Automated tests will verify doctor own-profile access, patient/unauthenticated rejection, doctor ownership isolation, patient appointment creation with server-derived patient, patient list isolation, doctor list isolation, cross-owner detail/update rejection, protected ownership-field rejection, valid and invalid status transitions, past-date rejection, doctor and patient conflict prevention, cancellation/completion authorization, Phase 6/7 regression, and health continuity.
