# Phase 17 Feature Schema

**Dataset:** UCI Heart Disease, UCI ID 45  
**Feature count:** 13  
**Target:** Derived `disease_label_present` from source `num`  
**Training status:** Not performed in Phase 16

| Order | Name | Source meaning | Type | Validation | Preprocessing |
|---:|---|---|---|---|---|
| 1 | `age` | Age in years | Numeric | Positive plausible range | Training-only median imputation; scaling |
| 2 | `sex` | Source-coded sex value | Binary/categorical | Explicit source code set | Explicit mapping; subgroup review |
| 3 | `cp` | Chest-pain type | Categorical | Source codes 1–4 | One-hot encoding |
| 4 | `trestbps` | Resting blood pressure | Numeric | Positive plausible range | Training-only median imputation; scaling |
| 5 | `chol` | Serum cholesterol | Numeric | Positive plausible range | Training-only median imputation; scaling |
| 6 | `fbs` | Fasting blood sugar indicator | Binary/categorical | Source code set | Explicit mapping |
| 7 | `restecg` | Resting ECG result | Categorical | Source code set | One-hot encoding |
| 8 | `thalach` | Maximum heart rate achieved | Numeric | Positive plausible range | Training-only median imputation; scaling |
| 9 | `exang` | Exercise-induced angina indicator | Binary/categorical | Source code set | Explicit mapping |
| 10 | `oldpeak` | ST depression relative to rest | Numeric | Finite numeric; source range review | Training-only median imputation; scaling |
| 11 | `slope` | Peak exercise ST-segment slope | Categorical | Source codes 1–3 | One-hot encoding |
| 12 | `ca` | Number of major vessels | Categorical/ordinal | 0–3; source missing values reviewed | Training-only imputation; explicit unknown policy |
| 13 | `thal` | Source-coded thalassemia result | Categorical | Source code set; missing values reviewed | Training-only imputation; one-hot encoding |

## Target transformation

```text
num == 0       -> disease_label_present = 0
num in 1..4    -> disease_label_present = 1
other/missing  -> invalid target; report and exclude under the frozen protocol
```

The target is a source dataset label and must never be called a diagnosis. Identifier columns, if present in a downloaded file, must be removed before the train/test split and must not be used for imputation, encoding, scaling, or feature selection.

## Data-contract rules

The implementation must reject missing required columns, unknown feature columns, invalid categorical codes, non-finite numeric values, and unsupported target values. It must log row counts at each validation stage, preserve the original source file separately from transformed data, and fit all learned preprocessing parameters on training folds only.
