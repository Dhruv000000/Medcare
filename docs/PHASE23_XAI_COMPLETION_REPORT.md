# MediCare Phase 23 XAI Completion Report

**Project:** MediCare — Intelligent Clinical Decision Support System  
**Phase:** 23 — Model-Tied Explainable AI  
**Status:** **COMPLETE**  
**Completion date:** 15 August 2026  
**Source of truth:** `/home/ubuntu/audit_project/medicare_phase2`  
**Next phase:** **Phase 24 deferred and not started**  
**Author:** Manus AI

> Phase 23 added only model-tied explainability for the existing academic `uci-heart-disease-logreg-v1.0.0` Logistic Regression workflow. The model artifact, preprocessing, endpoint, authorization boundary, patient denial, CSRF protection, rate limiting, privacy boundary, and clinical-safety boundary were preserved.

## 1. Phase status

Phase 23 is complete. A native Logistic Regression explanation was implemented inside the existing authorized inference workflow. The explanation is generated from the checksum-verified fitted artifact after the existing request serializer has accepted the exact 13-feature contract. No second model, generic explanation, external AI provider, database persistence, patient-facing prediction, or autonomous clinical action was introduced.

The implementation is technically validated for the existing controlled development/staging boundary. It is not a claim of clinical validation, medical-device compliance, diagnostic accuracy, causal explanation, or production clinical readiness.

## 2. Executive summary

The selected XAI method is a native coefficient-contribution decomposition. For each validated input, the service uses the existing fitted preprocessor to transform the row, multiplies each transformed value by the corresponding fitted Logistic Regression coefficient, aggregates transformed contributions back to the original 13 source features, and returns the fitted intercept as a model base value. The sum of the base value and feature contributions is checked against the same pipeline's `decision_function`.

The existing `POST /api/ai/heart-risk/predict/` endpoint now returns an additive `explanation` object. The existing doctor dashboard renders all 13 feature contributions through safe DOM construction, with signed logit-unit values and textual direction labels. Patient access remains denied. The model checksum remains `e548527e51c67a7b611501acc844b367cecdde53413e33914ed9757fb9bae6cd`.

## 3. SRS requirements addressed

The implementation addresses the Phase 16 explanation specification, which calls for coefficient-based associations labeled as model behavior rather than medical reasoning [1]. It also follows the Phase 17 explainability plan requiring model version, accepted feature values, output, safe wording, and fail-closed behavior for invalid input or artifact incompatibility [2]. Phase 18–22 authorization, privacy, and safety requirements remain intact [3] [4] [5].

| Requirement | Actual Phase 23 result | Status |
|---|---|---|
| Real model-tied explanation | Contributions generated from the loaded fitted pipeline, transformed row, coefficients, and intercept | **Implemented and verified** |
| Existing preprocessing reuse | Existing Phase 17 fitted imputer, scaler, and one-hot encoder reused unchanged | **Preserved** |
| Human-readable feature mapping | All 13 original feature names returned in established order | **Implemented** |
| Explanation consistency | Additive explanation matches the model decision function | **Verified** |
| Invalid-input boundary | Explanation generation occurs only after existing serializer validation | **Preserved** |
| Authorization | Active doctor and administrator access preserved; patient and unauthorized access denied | **Preserved and verified** |
| Safe clinical language | Model behavior only; no causal, diagnostic, treatment, or medical-advice claim | **Implemented** |
| Transient privacy | No prediction or explanation persistence, identifiers, patient lookup, or database changes | **Preserved and verified** |
| Doctor frontend integration | Contribution section added to the existing result card | **Implemented** |
| Patient denial | Patient page remains limited-access and direct patient request returns HTTP 403 | **Preserved and verified** |

## 4. XAI method selection

The selected method is `logistic_regression_native_coefficient_contribution`. It is a local additive explanation in the Logistic Regression decision space. It is not SHAP, LIME, Grad-CAM, a generic template, or a post-hoc fabricated narrative.

