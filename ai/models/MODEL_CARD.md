# MediCare Academic Model Card

**Model status:** **TRAINED / ACADEMIC DEVELOPMENT MODEL**  
**Model version:** `uci-heart-disease-logreg-v1.0.0`  
**Artifact:** `ai/models/artifacts/uci-heart-disease-logreg-v1.0.0.joblib`  
**Artifact SHA-256:** `e548527e51c67a7b611501acc844b367cecdde53413e33914ed9757fb9bae6cd`

> **THIS IS AN ACADEMIC MODEL AND NOT A CLINICALLY VALIDATED DIAGNOSTIC SYSTEM.**

## Intended use

This model classifies the normalized label of the official UCI Heart Disease Cleveland subset for an offline academic demonstration. It is intended for developers, researchers, and authorized academic reviewers evaluating a reproducible tabular classification pipeline.

The output is a model-estimated classification based on the provided public-dataset features. It is not a diagnosis, prognosis, treatment recommendation, emergency decision, patient-specific clinical risk assessment, or replacement for a physician.

## Prohibited use

The model must not be used with MediCare patient data or PostgreSQL data, exposed to patients or clinicians through the current application, used to prescribe or change medication, modify records, triage emergencies, or make autonomous clinical decisions. No AI API or frontend integration was implemented in Phase 17.

## Dataset

The model was trained only on the official UCI Heart Disease dataset, UCI Repository ID 45, using the archive’s `processed.cleveland.data` file.

| Item | Value |
|---|---|
| Official source | https://archive.ics.uci.edu/dataset/45/heart+disease |
| Download archive | https://archive.ics.uci.edu/static/public/45/heart+disease.zip |
| DOI | `10.24432/C52P4X` |
| License | CC BY 4.0, as stated by UCI |
| Archive SHA-256 | `b17cd273da9ce1caa4710fce80227ea454d4dbf9fcbc8e6a9121672751563adc` |
| Records | 303 |
| Raw columns | 14: 13 features plus original `num` target |
| Exact duplicates | 0 |
| Missing values | `ca`: 4; `thal`: 2; all other selected columns: 0 |

No real MediCare patient data, personal medical information, user records, appointments, prescriptions, reports, or PostgreSQL data were used.

## Features and target

The model features are `age`, `sex`, `cp`, `trestbps`, `chol`, `fbs`, `restecg`, `thalach`, `exang`, `oldpeak`, `slope`, `ca`, and `thal`. The source target is `num`, with observed values 0, 1, 2, 3, and 4. The approved normalized target is `disease_label_present`: source `num=0` maps to 0; source `num=1..4` maps to 1.

The observed normalized class distribution was 164 label-absent rows and 139 label-present rows. This target is a public dataset label and must not be called a diagnosis.

## Preprocessing

The complete preprocessing/model pipeline is serialized in the artifact. Numeric features use training-fitted median imputation followed by `StandardScaler`. Categorical features use training-fitted most-frequent imputation followed by `OneHotEncoder(handle_unknown="ignore", sparse_output=False)`. The target transformation and all preprocessing are defined in `ai/phase17_training.py`; preprocessing is fitted inside the training pipeline and not on the complete dataset before splitting.

## Training and evaluation protocol

The fixed random seed was 42. A stratified 80/20 holdout produced 242 training records and 61 test records. Five-fold stratified cross-validation was performed on the training partition for model comparison. The final test partition was not used to fit preprocessing or select hyperparameters.

### Primary algorithm configuration

Logistic Regression used `solver="lbfgs"`, `max_iter=2000`, `random_state=42`, and `class_weight=None`. No uncontrolled hyperparameter search was performed.

### Baseline and alternatives

The baseline was `DummyClassifier(strategy="most_frequent")`. The documented alternatives were evaluated on the same split and under the same pipeline/evaluation procedure: `DecisionTreeClassifier(max_depth=4, min_samples_leaf=5, random_state=42)` and `RandomForestClassifier(n_estimators=200, max_depth=5, min_samples_leaf=2, random_state=42, n_jobs=1)`.

## Actual held-out test results

The following values are actual results from the 61-row stratified test set.

