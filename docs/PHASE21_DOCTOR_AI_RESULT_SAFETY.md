# Phase 21 Doctor AI Result Safety

**Status:** Complete for the authorized doctor experience.  
**Patient-facing AI:** Remains unavailable.

## Purpose

Phase 21 refines the existing Phase 20 doctor dashboard workflow so an authorized doctor can understand what the academic output represents without confusing it with a diagnosis, clinical confidence, treatment recommendation, or autonomous action.

The implementation continues to use the single existing endpoint and unchanged model:

```text
POST /api/ai/heart-risk/predict/
uci-heart-disease-logreg-v1.0.0
```

## Result interpretation

The doctor result area uses only actual response fields: classification, model probability, model version, academic status, and disclaimer. The probability is labeled **Model probability** and is not transformed into a confidence score, diagnostic certainty, risk percentage, or clinical recommendation.

The result explicitly states:

> Doctor decision boundary: This is informational academic output. The doctor remains responsible for clinical interpretation and decision-making.

The form also explains that model probability is an academic model output, not diagnostic confidence. This is a language and experience refinement only; it does not change the model, preprocessing, endpoint, response, or authorization.

## Clinical safety boundary

The AI does not diagnose, prescribe medication, recommend treatment, update medical history, create prescriptions, change appointments, create clinical notes, alter clinical records, send notifications, trigger emergency actions, or make autonomous decisions. The doctor remains responsible for clinical interpretation and decisions.

No existing appointment, patient, report, prescription, or clinical-record workflow was connected to the result. No patient selection or patient-data mapping was added. The form continues to accept only the approved 13 model inputs.

## Authorization

| Role | Result |
|---|---|
| Active doctor | Allowed by the existing Phase 18 backend policy |
| Administrator | Existing API authorization preserved; no new UI invented |
| Patient | Denied; Patient AI page does not call the endpoint |
| Unauthenticated user | Denied by existing session authentication and permissions |

The frontend does not grant or simulate authorization. The backend remains authoritative.

## Privacy and transient behavior

Inputs and responses remain transient. The implementation does not store model inputs, predictions, probabilities, medical information, or model output in localStorage, sessionStorage, unnecessary cookies, prediction history, or a database. The model artifact remains server-side and is not exposed through frontend assets or static files.

The workflow uses manual synthetic/public-dataset feature values only. It does not automatically load or send patient name, address, phone, email, notes, prescriptions, appointments, or unrelated clinical records.

## Accessibility and safe rendering

The existing labels remain associated with controls. The form uses `aria-describedby` for the explanatory note, the result region uses `role="status"` and `aria-live="polite"`, the error region uses `role="alert"` and `aria-live="polite"`, and focus moves to the first form control when the tool opens.

Dynamic output is rendered through `textContent`, `append`, and `replaceChildren`. Raw API JSON and unsafe HTML injection are not used in the AI result path.

## Patient restriction

> Patient-facing AI prediction remains unavailable because the current SRS does not explicitly authorize patients to receive the academic heart-risk classification.

The Phase 19 limited-access state remains unchanged. Phase 21 does not create a patient form, patient request, patient result, or authorization bypass.

## Deferred functionality

Prediction history, database persistence, automated patient-data extraction, clinical recommendations, autonomous actions, model changes, external AI, chatbot, RAG, LLM, and Phase 22 work remain deferred.

## References

[1]: PHASE20_AUTHORIZED_AI_WORKFLOW.md "Phase 20 authorized AI workflow"
[2]: PHASE19_FRONTEND_INTEGRATION.md "Phase 19 patient authorization decision"
[3]: PHASE18_AI_API.md "Phase 18 secure AI API documentation"
[4]: ../ai/models/MODEL_CARD.md "Phase 17 model card"
