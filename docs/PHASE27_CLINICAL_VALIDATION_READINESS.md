# Phase 27 Clinical-Validation Readiness

**Status:** `EXTERNAL DEPENDENCY — CLINICAL VALIDATION REQUIRED`  
**Model:** `uci-heart-disease-logreg-v1.0.0`  
**Artifact SHA-256:** `e548527e51c67a7b611501acc844b367cecdde53413e33914ed9757fb9bae6cd`

## 1. Current decision

MediCare has **not** performed clinical validation. The existing model was trained and evaluated on the public UCI Heart Disease Cleveland processed dataset for an academic/development demonstration. Its held-out metrics and cross-validation results describe performance against public dataset labels under the documented split; they do not establish safety, clinical validity, diagnostic accuracy, generalizability, or suitability for patient care.

No real MediCare patient data was used, and no real-patient or clinical validation dataset will be created in Phase 27. The current patient AI denial and academic-only doctor boundary remain unchanged.

## 2. Required validation dataset

A genuine validation program would require a separately approved dataset that is representative of the intended deployment population and care setting. The data custodian would need to document provenance, collection period, site(s), data dictionary, licensing/permissions, access controls, de-identification or pseudonymization controls, missingness, measurement units, and version/hash.

The UCI dataset is not sufficient for this purpose. It is the training/development source for the current artifact and must not be presented as an independent clinical validation cohort.

## 3. Population and setting

Before collecting or accessing validation data, the project owner and clinical governance group would need to define the intended users, care setting, geography, age range, sex/gender representation, disease prevalence, referral spectrum, equipment/laboratory context, and any population exclusions. The cohort must reflect the population in which the system would actually be considered for use.

A representative validation population cannot be inferred from the current 303-row historical public dataset. Dataset shift and spectrum bias remain unresolved.

## 4. Inclusion and exclusion criteria

A clinical protocol must specify inclusion and exclusion criteria before outcome review. It should define eligible encounters, required clinical measurements, timing of measurements relative to the reference standard, handling of repeat encounters, and exclusions for missing or invalid measurements. Any exclusions must be prespecified and reported in a flow diagram.

The current application has no approved clinical protocol, patient-consent process, clinical data-access approval, or cohort adjudication workflow.

## 5. Target definition and reference standard

The current model target is a transformed UCI dataset label: `num=0` maps to label absent and `num=1..4` maps to label present. That public label is not a MediCare diagnosis and does not define a validated clinical endpoint.

A clinical study would require a clinically meaningful target definition, an explicit prediction horizon, a reference standard, and a prespecified adjudication procedure. Depending on the intended claim, the reference standard could require clinician adjudication, validated diagnostic criteria, longitudinal outcomes, or another independently justified standard. The reference standard must be defined before evaluating predictions and must be applied independently of model outputs.

## 6. Independent validation cohort

The validation cohort must be independent of training, preprocessing selection, threshold selection, model selection, and explainability design. Ideally it should be temporally, geographically, or institutionally external to the development data. No current project file provides such a cohort.

A future validation package must include cohort counts, exclusions, missingness, prevalence, subgroup composition, data-quality checks, and a locked model/artifact hash.

## 7. Required performance evaluation

The analysis plan should prespecify threshold behavior and report discrimination, classification, and calibration metrics appropriate to the intended use. At minimum, the review should consider sensitivity, specificity, positive predictive value, negative predictive value, likelihood ratios, ROC-AUC, PR-AUC where prevalence makes it relevant, calibration-in-the-large, calibration slope, reliability plots, Brier score, confusion matrices, and confidence intervals. The study must explain the clinical meaning of false positives and false negatives.

The current Phase 17 metrics are not clinical-validation evidence and must not be relabeled as clinical performance.

## 8. Subgroup and fairness analysis

The validation protocol must define clinically and operationally relevant subgroups before analysis. Candidate dimensions may include age bands, sex/gender where clinically justified, race/ethnicity where legally and ethically permitted, site, device, language, comorbidity, disease prevalence, and missingness pattern. Each subgroup requires sample-size justification, uncertainty intervals, performance comparison, error analysis, and a plan for unacceptable disparities.

The current project contains limited descriptive source-coded subgroup analysis only. It does not establish fairness or suitability for clinical use.

## 9. Calibration and threshold assessment

The current model artifact is not clinically calibrated. A clinical validation program would need calibration assessment on an independent cohort, prespecified recalibration rules if allowed, threshold selection tied to clinical consequences, and an explicit decision about whether probability output is appropriate for the intended use. Any calibration or threshold update would require a new governed model version and checksum; Phase 27 must not modify the current artifact.

## 10. External validation and transportability

External validation should be performed on data from a different site, time period, population, or measurement system. Transportability assessment must address prevalence shift, missingness, coding differences, equipment/laboratory differences, and changes in clinical practice. The current project has no external clinical cohort and no evidence of transportability.

## 11. Clinical review and governance approval

Before any clinical use, the project would require documented review by appropriately qualified clinicians, data protection/privacy personnel, security reviewers, statistical or ML reviewers, and the responsible governance authority. The review must approve the intended use, prohibited uses, user interface wording, escalation behavior, monitoring plan, incident process, and change-control procedure.

The project owner must also determine whether legal, regulatory, institutional review board, ethics, medical-device, or other jurisdiction-specific approvals apply. No such approval is claimed in Phase 27.

## 12. Monitoring requirements

If a future approved deployment were ever considered, monitoring would need to cover service availability, input-data quality, missingness, feature-distribution drift, prevalence drift, calibration drift, subgroup performance, false-negative and false-positive review, user overrides, safety incidents, complaints, security events, model-version integrity, and rollback triggers. Monitoring data must have an approved retention and access policy.

The current sandbox contains no production monitoring, clinical incident workflow, prospective outcome feed, or validated drift detector.

## 13. Readiness decision

The current model is **academically reproducible and technically integrity-checked**, but it is **not clinically validated** and **not production-approved for patient care**. The required external dependency is:

> **EXTERNAL DEPENDENCY — CLINICAL VALIDATION REQUIRED**

Phase 27 prepares the protocol and evidence requirements only. It does not access real patient data, perform clinical validation, modify the model, or change AI authorization.

## References

[1]: ../ai/models/MODEL_CARD.md "MediCare academic model card"

[2]: ../docs/AI_DATA_GOVERNANCE.md "MediCare AI data governance"

[3]: https://archive.ics.uci.edu/dataset/45/heart+disease "UCI Heart Disease dataset"
