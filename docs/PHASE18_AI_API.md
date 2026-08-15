# Phase 18 Secure AI API

**Status:** Implemented as an authenticated, stateless development-only integration around the Phase 17 artifact.  
**Endpoint:** `POST /api/ai/heart-risk/predict/`  
**Model:** `uci-heart-disease-logreg-v1.0.0`

> This output comes from an academic development-only model trained on the UCI Heart Disease dataset. It is not clinically validated, is not a diagnosis or medical advice, and must not replace a qualified healthcare professional.

## Authentication and authorization

The endpoint uses the existing Django session authentication and CSRF protection. A caller must be authenticated with an active MediCare session and must provide the normal CSRF header for a state-changing POST request.

Phase 18 authorizes **active doctors and administrators**. Patients are denied because this phase does not authorize patient-facing self-assessment, the frontend remains unchanged, and the SRS does not establish a patient-facing clinical-use policy for this academic artifact. No patient identifier is accepted or required. The server never uses a client-supplied patient ID and never queries MediCare patient records for inference.

## Request

The request must be a small JSON object with exactly the following 13 fields. Unknown fields are rejected. Model names, model paths, patient IDs, uploads, prediction IDs, and arbitrary model versions are not accepted.

| Field | JSON type | Required | Domain/validation |
|---|---|---:|---|
| `age` | number | Yes | Finite; verified Phase 17 support domain 29–77 |
| `sex` | integer | Yes | One of source codes 0, 1 |
| `cp` | integer | Yes | One of source codes 1, 2, 3, 4 |
| `trestbps` | number | Yes | Finite; verified Phase 17 support domain 94–200 |
| `chol` | number | Yes | Finite; verified Phase 17 support domain 126–564 |
| `fbs` | integer | Yes | One of source codes 0, 1 |
| `restecg` | integer | Yes | One of source codes 0, 1, 2 |
| `thalach` | number | Yes | Finite; verified Phase 17 support domain 71–202 |
| `exang` | integer | Yes | One of source codes 0, 1 |
| `oldpeak` | number | Yes | Finite; verified Phase 17 support domain 0–6.2 |
| `slope` | integer | Yes | One of source codes 1, 2, 3 |
| `ca` | integer | Yes | One of source codes 0, 1, 2, 3 |
| `thal` | integer | Yes | One of source codes 3, 6, 7 |

The numeric domains are observed support domains in the verified Phase 17 Cleveland training file, not clinical reference intervals or diagnostic thresholds. Values outside them are rejected conservatively rather than transformed automatically. `NaN`, positive/negative infinity, booleans in numeric positions, unexpected strings, nulls, missing fields, and malformed values are rejected.

### Safe synthetic example request

```json
{
  "age": 55.0,
  "sex": 1,
  "cp": 3,
  "trestbps": 130.0,
  "chol": 240.0,
  "fbs": 0,
  "restecg": 1,
  "thalach": 150.0,
  "exang": 0,
  "oldpeak": 1.0,
  "slope": 2,
  "ca": 0,
  "thal": 3
}
```

The request body is limited to 8,192 bytes and file uploads/multipart requests are not supported. The API is stateless and does not store requests, results, prediction history, or medical feature values.

## Response

A successful response has HTTP status `200 OK` and returns the actual output from the fixed Phase 17 pipeline:

```json
{
  "model": "uci-heart-disease-logreg-v1.0.0",
  "prediction": "label_absent",
  "model_probability": 0.123456,
  "status": "academic_development_only",
  "disclaimer": "This output comes from an academic development-only model trained on the UCI Heart Disease dataset. It is not clinically validated, is not a diagnosis or medical advice, and must not replace a qualified healthcare professional."
}
```

`model_probability` is the Logistic Regression model’s probability for the public dataset label-present class. It is called a **model probability**, not medical confidence or diagnostic certainty. No clinical calibration or patient-care interpretation is claimed.

## Errors

| Condition | Status | Response principle |
|---|---:|---|
| Unauthenticated or denied role | 403 | Existing authentication/permission response; no internal details |
| Missing/unknown/invalid field | 400 | DRF field-level validation errors |
| Malformed JSON | 400 | Generic malformed-body message |
| Wrong content type | 415 | JSON only |
| Oversized body | 413 | Generic request-size message |
| CSRF failure | 403 | Existing Django CSRF behavior |
| Fixed model unavailable/checksum/schema failure | 503 | Generic temporary-unavailable message |
| Inference failure | 500 | Generic prediction-failed message |
| Unexpected server error | 500 | Generic unexpected-error message |

Responses do not expose stack traces, filesystem paths, artifact paths, environment variables, secrets, credentials, patient IDs, or internal exception text.

## Model loading and inference boundary

The server uses a centralized service with a fixed internal project path to `ai/models/artifacts/uci-heart-disease-logreg-v1.0.0.joblib`. It verifies the adjacent SHA-256 checksum, validates the bundle version and exact 13-feature schema, and loads the artifact once per process with a bounded singleton cache. No request parameter can select a model, version, file path, or serialized object. No uploaded file is deserialized. The pipeline’s existing preprocessing is used unchanged; the API does not fit, retrain, or modify it.

## Rate limiting and logging

DRF’s built-in `UserRateThrottle` is applied with a scoped rate of **60 requests per minute per authenticated user**, backed by Django’s local cache configuration. No external rate-limiting service was installed. Server logs record only safe metadata such as model version, role, success/failure, and exception type; complete feature payloads, patient identifiers, credentials, secrets, and prediction history are not logged or stored.

## Privacy and integration boundary

The endpoint accepts explicitly submitted feature values only. It does not read patients, profiles, medical records, prescriptions, reports, appointments, or diagnoses from the database. It does not require a patient ID and does not create prediction-history tables or migrations. PostgreSQL is not accessed. The frontend and Patient AI Insights page are unchanged; frontend integration is deferred.

## Limitations

The model was trained on a small public academic dataset and not on MediCare data. It is not clinically validated, externally validated, production-ready, or a diagnostic system. The UCI label is a public dataset label transformed from the source `num` field, not a clinical diagnosis. External/generalization limitations remain substantial.

## References

[1]: https://archive.ics.uci.edu/dataset/45/heart+disease "UCI Heart Disease dataset"
[2]: https://creativecommons.org/licenses/by/4.0/legalcode "Creative Commons Attribution 4.0 International legal code"
