# Phase 16 AI Implementation Specification

**Status:** **READY FOR PHASE 17 MODEL IMPLEMENTATION**  
**Capability:** Academic disease-risk classification using the UCI Heart Disease dataset  
**Training status:** Not trained; no dataset downloaded; no model artifact created  
**API status:** No AI endpoint authorized or created in Phase 16  
**Frontend status:** Unchanged  

## 1. Capability and problem definition

MediCare’s first AI capability will be a bounded academic classification experiment. Given a row of approved public-dataset clinical features, the model will classify the dataset label as **heart-disease label absent** or **heart-disease label present** after the documented transformation of UCI’s `num` field.

This is not a diagnosis, prognosis, treatment recommendation, triage decision, or claim about a MediCare patient. The target is a dataset label derived from angiographic disease-status coding in the UCI source, and the output must be described as a model-generated classification for academic evaluation only [1].

### Intended purpose

The purpose is to demonstrate a reproducible, interpretable, non-autonomous healthcare classification workflow for the academic project. It is not intended for clinical deployment, patient-specific care, emergency decisions, prescription changes, or replacement of a clinician.

### Intended users

During the next implementation phase, only developers/researchers and explicitly authorized academic reviewers should access offline training/evaluation artifacts. No patient, doctor, or administrator frontend will receive model output until a separate integration phase explicitly authorizes it.

### Input → preprocessing → model → output → explanation/evaluation

| Stage | Phase 17 specification |
|---|---|
| Input | Approved UCI Heart Disease feature rows with the 13-feature contract below |
| Preprocessing | Training-fitted imputation, categorical one-hot encoding, numeric scaling, invalid/missing-value validation, and leakage controls |
| Model | Logistic Regression, binary classification, primary algorithm |
| Output | Dataset-label classification: `0 = label absent`, `1 = label present`; no diagnosis wording |
| Explanation | Coefficient-based feature association summary, labeled as model behavior rather than medical reasoning |
| Evaluation | Stratified evaluation with accuracy, balanced accuracy, precision, recall, F1, ROC-AUC, PR-AUC, confusion matrix, and calibration review only where supported by the final protocol |

## 2. Dataset decision

### Selected dataset

