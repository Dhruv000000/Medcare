# Phase 8 Doctor and Appointment API Guide

**Status:** Implemented and validated in the isolated sandbox. This guide documents only endpoints that exist in the project.

> **Environment boundary:** The sandbox is Ubuntu and is not the user’s Windows computer. PostgreSQL 18.6 on Windows was not accessed from the sandbox. Windows commands below are for the user’s local validation only.

## Architecture

The Phase 8 request flow is:

```text
Existing HTML/CSS frontend
        ↓
Vanilla JavaScript with the shared session client
        ↓
Django REST Framework session-authenticated views
        ↓
Role permissions and request.user-derived ownership
        ↓
Existing DoctorProfile, PatientProfile, and Appointment models
        ↓
User-configured PostgreSQL on Windows
```

The frontend uses the existing `fetch()`/CSRF helper. The backend uses Django session authentication, `IsAuthenticated`, and the existing `IsPatient`/`IsDoctor` permissions. No JWT, token storage, frontend router, or second user model was introduced.[1] [2]

## Appointment lifecycle

The controlled appointment statuses are:

| Status | Meaning |
|---|---|
| `pending` | Patient request awaiting doctor decision |
| `confirmed` | Doctor accepted the request |
| `rejected` | Doctor declined the request |
| `cancelled` | Patient or authorized doctor cancelled it |
| `completed` | Doctor marked a confirmed appointment as completed |

Valid transitions are:

| Current status | Allowed transitions |
|---|---|
| `pending` | `confirmed`, `rejected`, `cancelled` |
| `confirmed` | `cancelled`, `completed` |
| `rejected` | None |
| `cancelled` | None |
| `completed` | None |

Clients cannot submit arbitrary `status` values. Doctors submit an action to the transition endpoint, and the server maps that action to an allowed next state.

## Doctor endpoints

### `GET /api/doctor/profile/`

| Property | Requirement |
|---|---|
| Authentication | Django session required |
| Role | `doctor` |
| Ownership | Derived from `request.user.doctor_profile` |
| Purpose | Return the authenticated doctor’s safe profile |
| Request body | None |
| Success | HTTP 200 |
| Errors | HTTP 403 when unauthenticated, wrong role, or missing doctor profile |

Example response using fake data:

```json
{
  "email": "doctor.one@example.test",
  "first_name": "Doctor",
  "last_name": "One",
  "role": "doctor",
  "specialization": "Cardiology",
  "license_id": "LIC-EXAMPLE-001",
  "contact_details": ""
}
```

Passwords, password hashes, session secrets, and unrelated patient data are not returned.

### `GET /api/doctor/dashboard/`

| Property | Requirement |
|---|---|
| Authentication | Django session required |
| Role | `doctor` |
| Ownership | All counts and schedule rows are filtered by the authenticated doctor profile |
| Purpose | Return supported doctor identity and appointment summary values |
| Request body | None |
| Success | HTTP 200 |
| Errors | HTTP 403 when access is not permitted |

The response includes `pending_count`, `confirmed_count`, `today_count`, `completed_count`, `upcoming_count`, the safe doctor profile, and `today_appointments`. Unsupported dashboard figures such as total patients, pending reports, critical alerts, and AI insights are not fabricated; the existing dashboard displays them as deferred.

### `GET /api/doctor/appointments/`

| Property | Requirement |
|---|---|
| Authentication | Django session required |
| Role | `doctor` |
| Ownership | Returns only rows where `appointment.doctor = request.user.doctor_profile` |
| Filters | `status=pending|confirmed|rejected|cancelled|completed`; `scope=today|upcoming|past` |
| Success | HTTP 200 with an array |
| Errors | HTTP 400 for invalid filters; HTTP 403 for unauthorized access |

### `GET /api/doctor/appointments/<id>/`

Returns one appointment only when its doctor is the authenticated doctor. A different doctor receives HTTP 404 rather than another doctor’s row.

### `POST /api/doctor/appointments/<id>/transition/`

| Property | Requirement |
|---|---|
| Authentication | Django session plus CSRF token |
| Role | `doctor` |
| Ownership | The appointment must belong to the authenticated doctor |
| Request body | `{ "action": "confirm" }`, `{ "action": "reject" }`, `{ "action": "cancel" }`, or `{ "action": "complete" }` |
| Success | HTTP 200 with the updated appointment |
| Errors | HTTP 400 for invalid actions/transitions; HTTP 404 for another doctor’s appointment; HTTP 403 for unauthorized access |

The `status`, `doctor_id`, `patient_id`, and arbitrary extra fields are not accepted as substitutes for the controlled action.

## Patient appointment endpoints

### `GET /api/patient/doctors/`

| Property | Requirement |
|---|---|
| Authentication | Django session required |
| Role | `patient` |
| Purpose | Return active doctors for the existing booking selector |
| Response fields | `id`, `name`, `specialization` |
| Success | HTTP 200 |
| Errors | HTTP 403 for unauthorized access |

