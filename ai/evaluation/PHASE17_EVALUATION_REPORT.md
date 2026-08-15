# Phase 17 Evaluation Report

**Task:** Academic binary classification of the UCI Heart Disease Cleveland dataset label  
**Primary model:** Logistic Regression  
**Model version:** `uci-heart-disease-logreg-v1.0.0`  
**Status:** Trained academic/development artifact; not clinically validated

## Dataset and split

The official UCI Heart Disease archive was acquired from [UCI dataset 45][1] under the CC BY 4.0 license stated by UCI. The selected `processed.cleveland.data` file contained 303 rows, 13 approved features plus original `num`, 0 exact duplicate rows, 4 missing `ca` values, 2 missing `thal` values, and no missing target values. The original target values were 0–4; the approved normalization produced 164 label-absent rows and 139 label-present rows.

A stratified 80/20 split with seed 42 produced 242 training rows and 61 test rows. Five-fold stratified cross-validation was performed only within the training partition. The preprocessing pipeline fitted imputation, encoding, and scaling within the training folds.

## Test-set metrics

The following metrics are actual results on the fixed 61-row test set.

| Model | Accuracy | Balanced accuracy | Precision | Recall | Specificity | F1 | ROC-AUC | PR-AUC | Brier |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Majority baseline | 0.540984 | 0.500000 | 0.000000 | 0.000000 | 1.000000 | 0.000000 | 0.500000 | 0.459016 | 0.459016 |
| Logistic Regression | 0.885246 | 0.888528 | 0.838710 | 0.928571 | 0.848485 | 0.881356 | 0.966450 | 0.963435 | 0.079743 |
| Decision Tree | 0.770492 | 0.774351 | 0.718750 | 0.821429 | 0.727273 | 0.766667 | 0.872835 | 0.826708 | 0.146604 |
| Random Forest | 0.868852 | 0.870671 | 0.833333 | 0.892857 | 0.848485 | 0.862069 | 0.951299 | 0.941573 | 0.102953 |

## Primary confusion matrix

Rows are actual labels and columns are predicted labels, ordered absent/present:

| | Predicted absent | Predicted present |
|---|---:|---:|
| Actual absent | 28 | 5 |
| Actual present | 2 | 26 |

The selected test set therefore contains 28 true negatives, 5 false positives, 2 false negatives, and 26 true positives. These are errors against the public dataset label and are not clinical outcomes.

## Training-partition cross-validation

| Model | ROC-AUC mean ± SD | Balanced accuracy mean ± SD | F1 mean ± SD | PR-AUC mean ± SD |
|---|---:|---:|---:|---:|
| Majority baseline | 0.500000 ± 0.000000 | 0.500000 ± 0.000000 | 0.000000 ± 0.000000 | 0.458673 ± 0.006467 |
| Logistic Regression | 0.902493 ± 0.014440 | 0.841842 ± 0.006855 | 0.824501 ± 0.006867 | 0.899196 ± 0.021170 |
| Decision Tree | 0.813460 ± 0.052399 | 0.739964 ± 0.036405 | 0.713545 ± 0.047604 | 0.798654 ± 0.021490 |
| Random Forest | 0.895401 ± 0.030754 | 0.801729 ± 0.039598 | 0.780001 ± 0.049783 | 0.897741 ± 0.032306 |

## Explainability and fairness

Signed Logistic Regression coefficients are available in `logistic_coefficients.csv`. They describe model associations after preprocessing and are not causal medical explanations. The confusion-matrix and calibration-review images are included alongside this report.

A descriptive source-coded `sex` subgroup analysis used the same test split. Source value 0 had 20 test rows, accuracy 0.950000, balanced accuracy 0.928571, recall 0.857143, specificity 1.000000, and ROC-AUC 1.000000. Source value 1 had 41 test rows, accuracy 0.853659, balanced accuracy 0.851190, recall 0.952381, specificity 0.750000, and ROC-AUC 0.954762. These small, source-specific results do not support fairness certification or an unbiasedness claim.

## Interpretation and limitations

Logistic Regression outperformed the majority baseline and the two comparison models on this selected test split. This is a description of this dataset and protocol, not a claim of clinical usefulness. The sample is small and historical; the source population may not represent MediCare users; the label is a transformed dataset label; and calibration, external validation, clinical validation, and prospective performance are not established.

The model is an offline academic artifact. It is not connected to Django, PostgreSQL, the Patient AI Insights page, the Admin module, or any API. It must not diagnose, prescribe, treat, triage, or replace a clinician.

## References

[1]: https://archive.ics.uci.edu/dataset/45/heart+disease "UCI Heart Disease dataset"
[2]: https://creativecommons.org/licenses/by/4.0/legalcode "Creative Commons Attribution 4.0 International legal code"
