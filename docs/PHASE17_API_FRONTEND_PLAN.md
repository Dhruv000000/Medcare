# Phase 17 API and Frontend Integration Plan

## Phase 16 decision

No AI API endpoint, frontend integration, database migration, or UI/UX modification is authorized in Phase 16. The existing Patient, Doctor, and Admin interfaces remain unchanged.

## Future API contract

If a later phase explicitly authorizes integration, a server-side protected endpoint may be designed as:

```text
POST /api/ai/disease-risk/classify/
```

The request must contain the exact 13-feature allow-list and no patient ID, medical-record ID, arbitrary model path, or raw file upload. The response must be versioned and fail closed:

```json
{
  "status": "supported|unsupported|invalid",
  "task": "academic_disease_label_classification",
  "model_version": "uci-heart-disease-logreg-v1.0.0",
  "output_label": "label_absent|label_present",
  "explanation": [],
  "disclaimer": "Model-generated academic result; not a diagnosis or medical advice."
}
```

A probability/confidence field is deliberately omitted until calibration and clinical-safety review approve it.

## Access control

Any future endpoint must use server-side authentication and authorization, CSRF protection where applicable, strict serializer validation, rate limiting, audit-safe metadata, and explicit feature/schema validation. It must not be available to an anonymous user or to arbitrary patient self-service by default.

## Future frontend behavior

A separate later phase may evaluate whether a non-patient-facing academic review page is appropriate. If patient-facing display is ever approved, the current design language should be preserved and the result should appear only as a clearly labeled informational card with invalid/unsupported states and the full disclaimer. No emergency or treatment call-to-action is allowed.

## Future persistence

No migration is required for offline training. If audit persistence is later approved, store only model/preprocessing versions, status, timestamps, and safe operational metadata by default. Do not store raw feature payloads or attach predictions to clinical records without a separate privacy and clinical-governance decision.