Only a minimal directory representation is returned. Doctor management fields are not exposed here.

### `GET /api/patient/appointments/`

| Property | Requirement |
|---|---|
| Authentication | Django session required |
| Role | `patient` |
| Ownership | Returns only rows where `appointment.patient = request.user.patient_profile` |
| Filters | `status=pending|confirmed|rejected|cancelled|completed`; `scope=today|upcoming|past` |
| Success | HTTP 200 with an array |
| Errors | HTTP 400 for invalid filters; HTTP 403 for unauthorized access |

### `POST /api/patient/appointments/`

| Property | Requirement |
|---|---|
| Authentication | Django session plus CSRF token |
| Role | `patient` |
| Ownership | Patient is set from `request.user.patient_profile`; client `patient_id` is rejected |
| Request body | `doctor_id`, `scheduled_date` (`YYYY-MM-DD`), `scheduled_time` (`HH:MM`), optional `reason` |
| Success | HTTP 201 with a `pending` appointment |
| Errors | HTTP 400 for invalid doctor/date/time/fields; HTTP 409 for a scheduling conflict; HTTP 403 for unauthorized access |

Example request using fake data:

```json
{
  "doctor_id": 1,
  "scheduled_date": "2030-02-01",
  "scheduled_time": "09:30",
  "reason": "Follow-up consultation"
}
```

The server rejects past appointments, inactive/nonexistent doctors, unknown or protected fields, and obvious conflicts.

### `GET /api/patient/appointments/<id>/`

Returns one appointment only when it belongs to the authenticated patient. A different patient receives HTTP 404.

### `POST /api/patient/appointments/<id>/cancel/`

| Property | Requirement |
|---|---|
| Authentication | Django session plus CSRF token |
| Role | `patient` |
| Ownership | Appointment must belong to the authenticated patient |
| Allowed states | `pending` or `confirmed` |
| Success | HTTP 200 with the cancelled appointment |
| Errors | HTTP 400 for terminal states; HTTP 404 for another patient’s appointment; HTTP 403 for unauthorized access |

## Appointment integrity and timezone

The existing `Appointment` model was reused. The status choices were expanded and the smallest necessary database migration was created. The existing unique doctor/date/time constraint remains, and a patient/date/time constraint was added. Application-level checks return HTTP 409 before creation when a doctor or patient has an active appointment at the requested slot. Database integrity errors are also converted to HTTP 409.

Django currently uses `TIME_ZONE = "UTC"` with `USE_TZ = True`. Past-date/time validation compares the request to Django’s configured timezone-aware current time rather than assuming a Windows local timezone.[3]

## Frontend integration

The existing patient appointment page now uses the backend for doctor options, appointment listing, filters, booking, details, cancellation, and loading/error states. The existing modal, stats row, cards, filters, styles, and navigation remain in place.

The existing doctor dashboard now uses the backend for doctor identity, supported appointment counts, today’s assigned schedule, and confirm/reject/cancel/complete actions. The static total-patients, pending-reports, critical-alert, AI, and clinical patient-management features remain visibly deferred rather than fabricated.

## Windows validation

The following commands are for the user’s Windows computer, where PostgreSQL 18.6 is installed at `localhost:5432`. Do not run these commands in the sandbox.

```powershell
cd path\to\MediCare\backend
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py test
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

In a second PowerShell window:

```powershell
cd path\to\MediCare
py -m http.server 8010 --directory frontend
```

Use fake development accounts and data only. Register a fake patient and a fake doctor using the existing registration design. Log in as the patient, open the appointments page, load the doctor selector, create a future appointment, and confirm it is stored in PostgreSQL. Log in as the doctor, verify that only the assigned appointment appears, confirm or reject it, and return to the patient account to verify the status. Test cancellation, completion, another patient/doctor ownership attempt, a past date, and a double-booked slot.

Check these routes from the browser or API client:

```text
http://127.0.0.1:8000/api/health/
http://127.0.0.1:8000/api/doctor/profile/
http://127.0.0.1:8000/api/doctor/dashboard/
http://127.0.0.1:8000/api/doctor/appointments/
http://127.0.0.1:8000/api/patient/doctors/
http://127.0.0.1:8000/api/patient/appointments/
```

Never use real healthcare information, expose PostgreSQL to the internet, or place database credentials in source control.

## Deferred scope

Phase 8 does not implement clinical records, prescriptions, reports, diagnosis, treatment plans, lab results, clinical notes, AI, chatbot, RAG, recommendations, doctor patient-management, payment, notifications, or deployment automation. These belong to later phases.

## References

[1]: [Django authentication in web requests](https://docs.djangoproject.com/en/5.2/topics/auth/default/)  
[2]: [Django REST framework authentication](https://www.django-rest-framework.org/api-guide/authentication/)  
[3]: [Django time zones](https://docs.djangoproject.com/en/5.2/topics/i18n/timezones/)  
[4]: [Django database constraints](https://docs.djangoproject.com/en/5.2/ref/models/constraints/)  