The Phase 17 and Phase 16 specifications already identify signed Logistic Regression coefficient associations as the approved primary explanation direction [1] [2]. Artifact inspection confirmed a fitted `ColumnTransformer` followed by a fitted `LogisticRegression` classifier. The optional `shap` and `lime` packages were not available in the backend environment, and adding either dependency was unnecessary for this model and would have expanded the dependency and governance surface.

## 5. Why the selected method fits Logistic Regression

For the existing binary Logistic Regression pipeline, the model's decision function is an intercept plus the sum of transformed feature values multiplied by fitted coefficients. The explanation therefore uses the same mathematical objects used by the model rather than approximating the model with a second explainer. This makes the explanation deterministic, lightweight, auditable, and directly testable against the model's `decision_function` [6].

Categorical inputs are represented by the fitted one-hot encoder, while numeric inputs are represented after the fitted imputation and scaling steps. Contributions from transformed columns are aggregated to the corresponding source feature. Because each validated categorical input activates its fitted one-hot category and each numeric source feature has one transformed column, the returned 13-feature aggregation preserves the exact additive contribution for the submitted row.

## 6. Why unsupported methods were not used

SHAP and LIME were not added because they were not required by the approved project specification, their dependencies were unavailable, and the native Logistic Regression decomposition is more direct for this fixed pipeline. Grad-CAM was not used because it is designed for differentiable image-style architectures rather than this tabular Logistic Regression model. No LLM, chatbot, RAG system, external provider, second model, or generic explanation template was introduced.

## 7. Model architecture

The model remains the Phase 17 serialized bundle `uci-heart-disease-logreg-v1.0.0.joblib`. The runtime loads it only from the fixed internal path after verifying the adjacent SHA-256 file, bundle type, model version, exact feature schema, and required inference methods [3]. The fitted pipeline contains the existing preprocessing step followed by the Logistic Regression classifier.

The model artifact was not retrained, refitted, converted, optimized, replaced, or re-exported. The actual artifact checksum before and after Phase 23 is:

```text
e548527e51c67a7b611501acc844b367cecdde53413e33914ed9757fb9bae6cd
```

## 8. Preprocessing architecture

The existing Phase 17 preprocessing is reused without modification. Numeric features use the fitted median imputer followed by `StandardScaler`. Categorical features use the fitted most-frequent imputer followed by `OneHotEncoder(handle_unknown="ignore", sparse_output=False)`. The Phase 23 explanation layer calls the fitted preprocessor's `transform` method and never calls `fit` or `fit_transform`.

The exact accepted feature order remains: `age`, `sex`, `cp`, `trestbps`, `chol`, `fbs`, `restecg`, `thalach`, `exang`, `oldpeak`, `slope`, `ca`, and `thal` [3]. The backend continues to reject missing, unknown, non-finite, out-of-domain, and unsupported source-coded values before inference or explanation generation.

## 9. Explanation generation process

The service receives only the serializer-approved feature mapping and the prediction returned by the existing pipeline. It obtains the fitted preprocessor and classifier from the already checksum-verified bundle. It transforms the one-row input, obtains fitted transformed feature names and coefficients, computes each transformed contribution, maps each transformed name to an original feature, and sums contributions by original feature.

The explanation also includes the fitted intercept as `base_value`, `output_space: logit`, a stable method identifier, a preprocessing-version identifier, the accepted feature values, and an explanation-specific disclaimer. The service checks that all contributions are finite, that all 13 source features are represented, and that the additive decision boundary agrees with the model prediction.

## 10. Feature mapping

The transformed names are mapped as follows:

| Fitted transformed form | Returned source feature |
|---|---|
| `numeric__<feature>` | The matching numeric feature, such as `age` or `oldpeak` |
| `categorical__<feature>_<source-code>` | The matching categorical source feature, such as `cp` or `thal` |

The API returns one row per original source feature in the established 13-feature order. Each row contains the accepted value, signed contribution in logit units, and one of `supports_predicted_class`, `opposes_predicted_class`, or `neutral`.

## 11. API changes

The existing endpoint and route were preserved:

