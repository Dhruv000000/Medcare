# Phase 19 Patient AI Insights Frontend Integration

**Status:** **BLOCKED BY AUTHORIZATION REQUIREMENT**

## Decision

The Patient AI Insights page was not connected to `POST /api/ai/heart-risk/predict/` because the current SRS and Phase 18 implementation do not explicitly authorize patients to receive the academic heart-risk prediction.

Phase 18 authorizes only active doctors and administrators and denies patients. The current Patient AI Insights page is explicitly a deferred, patient-facing symptom-demo page, not a 13-feature heart-disease form. The Phase 16 specification states that patient-facing use requires a later explicit decision after endpoint authorization, role/privacy review, and safe-copy review. The Phase 18 API documentation records patient denial as the conservative policy. These sources do not establish a patient-facing prediction requirement.

> The frontend must not bypass a backend permission boundary. A patient page must not impersonate a doctor or administrator, retry through another endpoint, or alter the request to defeat the Phase 18 authorization policy.

## Implemented limited-access behavior

The existing Patient AI Insights page remains in place with its original layout, colors, typography, cards, sidebar, navigation, and responsive structure. No 13-feature medical questionnaire was invented and no API request is made from the patient page.

The minimal behavior change is a safe explanatory state. When the page loads, the existing analysis result area shows a neutral message explaining that patient-facing AI risk classification is unavailable because the backend currently authorizes only active doctors and administrators. The page also states that no prediction request was sent and directs the user to a qualified healthcare professional for medical concerns.

The existing deferred symptom-checker interaction continues to show the same controlled state. The implementation replaces static `innerHTML` rendering with `textContent` and `replaceChildren()` for dynamic messages. The result container has `role="status"` and `aria-live="polite"`, and the existing analysis button has an `aria-controls` relationship. No prediction result, model probability, model version, or patient data is displayed.

## Evidence reviewed

| Source | Finding |
|---|---|
| `docs/AI_REQUIREMENTS_SPECIFICATION.md` | Describes future AI requirements and existing ownership rules but does not authorize patient self-requested prediction |
| `docs/AI_SRS_TRACEABILITY.md` | Records disease-risk prediction as an SRS candidate; Phase 18 authorization is doctors/administrators only and patients denied |
| `docs/PHASE16_AI_SPECIFICATION.md` | States the current Patient AI Insights page remains non-predictive/deferred and requires an explicit patient-facing decision |
| `docs/PHASE18_AI_API.md` | Defines the exact endpoint and explicitly denies patients under the conservative Phase 18 policy |
| `backend/apps/ai_api/permissions.py` | Enforces active doctor/administrator access server-side |
| `frontend/pages/patient/patient-ai-insights.html` | Contains a deferred symptom-demo page, not the approved 13-feature model form |
| `frontend/js/patient/patient-ai-insights.js` | Previously made no API calls and intentionally rendered deferred states |

## Security boundary

No JavaScript authorization logic was added. The page does not call the denied endpoint, does not inspect local storage to grant access, does not create a second endpoint, and does not access the model artifact. No patient records, appointments, prescriptions, reports, or other clinical data are loaded into an AI request. No prediction or feature values are stored in browser storage.

## Requirements to unblock patient-facing integration

Patient-facing prediction requires an explicit product/SRS decision that patients are intended recipients of this academic output, a reviewed role and ownership policy, a decision about whether patients may submit all 13 feature values, safe patient-facing terminology, accessibility and privacy review, and updated backend authorization tests. Any backend permission change would need to be implemented server-side and documented; it must not be simulated by the frontend.

## References

[1]: ../docs/AI_REQUIREMENTS_SPECIFICATION.md "MediCare AI requirements specification"
[2]: ../docs/AI_SRS_TRACEABILITY.md "MediCare AI SRS traceability"
[3]: ../docs/PHASE16_AI_SPECIFICATION.md "Phase 16 AI specification"
[4]: ../docs/PHASE18_AI_API.md "Phase 18 secure AI API documentation"
