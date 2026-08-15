# MediCare Phase 26 Current Requirement Matrix

**Baseline:** Verified Phase 25 MediCare implementation  
**Re-audit date:** 15 August 2026  
**Selected scope:** Doctor-facing clinical workflow continuity using existing authorized record, report, and prescription APIs  
**Decision:** **IMPLEMENTED SCOPE JUSTIFIED; UNSUPPORTED GAPS REMAIN DEFERRED**

## 1. Re-audit method

The current SRS/project documents, Phase 22 audit, Phase 23 report, Phase 24 completion report, Phase 25 reporting/audit report, current Django models/APIs, current frontend pages, and existing regression tests were compared. Historical Phase 9/10 deferrals were not treated as automatically current requirements; each was reclassified against the live Phase 25 code.

## 2. Current requirement status

| Requirement/source | Current Phase 25 status | Remaining gap | Phase 26 decision | Evidence |
|---|---|---|---|---|
| Patient own clinical records | Complete | No supported patient clinical-write requirement | Preserve; no new write workflow | `clinical_api/views.py`, Phase 24 tests/browser smoke |
| Patient protected files | Complete | No additional lifecycle/retention requirement is specified | Preserve; no new file lifecycle invented | Phase 24 report and security scan |
| Doctor authorized record review | Complete at backend and viewer level | No gap requiring a second viewer | Preserve | Clinical API, Phase 24 doctor browser smoke |
| Doctor clinical-record creation | Backend create API complete | Existing dashboard has no integrated create form | **Implement Phase 26 doctor workflow integration** | `DoctorMedicalRecordCreateSerializer`, `/api/doctor/medical-records/`, Phase 9 audit |
| Doctor medical-report creation/review | Backend create API and Phase 24 viewer complete | Existing dashboard has no integrated create form; report lifecycle correction/versioning is unspecified | **Implement create-form integration only; defer correction/versioning** | `DoctorReportCreateSerializer`, `/api/doctor/reports/`, Phase 24 viewer |
| Doctor prescription creation/review | Backend create/list API complete; patient read-only view complete | Existing dashboard has no integrated create form | **Implement create-form integration only** | `DoctorPrescriptionCreateSerializer`, `/api/doctor/prescriptions/`, Phase 9 audit |
| Appointment-to-clinical linkage | Existing appointment authorization and optional record/report links exist | Forms should require an authorized selected patient and optionally selected appointment/record where supported | **Integrate existing linkage fields; no new assignment model** | `Appointment`, clinical serializers, Phase 24 authorization |
| Patient refill request | Deferred | No refill-request model, endpoint, approval workflow, or SRS-approved semantics | `NOT IMPLEMENTED — REQUIREMENT NOT SUFFICIENTLY SUPPORTED` | Phase 9 audit and current patient-prescription placeholder |
| Record/report correction and version history | Deferred | No amendment/version policy, audit semantics, or retention approval | `DEFERRED — DEPENDENCY REQUIRED` | Phase 9 audit and current models |
| Admin detailed clinical/AI history | Restricted by existing minimum-necessary policy | SRS does not authorize unrestricted medical detail | Preserve aggregate/oversight-only behavior | Phase 14, 24, and 25 reports |
| Patient-facing AI | Denied by policy | No SRS authorization for patient prediction | Preserve denial | Phase 18/19/25 evidence |
| AI model, preprocessing, XAI, reporting/audit | Complete within academic boundary | No new AI capability is supported | Preserve unchanged | Phase 17–25 reports and checksum |
| Notifications, refill automation, emergency workflows | Deferred | No approved workflow, safety policy, or endpoint | `DEFERRED — DEPENDENCY REQUIRED` | Historical audit and current source |
| PostgreSQL production validation | Not performed | Sandbox-only validation | Document limitation; do not install/access PostgreSQL | All phase reports |

## 3. Selected Phase 26 implementation

The highest-priority supported gap is the missing doctor-facing workflow continuity between the authorized patient dashboard/clinical viewer and the already implemented doctor create APIs. Phase 26 will add a minimal accessible action panel within the existing doctor clinical-record viewer. It will allow an authorized doctor to create a medical record, medical report with optional findings, or prescription with nested item data for the currently selected authorized patient.

The panel will submit only the existing serializer fields, derive doctor ownership from the authenticated session, require the server to validate patient/appointment/record authorization, use CSRF/session authentication, and render success/error/empty/loading/unauthorized states with safe DOM APIs. No new model, endpoint, clinical terminology, or medical decision rule will be invented.

## 4. Explicit non-scope

Phase 26 will not add patient writes, refill requests, record deletion, record correction/version history, Admin medical-detail access, AI changes, another prediction route, new model artifacts, notifications, treatment recommendations, emergency actions, chatbot/RAG/LLM behavior, or PostgreSQL access.