```text
POST /api/ai/heart-risk/predict/
```

The successful response retains `model`, `prediction`, `model_probability`, `status`, and `disclaimer`, and now includes the following additive structure:

```json
{
  "explanation": {
    "method": "logistic_regression_native_coefficient_contribution",
    "preprocessing": "phase17_numeric_median_scaler_categorical_mode_onehot_v1",
    "output_space": "logit",
    "base_value": -0.0257904165105582,
    "features": [
      {
        "feature": "age",
        "value": 55.0,
        "contribution": -0.0031,
        "direction": "supports_predicted_class"
      }
    ],
    "disclaimer": "Feature contributions describe this model's behavior for the submitted values. They do not establish biological causation, clinical importance, diagnosis, treatment advice, or medical certainty."
  }
}
```

The nested response serializer strictly permits the known explanation structure. Existing error handling, generic failure responses, request-size handling, CSRF behavior, and throttle behavior remain unchanged.

## 12. Frontend changes

The existing doctor AI result card now contains a small semantic section titled **Model feature contributions**. The section uses the original 13 feature names, accepted values, signed logit-unit amounts, direction text, and a responsive comparison bar. Color is not the sole carrier of meaning because each row also states whether the contribution supports, opposes, or is neutral for the predicted class.

The JavaScript validates the explanation structure before rendering. It uses `createElement`, `textContent`, `append`, `replaceChildren`, controlled class names, and bounded visual widths. It does not use raw API HTML, `innerHTML`, `eval`, dynamic function construction, browser storage, patient identifiers, or clinical-record fields. Existing dashboard layout, visual identity, navigation, loading behavior, and result wording were preserved.

## 13. Authorization behavior

The server remains authoritative. Active doctors and administrators remain allowed to use the existing endpoint. Unauthenticated users, patients, inactive doctors, and unauthorized roles remain denied. Explanation generation is not reachable through a patient page or a separate patient endpoint. No administrator dashboard was invented because existing requirements authorize API access but do not require a separate Admin XAI interface.

## 14. Security review

The Phase 22 security controls remain present. The fixed artifact path and SHA-256 validation are unchanged. No user-controlled model path, upload, serialized-object input, arbitrary file access, path traversal, external AI call, new endpoint, dynamic model selection, or runtime training path was introduced.

The Phase 23 scoped security scan passed all checks for the single route, CSRF boundary, external-provider absence, no runtime refitting, no patient identifiers/history, no file/model-path input, safe AI DOM APIs, patient-page denial, frontend artifact absence, secret-pattern absence, safe wording, and artifact checksum. The previous Phase 22 static scan also passed.

## 15. Privacy review

The endpoint still accepts only the approved 13 feature values. It does not accept a patient ID, clinical-record ID, uploaded file, free-text note, appointment, prescription, or report. Explanations remain transient in the response and browser DOM. No database model, migration, prediction history, explanation history, localStorage entry, sessionStorage entry, or patient-data lookup was added.

The browser smoke environment used synthetic accounts and the fixed public-dataset feature vector only. The disposable SQLite database was stopped and the original local SQLite file was restored. PostgreSQL was not accessed.

## 16. Clinical-safety review

The explanation is explicitly described as model behavior. It does not establish biological causation, clinical importance, diagnosis, treatment advice, prognosis, emergency action, or medical certainty. The doctor remains responsible for clinical interpretation and decision-making. The underlying model remains academic, development-only, trained on a small historical public dataset, and not clinically validated [2] [3].

The interface does not say that AI diagnosed a patient. It continues to use safe language such as **Academic AI Risk Classification**, **model probability**, and **model feature contributions**. The probability is not relabeled as confidence, diagnostic certainty, or a clinical risk percentage.

## 17. Model checksum

The exact required checksum passed after implementation:

| Artifact | SHA-256 | Result |
|---|---|---|
| `uci-heart-disease-logreg-v1.0.0.joblib` | `e548527e51c67a7b611501acc844b367cecdde53413e33914ed9757fb9bae6cd` | **PASS** |

