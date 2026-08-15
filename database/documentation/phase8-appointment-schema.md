# Phase 8 Appointment Schema Update

Phase 8 reuses the existing `appointments.Appointment` model. No duplicate appointment model was created and no Phase 5 tables were reset.

## Changed fields

The existing `status` field now uses the controlled values:

```text
pending
confirmed
rejected
cancelled
completed
```

The existing patient, doctor, scheduled-date, scheduled-time, reason, notes, and audit timestamp fields remain unchanged.

## Constraints

The original database-level doctor/date/time uniqueness constraint remains:

```text
unique_doctor_appointment_slot
```

Phase 8 adds:

```text
unique_patient_appointment_slot
```

Together, these prevent one doctor or one patient from having two appointment rows at exactly the same date and time. Application-level conflict checks run before insert and convert race-condition integrity errors into HTTP 409 responses.

## Migration

```text
backend/apps/appointments/migrations/0002_alter_appointment_status_and_more.py
```

The migration alters only the status choices/default and adds the patient slot constraint. It does not delete data, drop tables, reset migration history, or create a new appointment table.

## Lifecycle

```text
pending → confirmed
pending → rejected
pending → cancelled
confirmed → cancelled
confirmed → completed
```

Terminal states are `rejected`, `cancelled`, and `completed`. The API, not the frontend, controls transitions.

## Deferred data

Clinical records, prescriptions, reports, diagnosis, treatment plans, lab results, clinical notes, and AI data are not part of the appointment schema update.
