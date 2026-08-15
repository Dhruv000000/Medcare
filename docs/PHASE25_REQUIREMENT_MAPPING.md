# Phase 25 Requirement Mapping — AI Prediction Reporting and Protected Auditability

**Decision:** `IMPLEMENTATION JUSTIFIED — MINIMAL SCOPE ONLY`  
**Authoritative baseline:** Verified MediCare Phase 24  
**Phase boundary:** Implement Phase 25 only; do not start Phase 26.

## 1. Evidence reviewed

| Source | Relevant requirement or boundary | Decision impact |
|---|---|---|
| `docs/AI_REQUIREMENTS_MATRIX.md` | AI auditability is a future data responsibility; the bounded Phase 11 decision is minimum audit fields, not a broad audit system | Supports a minimal operational audit record, not unrestricted history |
| `docs/PHASE17_API_FRONTEND_PLAN.md` | If audit persistence is later approved, store model/preprocessing versions, status, timestamps, and safe operational metadata; do not store raw feature payloads or attach predictions to clinical records without separate governance | Defines the minimum data-minimization contract |
| `docs/PHASE18_AI_API.md` | The existing prediction endpoint is authenticated, stateless, accepts no patient ID, does not query clinical records, and does not create prediction history | Phase 25 is a deliberate additive reporting layer; the prediction endpoint’s input and authorization boundary remain unchanged |
| `docs/AI_SRS_TRACEABILITY.md` | Phase 23 explanations are transient and no prediction history was previously introduced; Phase 24 preserves the same boundary | Requires explicit Phase 25 traceability and preservation checks |
| `pasted_content_31.txt` | Phase 25 explicitly authorizes evaluation and implementation of a secure prediction-reporting/protected-auditability layer where justified | Provides the current phase authorization |

## 2. Supported Phase 25 capability

The reviewed requirements support a **minimal server-side AI prediction event record** for authorized inference activity and a protected report representation of completed results. The record is not a patient medical record, does not contain a patient identifier, does not attach to a Phase 24 clinical record, and does not store the complete submitted feature payload.

The completed report stores the fixed model version, server-generated event identifier and timestamp, authenticated requesting user/role, outcome status, prediction label, model probability, and a minimized model-tied explanation containing only feature names, signed contributions, direction, method, preprocessing version, output space, and base value. Submitted feature values are excluded from persistence.

Doctors may list and retrieve only their own completed prediction reports. This is the only report scope justified because the existing Phase 18 endpoint deliberately accepts no patient or clinical-context identifier; therefore a patient-linked doctor history cannot be authorized without inventing a new privacy/governance requirement. Administrators receive only aggregate audit counts by status/model version and no detailed prediction or patient data. Patients receive neither prediction access nor prediction history.

## 3. Audit events

The unified event record may capture only the following server-generated statuses: `completed`, `validation_failed`, `inference_failed`, `model_unavailable`, and `unauthorized`. Rejected/unauthorized events contain no request payload, feature values, patient identifiers, clinical data, credentials, CSRF tokens, session identifiers, or uploaded files.

The event model has no client-writable fields, no client-facing create/update endpoint, immutable server-controlled identity/timestamp/user/role/model/result fields, and no raw request/result payload column. Ordinary clients cannot alter or delete events.

## 4. Explicitly unsupported or deferred features

The current SRS and Phase 18 contract do not justify patient-facing prediction history, arbitrary patient-ID lookup, clinical-record-linked prediction reports, cross-doctor history, unrestricted Admin detailed history, raw feature-payload persistence, raw explanation input values, raw medical files, cryptographic audit chains, treatment recommendations, diagnosis, emergency workflows, autonomous actions, a second model, or a second prediction endpoint.

These features remain deferred or blocked rather than being invented for convenience.

## 5. Authorization decision

| Actor | Prediction endpoint | Detailed report access | Audit summary |
|---|---|---|---|
| Unauthenticated | Denied | Denied | Denied |
| Patient | Denied, preserved from Phase 18 | Denied; no frontend/history | Denied |
| Authorized doctor | Allowed, preserved | Own completed reports only | Denied |
| Unrelated doctor | Allowed to use the stateless endpoint under existing policy, but cannot access another doctor’s report because reports are requester-scoped | Denied with safe 404 | Denied |
| Administrator | Allowed, preserved | No detailed reports | Aggregate counts only, with no patient or raw prediction data |

## 6. Acceptance criteria

Phase 25 is accepted only if the implementation passes focused event/report tests, all Phase 17–24 regression tests, authorization and privacy scans, frontend contracts, AI artifact checksum/determinism checks, synthetic browser smoke tests for doctor/patient/Admin/logout behavior, and archive validation. The Phase 17 model checksum must remain `e548527e51c67a7b611501acc844b367cecdde53413e33914ed9757fb9bae6cd` and exactly one AI prediction route must remain.
