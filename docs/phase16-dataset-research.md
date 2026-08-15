# Phase 16 Dataset Research Notes

## Official sources consulted

The official UCI Machine Learning Repository pages were consulted without downloading any dataset:

1. [UCI Heart Disease](https://archive.ics.uci.edu/dataset/45/heart+disease)
2. [UCI Heart Failure Clinical Records](https://archive.ics.uci.edu/dataset/519/heart+failure+clinical+records)
3. [UCI CDC Diabetes Health Indicators](https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators)

## UCI Heart Disease

The official page describes a health-and-medicine multivariate classification dataset with 303 instances and 13 features, categorical/integer/real feature types, and missing values. The documented `num` attribute is the diagnosis-of-heart-disease field, with values 0 through 4; published experiments commonly reduce it to absence (`0`) versus presence (`1–4`). The page lists the 13 commonly used features: age, sex, chest-pain type, resting blood pressure, serum cholesterol, fasting blood sugar indicator, resting ECG result, maximum heart rate, exercise-induced angina, ST depression, ST-segment slope, number of major vessels, and thalassemia result. The page states that names and social-security numbers were removed or replaced with dummy values. The official page states a Creative Commons Attribution 4.0 International (CC BY 4.0) license and provides the DOI `10.24432/C52P4X`.

## UCI Heart Failure Clinical Records

The official page describes a health-and-medicine classification/regression/clustering dataset with 299 instances and 12 features plus a death-event target, no missing values, and numeric/binary fields including age, anaemia, CPK, diabetes, ejection fraction, high blood pressure, platelets, sex, serum creatinine, serum sodium, smoking, and follow-up time. It is licensed CC BY 4.0 and has DOI `10.24432/C5Z89R`. Its target and cohort are specific to survival among patients with heart failure, which is a narrower and more clinically loaded problem than the current MediCare SRS’s general disease-risk/symptom-analysis direction.

## UCI CDC Diabetes Health Indicators

The official page describes a large survey-based classification dataset with 253,680 instances and a diabetes target with classes corresponding to diabetes, pre-diabetes, or healthy. It includes demographic, lifestyle, health-history, and survey fields and notes sensitive information such as gender, income, and education. The UCI page points to an external linked dataset for licensing rather than stating a license directly on the page. Because the license/authorization terms require separate verification, it is not selected for Phase 17.

## Phase 16 decision implication

UCI Heart Disease is the strongest documented candidate for a future academic, non-autonomous MediCare disease-risk classification capability because its classification target, compact feature schema, official provenance, and CC BY 4.0 terms are directly documented by the official repository. This is a planning decision only. No data was downloaded, trained, fitted, or copied into MediCare.
