# Phase 16 AI Decision Log

## Decision 001 — First AI capability

**Decision:** Select academic disease-risk classification using the UCI Heart Disease dataset label transformation.

**Evidence:** The SRS explicitly names disease-risk prediction as a candidate AI capability. The current application contains an AI Insights page but no real AI runtime integration, no structured symptom table, no labeled report corpus, and no model. The UCI Heart Disease official page documents a classification task, compact 13-feature schema, target coding, missing-value notice, official provenance, DOI, and CC BY 4.0 license [1].

**Rationale:** This capability has the clearest bounded input/output contract and the most directly documented public source among the candidates reviewed. It can be implemented as an offline academic experiment without using MediCare patient data or making autonomous medical decisions.

**Rejected alternatives:** Symptom classification remains undefined because the current UI demonstration has no approved structured symptom schema or target. Medical-report classification lacks an annotated/licensed corpus. Heart-failure survival classification is narrower and risks unsupported prognosis claims. CDC diabetes classification has an external linked license/acknowledgment path that requires separate verification and includes sensitive survey features. Appointment no-show prediction is not specified in the SRS and has no historical label source.

## Decision 002 — Dataset source

**Decision:** Recommend UCI Machine Learning Repository Heart Disease dataset 45. Do not download it in Phase 16.

**License:** The UCI page states CC BY 4.0. The license permits sharing and adaptation subject to attribution and other conditions [2]. Phase 17 must preserve citation, DOI, source URL, license notice, and modification notice.

**Residual gate:** The owner must authorize retrieval and use before Phase 17 downloads the dataset. Phase 17 must record the downloaded file hash, exact file/version, schema, row count, missingness, duplicates, target distribution, and retention decision.

## Decision 003 — Target

**Decision:** Derive `disease_label_present` from UCI `num`: 0 maps to 0; 1–4 map to 1; all other values are invalid. This is a dataset label and must not be described as a diagnosis.

## Decision 004 — Primary algorithm

**Decision:** Select Logistic Regression for the first implementation. It is appropriate for a compact binary classification task, supports a transparent coefficient-based explanation, and keeps the first academic model conservative. Decision Tree and Random Forest are documented alternatives; no alternative was trained or benchmarked.

## Decision 005 — Phase 17 safety

**Decision:** Keep training offline and disconnected from patient/doctor/Admin APIs by default. No API endpoint, prediction, confidence, or patient-facing output is authorized in Phase 16. Any future integration requires a separate safety, privacy, human-oversight, and UI-copy approval.

## Decision 006 — Phase 17 readiness

**Decision:** The specification is implementation-ready, but Phase 17 must begin with a final pre-training gate. Readiness does not claim that the dataset is present in the repository, that training is authorized, or that model performance is known.

## References

[1]: https://archive.ics.uci.edu/dataset/45/heart+disease "UCI Heart Disease dataset"
[2]: https://creativecommons.org/licenses/by/4.0/legalcode "Creative Commons Attribution 4.0 International legal code"
