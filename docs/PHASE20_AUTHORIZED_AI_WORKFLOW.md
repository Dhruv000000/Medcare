# Phase 20 Authorized AI Workflow

**Status:** Implemented for the authorized doctor workflow; patient-facing AI remains restricted.

## Scope decision

The current SRS and Phase 16–19 documentation support a clinical decision-support/informational role for authorized clinical users, while the Phase 18 implementation explicitly permits active doctors and administrators and denies patients. Phase 20 therefore adds the smallest justified **doctor-facing** interface in the existing doctor dashboard AI panel. It does not change backend permissions.

An administrator may use the existing Phase 18 API under the existing server-side policy, but no new administrator AI dashboard was created because the current SRS does not establish a separate administrator testing/verification interface and a second interface would exceed the minimum justified scope.

Patient-facing AI remains unavailable. The Patient AI Insights page remains in the safe Phase 19 limited-access state and does not call the endpoint.

## Authorized endpoint

```text
POST /api/ai/heart-risk/predict/
```

This is the only AI inference route. The frontend uses the existing `MediCareAuth.apiRequest()` helper, which preserves session credentials and obtains the server-issued CSRF token for the POST request.

## Doctor workflow

The existing doctor dashboard’s `AI Clinical Insights (Deferred)` card was minimally converted into an expandable **Academic AI Risk Classification** form. The form is hidden until the doctor explicitly selects **Open Academic AI Tool**. It uses the existing dashboard card, colors, typography, spacing, buttons, responsive rules, and navigation.

The form has exactly the 13 Phase 17/18 fields:

```text
age, sex, cp, trestbps, chol, fbs, restecg, thalach,
exang, oldpeak, slope, ca, thal
```

Numeric controls use the verified Phase 17 support domains. Categorical controls use the approved source-coded options. The browser performs usability validation only; the Django serializer remains authoritative.

The browser sends a request only after explicit form submission. It disables the submit and clear controls, shows `Analyzing…`, prevents concurrent submissions, sends JSON to the existing endpoint, validates the response structure, renders the result with safe DOM APIs, and restores controls in `finally`.

## Response handling

The frontend accepts only the documented Phase 18 response shape and fixed model version:

| Field | Requirement |
|---|---|
| `model` | `uci-heart-disease-logreg-v1.0.0` |
| `prediction` | `label_absent` or `label_present` |
| `model_probability` | Finite number from 0 through 1 |
| `status` | `academic_development_only` |
| `disclaimer` | Non-empty approved disclaimer string |

The UI calls the probability **Model probability**. It does not call it confidence, diagnosis certainty, or clinical likelihood. It does not calculate additional metrics.

## Error handling

The doctor UI maps the actual Phase 18 status categories to controlled messages:

| Status | UI behavior |
|---:|---|
| 400 | Invalid academic model input message |
| 403 | Unauthorized-role message |
| 429 | Retry-later rate-limit message; no automatic retry |
| 500/503 | AI service unavailable message |
| Network failure | Backend unavailable message |
| Malformed successful response | Invalid-response message |

No raw JSON, stack trace, filesystem path, secret, credential, or Python exception is rendered.

## Security and privacy

The frontend does not implement authorization as a security boundary. The backend remains authoritative. The doctor form does not accept patient IDs or load patient records, prescriptions, reports, appointments, or unrelated clinical data. Requests and responses remain transient and are not stored in localStorage, sessionStorage, cookies, or prediction history.

The model artifact remains server-side. No `.joblib`, `.pkl`, `.onnx`, `.pt`, or `.h5` file is placed in the frontend. No model training, conversion, refitting, external AI provider, chatbot, RAG, LLM, or second endpoint was added.

## Patient restriction

> Patient-facing AI prediction remains unavailable because the current SRS does not explicitly authorize patients to receive the academic heart-risk classification.

The Patient AI Insights page remains unchanged from the Phase 19 safe limited-access decision. It does not submit the doctor form, call the endpoint, or attempt to impersonate an authorized role.

## Academic limitations

The workflow is an academic/development-only integration around the Phase 17 UCI Heart Disease model. It is not clinically validated, is not a diagnosis or medical advice, and must not replace professional medical judgment. Phase 17 evaluation values remain academic dataset results and are not displayed as clinical performance claims in the doctor form.

## References

[1]: PHASE18_AI_API.md "Phase 18 secure AI API documentation"
[2]: PHASE19_FRONTEND_INTEGRATION.md "Phase 19 patient authorization decision"
[3]: ../ai/models/MODEL_CARD.md "Phase 17 model card"