The deterministic Phase 22 output check also remained unchanged for the fixed synthetic vector: `label_absent` with model probability `0.16164121253810007`.

## 18. Tests

All results below are actual executed results.

| Validation | Actual result |
|---|---:|
| AI regression suite | **40 passed** |
| Focused Django AI API suite after Phase 23 additions | **23 passed** |
| Full Django suite | **81 passed** |
| Django system check | **Passed; 0 issues** |
| Migration check | **Passed; no changes detected** |
| New backend XAI tests | Included in the 23 focused API tests; consistency, determinism, input gating, and feature-change tests passed |
| Existing doctor frontend contract | **PASS** |
| New Phase 23 frontend XAI contract | **PASS** |
| Frontend contract scripts | **3 passed** |
| JavaScript syntax | **Passed** |
| Python compilation | **Passed** |
| Frontend references | **142 checked; 0 broken** |
| CSS integrity | **Passed; 149 balanced braces and required selectors present** |
| Phase 22 static security scan | **Passed** |
| Phase 23 scoped security scan | **Passed; all checks true** |
| Deterministic model output | **PASS** |
| Artifact checksum | **PASS** |
| AI route count | **1** |
| New migrations | **0** |

## 19. Browser smoke results

The browser smoke test used synthetic doctor and patient accounts, a disposable SQLite database, the existing local frontend origin, and the fixed synthetic 13-feature vector. No real patient data or PostgreSQL was used.

| Smoke step | Actual result |
|---|---|
| Doctor login | **PASS** |
| Doctor dashboard | **PASS** |
| Existing AI card | **PASS** |
| Valid 13-field entry | **PASS** |
| Prediction rendering | **PASS — `label_absent`** |
| Probability rendering | **PASS — `0.16164121253810007`** |
| Model version rendering | **PASS — `uci-heart-disease-logreg-v1.0.0`** |
| XAI explanation rendering | **PASS — all 13 contributions rendered** |
| Contribution direction text | **PASS** |
| Interpretation disclaimer | **PASS** |
| Invalid input rejection | **PASS — age 28 rejected before API call** |
| Patient login | **PASS** |
| Patient limited-access AI page | **PASS** |
| Direct patient prediction attempt | **PASS — HTTP 403** |
| Logout/session invalidation | **PASS at application API level — before 200, logout 200, after 403** |
| Navigation back to login | **PASS** |

The browser harness timed out once on the patient-page logout click. This was not treated as a successful click result. The same application logout API was then verified through its existing CSRF/session flow, returning `logout_status=200` and a subsequent unauthenticated `/api/auth/me/` status of `403`. No stack trace, raw JSON dump, filesystem path, artifact path, secret, or patient identifier was visible in the tested UI.

## 20. Performance observations

A local warm-path observation used 30 repeated calls with the fixed synthetic vector after the model was loaded. The combined prediction-plus-explanation operation produced the following actual sandbox measurements:

| Observation | Value |
|---|---:|
| Samples | 30 |
| Minimum | 18.3555 ms |
| Median | 19.4880 ms |
| Mean | 19.6673 ms |
| Maximum | 22.2954 ms |
| Explanation rows | 13 |

These are local development observations, not a production service-level objective, capacity benchmark, or clinical performance result.

## 21. Known limitations

The explanation is a local additive decomposition in the Logistic Regression logit space. It describes how the fitted model combines the submitted values for that prediction. It does not prove that any feature caused a biological condition, establish clinical validity, provide treatment guidance, resolve confounding, or establish population-level fairness.

One-hot categorical contributions are aggregated back to the source feature name for readability. This is exact for the current fitted pipeline and input row, but it does not make the source-coded features clinically interpretable. Correlated variables, historical sampling bias, missingness, dataset shift, small sample size, and the public dataset's label semantics remain limitations [2] [3].

The explanation is not a calibrated clinical uncertainty measure. The existing model probability remains an academic model output, not diagnostic confidence or a patient-specific risk estimate.

## 22. Deferred XAI capabilities

