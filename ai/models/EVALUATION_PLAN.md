# MediCare AI Evaluation Plan — Phase 13

**Status:** Specification only; **NOT YET EVALUATED**.

## Evaluation prerequisite

Evaluation cannot be designed as a single final metric set until one capability, task type, target, feature schema, and dataset are approved. The plan below defines the minimum framework and must be narrowed before model implementation.

## Train/validation/test strategy

A future dataset must be separated before preprocessing fitting or model training. Patient-level splitting is required when multiple observations can belong to one patient. Temporal splitting is required when the task predicts future outcomes or when random splitting would leak time. Stratification may be used for classification only after checking that it does not violate patient or temporal separation.

The split ratio must be justified from dataset size and task risk; it must not be chosen to produce a desired metric. A fixed documented random seed, dataset version/hash, preprocessing version, and split manifest are required.

## Leakage prevention

Target-derived fields, post-outcome events, future notes, duplicate patients, and evaluation-derived transformations must not enter training. Imputation, scaling, encoding, feature selection, and vocabulary construction must be fitted only on the training partition and then applied unchanged to validation/test data.

## Candidate metrics

| Future task | Planned metrics | Additional safety analysis |
|---|---|---|
| Binary/multiclass symptom or disease classification | Accuracy only as context; precision, recall, F1, confusion matrix; ROC-AUC where appropriate | Sensitivity, specificity, calibration, abstention rate, subgroup performance |
| Risk estimation | ROC-AUC/PR-AUC where justified, sensitivity, specificity, calibration curve/Brier-style measure if appropriate | Threshold harm analysis, temporal validation, subgroup and missingness analysis |
| Report extraction | Field-level precision/recall/F1 or agreement appropriate to annotation type | Error review for clinically important fields, provenance and abstention |
| Medicine/interaction lookup | Retrieval precision/recall, evidence coverage, severity-stratified recall | False-negative review, source freshness, citation completeness |
| Recommendations | No metric selected until recommendation policy and labels exist | Clinician review, unsafe-advice rate, escalation/abstention |

## Results policy

No Phase 13 model is trained or evaluated. Every future metric is marked **NOT YET EVALUATED** until measured on an approved held-out test set. No metric, prediction, confidence, or clinical outcome is fabricated.

## Evaluation governance

A future evaluation must include dataset provenance, label-quality review, missingness, imbalance, subgroup/fairness analysis, confidence/calibration interpretation, failure modes, human-review requirements, and limitations. Metrics alone do not establish clinical validity or production readiness.


## Phase 16 task-specific addendum

**Task:** Binary classification of the UCI Heart Disease source label  
**Primary algorithm:** Logistic Regression  
**Status:** **SPECIFIED / NOT YET EVALUATED**

Use a reproducible stratified 80/20 holdout for final evaluation and fixed stratified cross-validation inside the training partition for model/baseline decisions. Freeze the random seed, fold count, feature order, preprocessing, and threshold policy before the final test is opened. Fit imputation, encoding, scaling, and any learned transformation inside training folds only.

Evaluate a majority-class baseline and report balanced accuracy, accuracy, precision, recall/sensitivity, specificity, F1, ROC-AUC, PR-AUC, confusion matrix, and calibration review where supported. Report class distribution, invalid/missing target values, missingness, duplicates, exclusions, data version/hash, preprocessing version, and subgroup performance only where sample sizes justify it. No metric or prediction exists from Phase 16.


## Phase 17 actual-results addendum

The approved protocol was executed with random seed 42, a stratified 80/20 holdout (242 training / 61 test records), and five-fold stratified cross-validation on the training partition. The test set was not used to fit preprocessing.

Actual Logistic Regression test results were: accuracy 0.8852459016, balanced accuracy 0.8885281385, precision 0.8387096774, recall 0.9285714286, specificity 0.8484848485, F1 0.8813559322, ROC-AUC 0.9664502165, PR-AUC 0.9634351641, and Brier score 0.0797434423. The confusion matrix was `[[28, 5], [2, 26]]` in label order absent/present. Actual baseline and alternative-model results are recorded in `ai/evaluation/phase17_metrics.json`.

These are selected-test-set academic results and do not establish clinical validity, generalization, diagnostic performance, or production readiness.