**UCI Heart Disease**, UCI Machine Learning Repository dataset 45, DOI `10.24432/C52P4X`, official page: [UCI Heart Disease](https://archive.ics.uci.edu/dataset/45/heart+disease).

The official page documents 303 instances, 13 commonly used features, categorical/integer/real feature types, a classification task, missing values, the `num` target field, and removal/replacement of names and social-security numbers with dummy values [1].

### License and authorization

The official UCI page states **Creative Commons Attribution 4.0 International (CC BY 4.0)**. The CC BY 4.0 license grants rights to reproduce/share and produce/share adapted material subject to attribution and other license conditions [2]. Phase 17 must preserve the UCI citation, DOI, source URL, license notice, and modification notice if the dataset is transformed or redistributed.

The UCI license is a strong public-source basis for an academic implementation, but it does not replace the project owner’s final approval, privacy review, data-retention decision, or institutional requirements. Phase 17 must record the approval decision before downloading.

### Dataset suitability

The dataset is suitable for a small academic binary-classification demonstration because the target transformation and compact feature schema are documented by the official repository. It is not sufficient for clinical validation, production deployment, general population claims, or direct MediCare patient inference. The source cohort, historical provenance, missing values, small sample size, and target semantics require explicit limitations.

### Dataset comparison summary

| Dataset | Target | Features/size | License evidence | Suitability decision |
|---|---|---|---|---|
| UCI Heart Disease | `num`: 0 versus 1–4 | 13 common features; 303 instances | CC BY 4.0 stated on official UCI page | **Selected** |
| UCI Heart Failure Clinical Records | Death event during follow-up | 12 features plus target; 299 instances | CC BY 4.0 stated on official UCI page | Rejected: narrower survival cohort and higher risk of prognosis claims |
| UCI CDC Diabetes Health Indicators | Diabetes/pre-diabetes/healthy label | Survey/health features; 253,680 instances | UCI page refers to linked source licensing; direct license requires separate verification | Rejected: license/authorization not yet verified and sensitive survey features require additional governance |

## 3. Feature schema

The model must use only the documented 13-feature subset and must not use identifiers or unapproved attributes. The official page lists these features and descriptions [1].

| Feature | Type | Meaning/allowed values | Required | Planned preprocessing | Safe exposure |
|---|---|---|---|---|---|
| `age` | Numeric integer | Age in years; validate positive plausible range | Yes | Median imputation if missing; standard scaling | Offline only in Phase 17 |
| `sex` | Categorical/binary | Source-coded sex value | Yes | Explicit category mapping; no unsupported reinterpretation | Offline only; demographic fairness review required |
| `cp` | Categorical | Chest-pain type categories 1–4 | Yes | One-hot encoding; reject unknown codes | Offline only |
| `trestbps` | Numeric integer | Resting blood pressure in mm Hg | Yes | Median imputation; standard scaling; range validation | Offline only |
| `chol` | Numeric integer | Serum cholesterol in mg/dl | Yes | Median imputation; standard scaling; range validation | Offline only |
| `fbs` | Categorical/binary | Fasting blood sugar >120 mg/dl indicator | Yes | Explicit binary mapping; reject invalid codes | Offline only |
| `restecg` | Categorical | Resting ECG result categories documented by source | Yes | One-hot encoding; reject unknown codes | Offline only |
| `thalach` | Numeric integer | Maximum heart rate achieved | Yes | Median imputation; standard scaling; range validation | Offline only |
| `exang` | Categorical/binary | Exercise-induced angina indicator | Yes | Explicit binary mapping; reject invalid codes | Offline only |
| `oldpeak` | Numeric | ST depression induced by exercise relative to rest | Yes | Median imputation; standard scaling; range validation | Offline only |
| `slope` | Categorical | Peak exercise ST-segment slope categories 1–3 | Yes | One-hot encoding; reject unknown codes | Offline only |
| `ca` | Categorical/ordinal | Number of major vessels, 0–3; source missing values possible | Yes | Validate 0–3; impute only under predeclared training-only policy | Offline only |
| `thal` | Categorical | Source-coded thalassemia result values | Yes | Explicit category mapping; source-missing values handled by training-only imputer | Offline only |

No names, social-security numbers, IDs, addresses, phone numbers, emails, dates of birth, medical-record IDs, or MediCare identifiers are model features. If source files contain residual identifier columns, they must be removed before any split and recorded in the preprocessing manifest.

## 4. Target variable

### Target name

`disease_label_present` — a derived binary dataset label.

### Derivation

The source `num` field is integer-valued from 0 to 4. The official page documents the common classification convention of distinguishing absence (`0`) from presence (`1,2,3,4`) [1]. Phase 17 must derive:

```text
num == 0       → disease_label_present = 0 (source label absent)
num in 1..4    → disease_label_present = 1 (source label present)
other values   → invalid record; reject and report
```

The derived target must never be called a diagnosis. It represents the public dataset’s coded label and its transformation only.

### Target quality requirements

Phase 17 must document the class distribution, invalid labels, duplicates, missing target values, and any excluded rows. It must not silently delete large portions of the data. Target-derived fields must never enter the feature matrix.

## 5. Algorithm selection

### Primary algorithm

**Logistic Regression** with a reproducible random seed and a training-fitted preprocessing pipeline is the primary algorithm.

### Justification

Logistic Regression fits a binary classification task, works with a compact mixed categorical/numeric schema after encoding, is computationally lightweight, provides coefficient-based associations suitable for bounded explanations, and is academically understandable. It does not provide causality, medical reasoning, calibrated clinical risk by default, or generalizable clinical performance.

### Alternatives

| Algorithm | Advantages | Disadvantages | Interpretability | Decision |
|---|---|---|---|---|
| Logistic Regression | Simple, fast, coefficient associations, stable baseline | Linear decision boundary; calibration must be assessed | High relative to alternatives, but not causal | **Primary** |
| Shallow Decision Tree | Human-readable split paths; mixed data handling | Unstable, can overfit, may appear overly certain | Moderate; paths are not medical reasoning | Secondary comparison only if Phase 17 protocol permits |
| Random Forest | Nonlinear patterns and interaction handling | Less transparent; requires more explanation/calibration governance | Lower; feature importance is not causality | Rejected as primary |
| Gradient Boosting | Potentially strong tabular performance | More tuning and overfitting risk; higher governance burden | Lower | Rejected as primary |

No algorithm was trained or benchmarked in Phase 16.

## 6. Baseline

The future baseline is a **majority-class classifier** using the most frequent training-label class. It must be computed from training data only and evaluated on the same held-out test set and folds as Logistic Regression. Improvement must be reported only if measured; no Phase 16 performance claim exists.

## 7. Preprocessing plan

Phase 17 must implement the following reproducible sequence without fitting on validation/test data:

1. Verify required columns and reject unknown or unauthorized feature columns.
2. Remove identifier columns before splitting.
3. Validate target values and derive the binary label.
4. Detect and report duplicate rows; define a documented policy before removal.
5. Validate numeric ranges and categorical code sets; invalid records must be reported, not silently discarded in bulk.
6. Fit numeric median imputation on training folds only.
7. Fit categorical most-frequent or explicit-unknown imputation on training folds only.
8. Fit one-hot encoding on training folds only, with an explicit unknown-category policy.
9. Fit standard scaling on numeric training values only.
10. Persist the preprocessing configuration/version alongside the future model artifact.

The Phase 17 implementation must record row counts before/after each exclusion and assert that no target-derived field or test-derived statistic enters preprocessing.

## 8. Train/test and validation strategy

The dataset is small. Phase 17 should use a reproducible stratified protocol such as an 80/20 stratified holdout for final evaluation plus repeated or fixed stratified cross-validation inside the training set for model/baseline comparison. The exact fold count must be recorded before training and must not be chosen after observing test results.

A random seed must be fixed and recorded. If source records include a patient identifier or repeated-patient structure, grouping must be reviewed; no identifier may be used as a feature. A duplicate/near-duplicate audit must be performed before splitting.

The final test set must remain untouched until preprocessing and model decisions are frozen. No validation or test labels may influence feature selection, imputation choices, threshold selection, or calibration.

## 9. Evaluation metrics

Because the future task is binary classification with potentially asymmetric healthcare risks and possible class imbalance, Phase 17 should report only metrics justified by the final protocol:

| Metric | Purpose |
|---|---|
| Balanced accuracy | More informative than raw accuracy if classes are imbalanced |
| Precision | Describes positive predictive correctness for the dataset label |
| Recall/sensitivity | Measures captured positive dataset labels; important for false-negative analysis |
| Specificity | Measures negative-label recognition and false-positive analysis |
| F1 | Summarizes precision/recall tradeoff when appropriate |
| ROC-AUC | Ranking discrimination across thresholds, only with suitable test design |
| PR-AUC | Positive-class performance under imbalance |
| Confusion matrix | Makes false-positive/false-negative counts explicit |
| Calibration review | Required before any probability-like output could be considered; no confidence is exposed by default |

No metric values are produced in Phase 16.

## 10. Explainability plan

The future primary model explanation will use signed Logistic Regression coefficient associations after mapping encoded features back to their source feature names. Explanations must say that the model’s output is associated with the provided feature values; they must not say that a feature caused disease or that the model reasoned clinically.

A future explanation must include the model version, preprocessing version, feature values actually accepted, and a disclaimer that coefficients are statistical model behavior rather than medical reasoning. SHAP/LIME are not required for the primary Phase 17 implementation unless the final model selection changes and the method is justified.

## 11. Bias and fairness plan

Before training, Phase 17 must document representation and class distribution. Where the dataset supports legitimate subgroup analysis, report subgroup sample sizes and appropriate performance metrics without exposing demographic data through the application. Sex is a source feature and demographic subgroup candidate; subgroup results must be reported only when sample sizes are adequate and the protocol is predeclared.

Potential risks include historical sampling bias, sex representation imbalance, measurement differences, target-label bias, missingness patterns, and distribution shift between the UCI cohort and MediCare users. No fairness metric or subgroup result is claimed in Phase 16.

## 12. Healthcare safety boundaries

The model is an academic software component, not a medical device or clinical decision-maker. It must not diagnose, prescribe, treat, change medication, book emergency care, alter records, or replace a physician. Any future output must be labeled informational/model-generated and must include a clear “not medical advice / not a diagnosis” disclaimer.

The model must be unavailable for direct MediCare patient inference unless a later phase explicitly authorizes integration after privacy, clinical, safety, and human-review approval. A future abstention/error state is required for invalid, missing, out-of-range, or unsupported input.

## 13. Future API contract

No API is created in Phase 16. If later authorized, the minimum future contract should be a developer/admin-gated endpoint outside patient self-service APIs:

```text
POST /api/ai/disease-risk/classify/
```

The future request would contain only the approved feature schema, not a patient ID or clinical-record ID. The future response would contain:

```json
{
  "status": "supported|unsupported|invalid",
  "task": "academic_disease_label_classification",
  "model_version": "...",
  "output_label": "label_absent|label_present",
  "explanation": [],
  "disclaimer": "Model-generated academic result; not a diagnosis or medical advice."
}
```

No confidence/probability field is included by default. It may be added only after calibration, safety review, and explicit authorization. The future endpoint must never accept a user-controlled model path, patient record ID, arbitrary raw file, or unvalidated feature dictionary.

## 14. Future Patient AI Insights integration

No frontend change is made in Phase 16. A later integration phase may show a clearly deferred, informational result card only after endpoint authorization, role/privacy review, safe copy review, and an explicit decision about whether patient-facing use is appropriate. The current Patient AI Insights page remains non-predictive/deferred.

## 15. Future database requirements

No database changes are required for offline Phase 17 training. If a later authorized integration needs persistence, it should use a versioned, non-clinical prediction-audit structure that stores model version, preprocessing version, request status, created timestamp, and safe operational metadata without storing raw patient payloads by default. That structure requires a separate privacy/security decision and migration review.

## 16. Dependencies

Phase 16 adds no dependency. Phase 17 should use only the minimal pinned scientific stack required by the implementation, such as the project-approved versions of NumPy/pandas/scikit-learn if required after final environment review. No external AI provider, cloud API, LLM, RAG system, or model-hosting dependency is authorized.

## 17. Reproducibility plan

Phase 17 must record the UCI source URL, DOI, license, dataset file/version/hash, source citation, preprocessing configuration, feature order, target transformation, random seed, split protocol, algorithm settings, Python version, dependency lock/requirements, evaluation script version, and artifact checksum. A clean-room run must be possible without access to MediCare patient data.

## 18. Model versioning plan

Future artifacts should use a version such as `uci-heart-disease-logreg-v1.0.0`, with a model card, dataset hash, preprocessing version, training code commit, dependency manifest, metric report, and safety review status. Any change to features, target transformation, dataset, preprocessing, algorithm, or threshold must increment the appropriate version and invalidate prior evaluation claims.

## 19. Phase 17 readiness gate

Phase 17 is **ready for implementation planning** but must begin with a final pre-training authorization checklist:

| Gate | Required evidence |
|---|---|
| Dataset access | Owner explicitly authorizes retrieval/use |
| Source/license | UCI URL, DOI, CC BY 4.0 notice, attribution plan |
| Data verification | File hash, schema, row count, missingness, duplicates, target distribution |
| Privacy | No MediCare patient export; identifier removal confirmed |
| Feature/target | Exact mapping and invalid-value policy reviewed |
| Algorithm | Logistic Regression selection confirmed |
| Evaluation | Split/seed/metrics protocol frozen before training |
| Safety | Academic-only, non-diagnostic, no endpoint by default |
| Reproducibility | Pinned environment and artifact storage plan |

## 20. Class imbalance handling

Phase 17 must measure class distribution before fitting. Stratified splitting is required. No resampling or class weighting is applied in Phase 16. If imbalance is material, a class-weighted Logistic Regression or another mitigation may be predeclared and evaluated using training folds only; the choice must not be made after observing final test results. Balanced accuracy, recall, specificity, PR-AUC, and the confusion matrix are included to avoid relying on raw accuracy alone.

## 21. Future Admin integration

No Admin AI management is implemented in Phase 16. If a later operations phase requires it, an authorized Admin-only view may expose model status, model version, dataset identifier/hash, evaluation-report location, and safety-review status. It must not expose raw dataset rows, patient data, secrets, arbitrary artifact paths, or an unsafe “approved for clinical use” label. Admin visibility requires server-side authorization and a separate review.

## 22. License permissions and restrictions

The UCI page states CC BY 4.0. Under the Creative Commons legal code, sharing and adaptation are permitted subject to attribution, license notice, modification notice where applicable, and the license’s disclaimer and other conditions [2]. The official source does not identify a separate project-specific permission requirement on the dataset page. Nevertheless, Phase 17 must obtain project-owner authorization, preserve attribution and DOI, record the exact source/version/hash, and check whether any accompanying files or third-party content have terms different from the dataset page.

## 23. Assumptions and unresolved questions

Phase 16 assumes that the UCI page and its stated license remain the governing source at the time of Phase 17 retrieval, that the dataset is used only for the academic offline task, and that no MediCare patient data enters the workflow. Unresolved questions are the owner’s final download/training authorization, the exact file/version/hash retrieved in Phase 17, the final dependency versions, and whether any future patient-facing or Admin-facing display should ever be approved. These questions do not block the specification, but they do block training and runtime integration until resolved.

## References

[1]: https://archive.ics.uci.edu/dataset/45/heart+disease "UCI Heart Disease dataset"
[2]: https://creativecommons.org/licenses/by/4.0/legalcode "Creative Commons Attribution 4.0 International legal code"
[3]: https://archive.ics.uci.edu/dataset/519/heart+failure+clinical+records "UCI Heart Failure Clinical Records dataset"
[4]: https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators "UCI CDC Diabetes Health Indicators dataset"
[5]: ../upload/pasted_content_17.txt "Authoritative Phase 16 prompt"
[6]: ../upload/pasted_content_18.txt "Phase 16 execution instruction"
