# AI Data Requirements

## Scope

This document defines what future AI tasks may legitimately request from the existing MediCare data model. It does not authorize a model, a training dataset, or use of real patient data. Every future request must be minimized, ownership-checked, purpose-bound, and documented.

## Feature inventory

| Feature or source | Type and known values | Source | Missing-value behavior | Validation | Privacy considerations |
|---|---|---|---|---|---|
| Patient role/profile identity | Categorical role; patient/doctor/administrator | `accounts.User`, `PatientProfile` | Omit unless task requires role context | Must match authenticated request context | Never use email or name as a predictive feature by default |
| Date of birth/age | Date; age derived only when task-approved | `accounts.User.date_of_birth` | Missing remains missing; never guess | Date cannot be in the future; derived age must be bounded | Sensitive demographic attribute; use only with explicit justification |
| Gender | Free-text current field; no controlled vocabulary beyond frontend values | `accounts.User.gender` | Omit if blank | Must be treated as untrusted categorical input | Sensitive attribute; exclude by default and assess fairness impact |
| Blood group | Controlled values `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`, `unknown` | `PatientProfile.blood_group` | `unknown` remains unknown; no inference | Must match model choices | Sensitive clinical data; use only when clinically relevant |
| Medical-record type | `lab_test`, `consultation`, `imaging`, `prescription`, `other` | `MedicalRecord.record_type` | Missing is invalid for a record | Must match model choices | Patient-owned clinical data; access is server-authorized |
| Record date | Date | `MedicalRecord.occurred_on` | Required for existing record | Cannot be impossible relative to allowed task window | Temporal data can reveal care events |
| Diagnosis text | String up to 255 characters | `MedicalRecord.diagnosis` | Missing is invalid for the record, but not automatically a model feature | No automatic clinical interpretation in Phase 11 | Highly sensitive; no free-text training without governance |
| Record notes | Free text | `MedicalRecord.notes` | Omit by default | Size and encoding checks only until a task is approved | May contain unnecessary identifiers; minimize and redact later |
| Report type/status | Controlled report type and status | `MedicalReport` | Status remains explicit; no inference | Must match choices | Patient-owned clinical data |
| Report summary/interpretation | Free text | `MedicalReport.summary`, `interpretation` | Omit when blank | No automatic interpretation in Phase 11 | Sensitive clinical narrative; secure processing required |
| Report finding label/value | Strings; `is_normal` boolean; ordered findings | `ReportFinding` | Missing finding is not imputed | Preserve label/value; no invented units/ranges | May contain laboratory data; units are not currently modeled |
| Prescription status/dates | Controlled status plus dates | `Prescription` | Optional end date remains null | Existing model constraints apply | Medication data is sensitive |
| Prescription medicine/dosage | Free text | `PrescriptionItem` | Missing medicine/dosage is invalid for a future medication task | Requires normalization only after approved vocabulary | No interaction claims without authoritative source |
| Appointment status/date/reason | Controlled status, date/time, free text reason | `Appointment` | Missing reason remains blank | Status and date follow existing API/model constraints | Used primarily for ownership/authorization, not diagnosis |

## Data not currently available

The current schema has no persistent symptom events, structured laboratory units and reference ranges, normalized medication identifiers, diagnosis/outcome labels for prediction, consent records for AI processing, model-training dataset version, or provenance record for external medical knowledge.

## Future minimum requirements

A future task must define the smallest feature subset, allowed value/range rules, missingness policy, redaction requirements, retention policy, and authorization query before implementation. Free text and attachments must not be sent to a model by default. Real patient data must not be used for training without explicit authorization and privacy review.