| Model | Accuracy | Balanced accuracy | Precision | Recall/sensitivity | Specificity | F1 | ROC-AUC | PR-AUC | Brier score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Majority baseline | 0.540984 | 0.500000 | 0.000000 | 0.000000 | 1.000000 | 0.000000 | 0.500000 | 0.459016 | 0.459016 |
| Logistic Regression | 0.885246 | 0.888528 | 0.838710 | 0.928571 | 0.848485 | 0.881356 | 0.966450 | 0.963435 | 0.079743 |
| Decision Tree | 0.770492 | 0.774351 | 0.718750 | 0.821429 | 0.727273 | 0.766667 | 0.872835 | 0.826708 | 0.146604 |
| Random Forest | 0.868852 | 0.870671 | 0.833333 | 0.892857 | 0.848485 | 0.862069 | 0.951299 | 0.941573 | 0.102953 |

The Logistic Regression result is a selected-test-set result under this protocol. It is not clinical validation and must not be described as diagnostic accuracy.

### Logistic Regression confusion matrix

Rows are actual labels and columns are predicted labels, ordered as label absent then label present:

| | Predicted absent | Predicted present |
|---|---:|---:|
| Actual absent | 28 | 5 |
| Actual present | 2 | 26 |

Thus, the test set contained 28 true negatives, 5 false positives, 2 false negatives, and 26 true positives. These are dataset-label errors, not clinical outcomes.

### Training-partition cross-validation summary

| Model | ROC-AUC mean ± SD | Balanced accuracy mean ± SD | F1 mean ± SD | PR-AUC mean ± SD |
|---|---:|---:|---:|---:|
| Majority baseline | 0.500000 ± 0.000000 | 0.500000 ± 0.000000 | 0.000000 ± 0.000000 | 0.458673 ± 0.006467 |
| Logistic Regression | 0.902493 ± 0.014440 | 0.841842 ± 0.006855 | 0.824501 ± 0.006867 | 0.899196 ± 0.021170 |
| Decision Tree | 0.813460 ± 0.052399 | 0.739964 ± 0.036405 | 0.713545 ± 0.047604 | 0.798654 ± 0.021490 |
| Random Forest | 0.895401 ± 0.030754 | 0.801729 ± 0.039598 | 0.780001 ± 0.049783 | 0.897741 ± 0.032306 |

## Explainability

The Logistic Regression pipeline’s signed coefficients are recorded in `ai/evaluation/logistic_coefficients.csv`. They describe the model’s statistical associations after encoding and scaling. They do not establish causation, medical reasoning, or treatment relevance. The model output must be accompanied by the academic/non-diagnostic disclaimer.

The saved evaluation assets include `logistic_confusion_matrix.png` and `logistic_calibration.png`. Calibration is provided for review only; no confidence value is exposed through an API because no API exists in this phase.

## Bias and fairness

The source dataset is small and historical. The observed source includes a binary `sex` feature, but subgroup conclusions are not treated as reliable without adequate subgroup sample sizes and uncertainty analysis. No claim is made that the model is unbiased or representative of MediCare users. Potential risks include sampling bias, sex representation imbalance, label bias, measurement differences, missingness patterns, and distribution shift.

## Limitations and safety

The model is not clinically validated, externally validated, calibrated for clinical use, or approved for patient care. The dataset is not representative of the MediCare population. The target is an angiographic dataset label transformed from 0 versus 1–4, not a clinical diagnosis. The test set is small, so metrics are uncertain and may vary under other splits or populations.

The model remains offline and development-only. It is not connected to Django, the Patient AI Insights page, the Admin module, any clinical workflow, any API, or PostgreSQL. No patient-facing prediction is available. Future use requires a separate safety, privacy, clinical, security, and integration review.

## Reproducibility

Training is reproduced by running `python3 ai/phase17_training.py` after the pinned dependencies in `ai/requirements-phase17.txt` are installed. Dataset inspection is reproduced by running `python3 ai/scripts_inspect_dataset.py` after acquiring the official archive. The script records the source, archive hash, schema, target transformation, seed, split, CV folds, algorithm settings, package versions, metrics, and artifact hash.

## Version history

| Version | Status | Notes |
|---|---|---|
| Pending | Historical blocked record | Phases 11–15 had no selected task/dataset/algorithm |
| `uci-heart-disease-logreg-v1.0.0` | **Trained academic/development model** | Phase 17 artifact created and evaluated; not clinically validated; no API/frontend integration |

## Attribution

UCI Machine Learning Repository, Heart Disease dataset, ID 45, DOI `10.24432/C52P4X`, licensed CC BY 4.0. Any redistribution or adaptation must preserve the required attribution, license notice, source link, and modification notice where applicable.