The following remain deferred and were not implemented: SHAP, LIME, counterfactual explanations, global feature-importance dashboards, cohort-level fairness explanations, uncertainty quantification, calibration-based clinical interpretation, patient-facing explanations, explanation persistence, explanation audit history, model comparison explanations, natural-language clinical summaries, chatbot/RAG/LLM functionality, recommendations, monitoring, and autonomous action.

Any future expansion requires a separate requirements, safety, privacy, clinical, security, and authorization review.

## 23. Files changed

The following implementation and documentation files were added or modified relative to the Phase 22 project package:

| File | Change |
|---|---|
| `backend/apps/ai_api/constants.py` | Added the immutable preprocessing-version contract label |
| `backend/apps/ai_api/explainability.py` | Added the native model-tied contribution engine |
| `backend/apps/ai_api/serializers.py` | Added strict nested explanation response serializers |
| `backend/apps/ai_api/services.py` | Added explanation generation to the existing prediction response |
| `backend/apps/ai_api/tests.py` | Added four backend XAI consistency, determinism, sensitivity, and input-gating tests |
| `frontend/pages/doctor/doctor-dashboard.html` | Added semantic explanation section inside the existing result card |
| `frontend/js/doctor/doctor-dashboard.js` | Added response validation and safe contribution rendering |
| `frontend/css/doctor/doctor-dashboard.css` | Added compact responsive contribution-row styling |
| `frontend/tests/test_phase23_xai.js` | Added the Phase 23 frontend security/accessibility contract |
| `docs/PHASE23_XAI_DESIGN.md` | Documented method, mapping, safety, privacy, and limitations |
| `docs/PHASE23_XAI_COMPLETION_REPORT.md` | This completion report |
| `docs/AI_ROADMAP.md` | Marked Phase 23 complete and Phase 24 deferred |
| `docs/AI_SRS_TRACEABILITY.md` | Appended Phase 23 traceability mappings |
| `ai/documentation/phase23-final-validation.log` | Final validation evidence |
| `ai/documentation/phase23-security-scan.log` | Scoped security-scan evidence |
| `ai/documentation/phase23-browser-smoke-notes.md` | Browser smoke evidence and the explicit logout harness note |
| `ai/documentation/phase23-performance.json` | Actual local warm-path performance observation |
| `ai/documentation/phase23-package-validation.log` | Final archive integrity, required-file, exclusion, route, and checksum evidence |

## 24. Files intentionally unchanged

The following boundaries were intentionally preserved: `ai/models/artifacts/uci-heart-disease-logreg-v1.0.0.joblib`, its checksum file, Phase 17 training and preprocessing implementation, the existing single AI route, authentication and permission classes, CSRF behavior, rate-limit configuration, patient AI page behavior, database models and migrations, PostgreSQL configuration, external-provider configuration, patient and doctor domain models, and all unrelated dashboard functionality.

The local `backend/db.sqlite3` file was temporarily replaced only inside the disposable browser smoke setup and was restored afterward. It is not a Phase 23 implementation change and is excluded from the final package.

## 25. Phase 24 readiness

Phase 24 is **deferred and not started**. Phase 23 leaves the project at a bounded, technically validated, academic explainability state. Any Phase 24 work requires an explicit new instruction, a fresh scope decision, and a separate safety/security/privacy review. No Phase 24 code, endpoint, model, database structure, patient access, or autonomous behavior was started.

## References

[1]: PHASE16_AI_SPECIFICATION.md "Phase 16 AI implementation specification"
[2]: ../ai/models/PHASE17_EXPLAINABILITY_PLAN.md "Phase 17 explainability plan"
[3]: PHASE18_AI_API.md "Phase 18 secure AI API"
[4]: PHASE21_DOCTOR_AI_RESULT_SAFETY.md "Phase 21 doctor AI result safety"
[5]: PHASE22_COMPLETION_REPORT.md "Phase 22 completion report"
[6]: https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression "scikit-learn Logistic Regression documentation"
[7]: https://archive.ics.uci.edu/dataset/45/heart+disease "UCI Heart Disease dataset"
