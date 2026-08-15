# Phase 9 Clinical Data Audit
## Medical records, prescriptions, and medical reports

**Status:** Completed before implementation. This audit uses the Phase 9 requirements, the existing Phase 5 Django models and migrations, the Phase 6 authentication and permissions, the Phase 8 appointment lifecycle, and the current patient-facing HTML/CSS/Vanilla JavaScript pages.

## 1. Phase 9 objective and boundary

Phase 9 adds authenticated clinical-data access to the existing MediCare academic application. The scope is limited to three existing model groups: `MedicalRecord`, `Prescription` with nested `PrescriptionItem` rows, and `MedicalReport` with nested `ReportFinding` rows. The implementation will reuse those models without creating a second clinical schema, without introducing AI or clinical decision-making logic, and without redesigning the current user interface.

The phase is deliberately conservative. Patients receive read-only access to their own clinical data. Doctors receive list and create access only for patients with whom they have an existing appointment relationship. No delete endpoint, no general-purpose doctor-patient directory, no report download service, and no real file-upload workflow will be added in this phase.

## 2. Existing models reused

The three clinical model groups were already created and migrated during Phase 5. Their relationships are sufficient for the Phase 9 API and do not require a new migration.

| Model group | Existing persisted structure | Phase 9 use |
|---|---|---|
| `medical_records.MedicalRecord` | Patient foreign key; optional doctor and appointment references; record type; occurrence date; diagnosis; notes; optional attachment; audit timestamps | Patient list endpoint and authorized-doctor list/create endpoint |
| `prescriptions.Prescription` and `PrescriptionItem` | Prescription owner patient; protected doctor relationship; status; issued/start/end dates; nested medicine, dosage, frequency, duration, instructions, side effects | Patient list endpoint and authorized-doctor list/create endpoint with nested items |
| `reports.MedicalReport` and `ReportFinding` | Patient foreign key; optional doctor, appointment, and medical-record references; title/type/laboratory/date/status; summary/interpretation; optional attachment; ordered findings | Patient list endpoint and authorized-doctor list/create endpoint with nested findings |

The existing migrations confirm that these models are already part of the database schema. Phase 9 therefore requires **no new database tables and no schema migration**, provided that the implementation does not alter model fields or constraints.

## 3. Authentication and ownership rules

All endpoints will use Django session authentication and the existing `IsAuthenticated` plus role-specific permission classes. The authenticated user is the only source of patient or doctor ownership. Request payloads must not be able to replace the owner with a submitted `patient_id`, `doctor_id`, or equivalent field.

For patient requests, the API resolves `request.user.patient_profile`. A patient can retrieve only rows whose `patient` is that profile. A patient cannot create, patch, or delete clinical rows through Phase 9 endpoints. The API will return a role/profile error as forbidden when the authenticated account is not a usable patient account.

For doctor requests, the API resolves `request.user.doctor_profile`. A doctor can retrieve rows that were created by that doctor, as well as rows for patients authorized through the appointment rule below. When creating a row, the doctor must identify a target patient through a validated patient reference, but the server will set the `doctor` field from the authenticated doctor and will independently validate the patient relationship. Protected ownership fields cannot be reassigned through payload data.

## 4. Doctor authorization rule

The existing schema does not contain a formal doctor-patient assignment table. The smallest defensible authorization rule supported by the current database is therefore:

> **A doctor may view or create clinical data for a patient only when at least one appointment exists linking that doctor to that patient.**

The relationship is checked through `appointments.Appointment.objects.filter(doctor=current_doctor, patient=target_patient).exists()`. The check is not limited to a particular appointment status because the database currently records the relationship across the appointment lifecycle, and the Phase 8 appointment API already controls creation and status transitions. This rule avoids unrestricted access while not inventing a new assignment workflow in Phase 9.

A doctor may list their own clinical records, prescriptions, and reports. For list endpoints that expose patient data, the queryset will be restricted to patients with at least one appointment with that doctor. A doctor may not use a patient identifier to bypass this queryset. Detail endpoints are not required for the minimum scope; nested data is returned by the authorized list/create endpoints.

## 5. Serializer design

Serializers will use explicit field lists and will not use `fields = "__all__"`. Read serializers will expose safe, display-oriented values, including human-readable choice labels and doctor/patient summary fields where useful. Nested child serializers will expose prescription items and report findings in stable arrays so the current patient pages can render their existing cards and modals.

Doctor-create serializers will validate the nested child structures and dates, while views will inject the authenticated doctor and resolve the target patient from the server-side authorization check. Patient, doctor, appointment, and attachment ownership fields will not be writable through arbitrary payload data. Attachments will be represented as metadata or a null value rather than accepted as uploaded content.

## 6. File-upload decision

The existing models contain optional `FileField` columns and the current patient pages contain upload controls. However, the Phase 9 requirements do not require secure clinical file storage, download authorization, virus scanning, retention rules, or file lifecycle management. The current upload forms are browser-only demonstrations that append data to an in-memory array; they are not evidence of a completed storage workflow.

