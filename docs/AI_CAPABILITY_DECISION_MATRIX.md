# Phase 16 AI Capability Decision Matrix

**Decision status:** **READY FOR PHASE 17 MODEL IMPLEMENTATION**, subject to the documented Phase 17 authorization and final pre-training verification gates.  
**Selected first capability:** **Academic disease-risk classification using the UCI Heart Disease dataset label transformation.**

## Candidate capability comparison

| Candidate | SRS alignment | Dataset availability | Target clarity | Feature availability | Evaluation feasibility | Safety/integration assessment | Decision |
|---|---|---|---|---|---|---|---|
| Disease-risk classification | Directly named by the SRS as disease risk prediction; can be bounded as an academic dataset-label classification task | UCI Heart Disease has an official repository page, 303 instances, 13 commonly used features, a documented `num` field, missing-value notice, DOI, and CC BY 4.0 license [1] | Clear after an explicit binary transformation: `0` versus `1–4`; this remains a dataset label, not a diagnosis | Compact tabular feature schema is documented; no identifiers are used as model features | Binary classification supports stratified holdout, cross-validation, discrimination, recall/specificity, PR-AUC, and calibration review | Can remain informational and disconnected from MediCare patient data; no autonomous action or clinical claim | **Selected** |
| Symptom-based risk classification | Appears in SRS capability list and former UI demonstration | No approved symptom dataset or label corpus exists in the project; no official task-specific corpus was selected | Missing symptom vocabulary, severity/context schema, label source, and escalation/abstention target | Current clinical models do not contain a structured symptom table | Not reproducible without a label policy and task-specific corpus | High risk of converting a demo into unsupported clinical advice | Not selected |
| Medical-report classification | Appears in SRS capability list | Current report models have structured fields but no approved annotated corpus or licensed attachment/text dataset | Missing report categories, annotation protocol, label quality, and permitted attachment/text handling | Existing report fields are not a labeled corpus and attachments are deferred metadata-only | Requires annotation and document governance before evaluation | Sensitive and potentially high-risk; no data authorization | Not selected |
| Heart-failure survival classification | Public UCI candidate has a documented binary death-event target and CC BY 4.0 license [2] | Officially documented, but only 299 records and a narrower cohort of patients with heart failure | Clear target, but the intended MediCare use would imply survival-risk claims not supported by current SRS | Numeric clinical schema is documented | Technically feasible but clinically more specific and risk-laden | Poorer fit to general MediCare scope; avoid implying survival prognosis | Not selected |
| Diabetes health classification | Broad health-survey classification candidate with 253,680 instances and documented classes [3] | UCI page identifies an external linked source for license/acknowledgment rather than stating a direct license on the page | Target is documented, but source/license authorization requires separate verification | Includes sensitive demographic, income, and education fields requiring minimization | Technically feasible | Licensing and feature/privacy review are incomplete; not selected | Not selected |
| Appointment no-show prediction | Plausible operational ML task | No approved no-show dataset or target exists; current Appointment model does not contain historical no-show labels | Target and observation window are absent | Current appointment fields are insufficient for a validated no-show outcome | Not reproducible without historical outcome data | Not explicitly required by the SRS; would require new labels and governance | Not selected |

## Final decision

The first capability is **academic disease-risk classification**, defined narrowly as predicting the UCI dataset’s transformed label from the approved UCI feature subset. The future model output must be described as a model-generated classification of a public dataset label, not as a diagnosis, prognosis, or clinical determination.

The UCI Heart Disease candidate is preferable because the official source documents the classification task, feature types, 303-instance size, missing-value presence, target encoding, removal/replacement of personal identifiers, DOI, and CC BY 4.0 license [1]. The future Phase 17 implementation must still record the dataset version/hash, preserve attribution, profile missingness and duplicates, and repeat the data gate before training.

## Primary future algorithm

**Logistic Regression** is selected for Phase 17 as the primary algorithm because the proposed task is binary classification, the feature set is compact and mixed-type, the model is computationally modest, its coefficients can support bounded feature-association explanations, and it provides an academically understandable baseline for a healthcare-safety-oriented prototype. It is not selected because it is guaranteed to perform well, and no performance is claimed in Phase 16.

Reasonable alternatives are a shallow Decision Tree and Random Forest. A shallow Decision Tree is easier to visualize but may be unstable and appear more certain than justified. Random Forest can represent nonlinear interactions but is less transparent and would require additional calibration and explanation controls. Neither alternative is preferred over Logistic Regression for this first, deliberately conservative academic capability.

## Status interpretation

`READY FOR PHASE 17 MODEL IMPLEMENTATION` means that Phase 16 has produced a concrete, evidence-backed specification and recommended public source. It does **not** mean that a model is trained, that the dataset has been downloaded, that the owner has waived final review, or that the model is clinically validated. Phase 17 must reverify the source, license, dataset hash, feature/target mapping, privacy controls, and training authorization before any download or training.

## References

[1]: https://archive.ics.uci.edu/dataset/45/heart+disease "UCI Heart Disease dataset"
[2]: https://archive.ics.uci.edu/dataset/519/heart+failure+clinical+records "UCI Heart Failure Clinical Records dataset"
[3]: https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators "UCI CDC Diabetes Health Indicators dataset"