Phase 9 will therefore implement **metadata-only clinical APIs**. No endpoint will accept multipart clinical files, and no file will be written to `MEDIA_ROOT`. Existing upload controls will be disabled or converted to a clearly deferred informational action with minimal JavaScript changes, while the surrounding UI structure and visual identity remain unchanged. Download buttons will remain deferred and will not claim to generate a PDF or expose a file URL.

## 7. Deletion and modification decision

No deletion endpoint will be implemented. Healthcare records, prescriptions, and reports should not be silently removed by a patient-facing workflow, and the Phase 9 requirements do not define a retention, correction, audit, or archival process. Patients therefore have read-only access. Doctors can create authorized clinical rows but cannot arbitrarily delete or rewrite existing rows through the Phase 9 API.

If a future phase requires corrections, it should define an auditable amendment or versioning workflow rather than adding an unrestricted `DELETE` operation.

## 8. Existing patient-page audit

The patient medical-record page currently renders a local array with record type, date, doctor, diagnosis, notes, and an icon. Its upload modal includes a file input and a patient-supplied doctor name, both of which conflict with the Phase 9 ownership model. The page will instead load `/api/patient/medical-records/`, render server-backed records, and keep detail/download behavior conservative.

The patient prescription page currently renders a local array containing medicine details, date range, prescriber, status, instructions, side effects, and derived course progress. It has no creation form. The page will load `/api/patient/prescriptions/` and retain its existing filters, tabs, cards, and details modal. The refill button remains a non-persisting deferred action because Phase 9 does not define a refill-request model or endpoint.

The patient report page currently renders title, report type, doctor, laboratory, date, status, summary, findings, and interpretation. Its upload form requires a file and creates a local pending report. The page will load `/api/patient/reports/`, preserve its filters, cards, findings display, and detail modal, and defer the upload/download workflows.

## 9. Planned endpoints

| Method | URL | Access | Purpose |
|---|---|---|---|
| `GET` | `/api/patient/medical-records/` | Authenticated patient | List the current patient’s medical records |
| `GET` | `/api/patient/prescriptions/` | Authenticated patient | List the current patient’s prescriptions with nested items |
| `GET` | `/api/patient/reports/` | Authenticated patient | List the current patient’s reports with nested findings |
| `GET` | `/api/doctor/medical-records/` | Authenticated doctor | List the doctor’s authorized clinical records |
| `POST` | `/api/doctor/medical-records/` | Authenticated doctor | Create a record for an authorized patient |
| `GET` | `/api/doctor/prescriptions/` | Authenticated doctor | List the doctor’s authorized prescriptions |
| `POST` | `/api/doctor/prescriptions/` | Authenticated doctor | Create a prescription with nested items for an authorized patient |
| `GET` | `/api/doctor/reports/` | Authenticated doctor | List the doctor’s authorized reports |
| `POST` | `/api/doctor/reports/` | Authenticated doctor | Create a report with nested findings for an authorized patient |

The initial API uses collection endpoints to keep the surface area small and auditable. There are no patient write endpoints, no delete endpoints, and no attachment endpoints.

## 10. Deferred functionality

The following features remain explicitly outside Phase 9: AI insights, chatbot or RAG behavior, diagnosis generation, medical recommendations, clinical alerts, report-file upload, report-file download, PDF generation, finding upload from a patient, refill persistence, doctor-side clinical management pages, correction/version history, notifications, and production deployment.

## 11. Security and regression expectations

Tests will use fake test data only. They will verify unauthenticated rejection, wrong-role rejection, patient ownership isolation, doctor authorization through appointments, unauthorized doctor rejection, server-derived doctor ownership, protected ownership-field handling, nested prescription and report persistence, and the absence of delete behavior. The full existing Phase 6, Phase 7, and Phase 8 test suites must continue to pass.

Validation will be performed in the isolated Ubuntu sandbox using the project’s SQLite fallback. No claim will be made that the sandbox connected to the user’s Windows PostgreSQL 18.6 instance. Windows/PostgreSQL validation remains a separate user-side step after the completed project is transferred.

## References

[1]: ../backend/apps/medical_records/models.py "Existing MedicalRecord model"
[2]: ../backend/apps/prescriptions/models.py "Existing Prescription and PrescriptionItem models"
[3]: ../backend/apps/reports/models.py "Existing MedicalReport and ReportFinding models"
[4]: ../backend/apps/appointments/models.py "Existing Appointment model and relationship"
[5]: ../backend/apps/accounts/permissions.py "Existing role permissions"
[6]: ../frontend/js/patient/patient-medical-records.js "Existing patient medical-record page logic"
[7]: ../frontend/js/patient/patient-prescriptions.js "Existing patient prescription page logic"
[8]: ../frontend/js/patient/patient-reports.js "Existing patient medical-report page logic"
