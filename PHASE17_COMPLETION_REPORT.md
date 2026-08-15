# MediCare Phase 17 Completion Report

**Author:** Manus AI  
**Phase:** 17 — AI Dataset Acquisition, Preprocessing, Model Training & Evaluation  
**Project:** MediCare — Intelligent Clinical Decision Support System  

> **PHASE 17 STATUS: COMPLETE — TRAINED ACADEMIC/DEVELOPMENT MODEL**

Phase 17 was executed using only the approved UCI Heart Disease dataset. The model was trained and evaluated locally. The existing MediCare frontend, backend, database models, migrations, authentication, Admin module, and API routing were preserved. No real MediCare patient data or PostgreSQL data was accessed.

## 1. AI capability

The implemented capability is **academic disease-risk classification**, strictly bounded to classification of the public UCI dataset label. It is not a diagnosis, prognosis, medical risk assessment for MediCare users, treatment recommendation, or clinical decision-maker.

The trained model returns a binary classification of the normalized public-dataset target: `label_absent` versus `label_present`. It must be described as **model-estimated classification based on the provided features** and not as medical certainty.

## 2. Dataset source and license

The dataset was acquired from the official [UCI Heart Disease dataset page][1] and the official archive URL [2]. The project used only the archive’s `processed.cleveland.data` file.

| Item | Actual value |
|---|---|
| Dataset | UCI Heart Disease |
| UCI ID | 45 |
| Official source | https://archive.ics.uci.edu/dataset/45/heart+disease |
| Official archive | https://archive.ics.uci.edu/static/public/45/heart+disease.zip |
| DOI | `10.24432/C52P4X` |
| License | CC BY 4.0, as stated by UCI |
| Archive SHA-256 | `b17cd273da9ce1caa4710fce80227ea454d4dbf9fcbc8e6a9121672751563adc` |
| Attribution | UCI Machine Learning Repository, dataset name/ID/DOI/source URL, CC BY 4.0 notice, and modification notice where applicable |

The raw archive and selected source documentation are stored under `ai/data/raw/`. The processed data and inspection manifest are stored under `ai/data/processed/`. No mirror, GitHub copy, Kaggle copy, or substitute dataset was used.

## 3. Dataset acquisition and inspection

The official archive was downloaded and its SHA-256 checksum was recorded before extraction. The archive was inspected for identity, documentation, structure, and the selected Cleveland file. Non-selected database files from the archive were not retained as training data; the original archive remains the provenance record.

The inspection script `ai/scripts_inspect_dataset.py` read the official Cleveland file without silently dropping rows, normalized missing-value tokens to missing values in the processed representation, validated the schema and target, and wrote `ai/data/processed/phase17_dataset_inspection.json`.

### Actual dataset statistics

| Statistic | Actual result |
|---|---:|
| Records | 303 |
| Raw columns | 14 |
| Model features | 13 |
| Exact duplicate rows | 0 |
| Missing `ca` values | 4 |
| Missing `thal` values | 2 |
| Missing target values | 0 |
| Invalid categorical values | 0 observed |
| Invalid target values | 0 observed |
| Original target values | 0, 1, 2, 3, 4 |
| Normalized label-absent rows | 164 |
| Normalized label-present rows | 139 |

The source documentation in `heart-disease.names` states that the selected attributes include the 13 approved feature fields and `num` as the predicted attribute. The selected file contains no identifier column. No names, addresses, emails, phone numbers, MediCare IDs, medical-record IDs, or operational application fields were used.

## 4. Feature schema

The model used exactly the Phase 16 feature allow-list:

`age`, `sex`, `cp`, `trestbps`, `chol`, `fbs`, `restecg`, `thalach`, `exang`, `oldpeak`, `slope`, `ca`, and `thal`.

| Feature | Type/handling | Included |
|---|---|---|
| `age` | Numeric; median imputation and scaling inside training pipeline | Yes |
| `sex` | Source-coded categorical/binary; explicit category handling | Yes |
| `cp` | Source-coded categorical; one-hot encoding | Yes |
| `trestbps` | Numeric; median imputation and scaling | Yes |
| `chol` | Numeric; median imputation and scaling | Yes |
| `fbs` | Source-coded categorical/binary; explicit category handling | Yes |
| `restecg` | Source-coded categorical; one-hot encoding | Yes |
| `thalach` | Numeric; median imputation and scaling | Yes |
| `exang` | Source-coded categorical/binary; explicit category handling | Yes |
| `oldpeak` | Numeric; median imputation and scaling | Yes |
| `slope` | Source-coded categorical; one-hot encoding | Yes |
| `ca` | Source-coded categorical/ordinal; 4 source values missing and imputed inside pipeline | Yes |
| `thal` | Source-coded categorical; 2 source values missing and imputed inside pipeline | Yes |

No additional features were introduced. The original `num` column was retained only for provenance and target validation; it was not included in the feature matrix.

## 5. Target definition

The original target column was `num`. The actual downloaded file contained values 0, 1, 2, 3, and 4, with no missing or invalid target values.

The approved Phase 16 transformation was applied exactly:

```text
num == 0       -> disease_label_present = 0 (dataset label absent)
num in 1..4    -> disease_label_present = 1 (dataset label present)
other/missing  -> invalid; reject
```

The normalized target distribution was 164 rows with label 0 and 139 rows with label 1. This is a public dataset label, not a clinical diagnosis.

## 6. Data cleaning

No exact duplicate rows were removed because the inspection found zero exact duplicates. Missing values were not imputed before splitting. The processed CSV preserves missing values; the training pipeline fits numeric median imputation and categorical most-frequent imputation only on the training partition/folds.

Categorical code sets were validated against the Phase 16 contract. No invalid categorical values were observed. Numeric fields were converted deterministically and inspected for the documented invalid conditions. No records were deleted for performance manipulation.

## 7. Preprocessing pipeline

The trained artifact contains the complete preprocessing and Logistic Regression pipeline:

| Feature group | Pipeline steps |
|---|---|
| Numeric: `age`, `trestbps`, `chol`, `thalach`, `oldpeak` | `SimpleImputer(strategy="median")` followed by `StandardScaler()` |
| Categorical: `sex`, `cp`, `fbs`, `restecg`, `exang`, `slope`, `ca`, `thal` | `SimpleImputer(strategy="most_frequent")` followed by `OneHotEncoder(handle_unknown="ignore", sparse_output=False)` |

All learned preprocessing steps were fitted inside the training pipeline. No full-dataset scaler, encoder, imputation statistic, or target-derived feature was used.

## 8. Train/test split and evaluation strategy

The fixed random seed was **42**. The split was a stratified 80/20 holdout:

| Partition | Records |
|---|---:|
| Training | 242 |
| Test | 61 |

Five-fold stratified cross-validation was performed inside the training partition for model comparison. The final test set was not used to fit preprocessing, select hyperparameters, or choose the algorithm. No repeated-patient identifier was available in the selected feature file, and no identifier was used as a feature.

## 9. Baseline

The approved baseline was `DummyClassifier(strategy="most_frequent")`. It was fit on the training partition and evaluated on the same 61-record test partition.

## 10. Logistic Regression configuration

The primary model was configured as follows:

| Parameter | Value |
|---|---|
| Algorithm | Logistic Regression |
| Solver | `lbfgs` |
| Maximum iterations | 2000 |
| Random state | 42 |
| Class weight | None; no reweighting applied |
| Model version | `uci-heart-disease-logreg-v1.0.0` |
| Python | 3.12.3 |
| NumPy | 2.5.2 |
| pandas | 3.0.5 |
| scikit-learn | 1.9.0 |
| joblib | 1.5.3 |
| matplotlib | 3.11.1 |

No uncontrolled hyperparameter search was performed.

## 11. Alternative-model comparison

The Phase 16-documented alternatives were evaluated using the same split and preprocessing/evaluation methodology.

| Alternative | Configuration |
|---|---|
| Decision Tree | `max_depth=4`, `min_samples_leaf=5`, `random_state=42` |
| Random Forest | `n_estimators=200`, `max_depth=5`, `min_samples_leaf=2`, `random_state=42`, `n_jobs=1` |

The alternatives were comparison models only. Logistic Regression remained the approved primary algorithm regardless of comparison performance.

## 12. Actual held-out metrics

The following values are actual results from the fixed 61-record test set. Values are shown to six decimal places for reproducibility.

| Model | Accuracy | Balanced accuracy | Precision | Recall/sensitivity | Specificity | F1 | ROC-AUC | PR-AUC | Brier score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Majority baseline | 0.540984 | 0.500000 | 0.000000 | 0.000000 | 1.000000 | 0.000000 | 0.500000 | 0.459016 | 0.459016 |
| Logistic Regression | 0.885246 | 0.888528 | 0.838710 | 0.928571 | 0.848485 | 0.881356 | 0.966450 | 0.963435 | 0.079743 |
| Decision Tree | 0.770492 | 0.774351 | 0.718750 | 0.821429 | 0.727273 | 0.766667 | 0.872835 | 0.826708 | 0.146604 |
| Random Forest | 0.868852 | 0.870671 | 0.833333 | 0.892857 | 0.848485 | 0.862069 | 0.951299 | 0.941573 | 0.102953 |

The primary model’s results are selected-test-set academic results. They do not establish clinical validity, diagnostic accuracy, generalization, or production readiness.

## 13. Confusion matrix

The Logistic Regression confusion matrix is ordered as rows = actual labels and columns = predicted labels, with label absent first and label present second:

| | Predicted absent | Predicted present |
|---|---:|---:|
| Actual absent | 28 | 5 |
| Actual present | 2 | 26 |

The test set therefore contains 28 true negatives, 5 false positives, 2 false negatives, and 26 true positives against the public dataset label. The rendered image is `ai/evaluation/logistic_confusion_matrix.png`.

## 14. Cross-validation results

Five-fold stratified cross-validation was performed on the 242-record training partition.

| Model | ROC-AUC mean ± SD | Balanced accuracy mean ± SD | F1 mean ± SD | PR-AUC mean ± SD |
|---|---:|---:|---:|---:|
| Majority baseline | 0.500000 ± 0.000000 | 0.500000 ± 0.000000 | 0.000000 ± 0.000000 | 0.458673 ± 0.006467 |
| Logistic Regression | 0.902493 ± 0.014440 | 0.841842 ± 0.006855 | 0.824501 ± 0.006867 | 0.899196 ± 0.021170 |
| Decision Tree | 0.813460 ± 0.052399 | 0.739964 ± 0.036405 | 0.713545 ± 0.047604 | 0.798654 ± 0.021490 |
| Random Forest | 0.895401 ± 0.030754 | 0.801729 ± 0.039598 | 0.780001 ± 0.049783 | 0.897741 ± 0.032306 |

## 15. Explainability

The artifact uses Logistic Regression, so the explanation output is a signed coefficient table in `ai/evaluation/logistic_coefficients.csv`. The largest absolute encoded-feature coefficients in the trained model were:

| Encoded feature | Coefficient | Odds-ratio representation |
|---|---:|---:|
| `categorical__ca_0.0` | -1.498641 | 0.223434 |
| `categorical__cp_4.0` | 1.030561 | 2.802637 |
| `categorical__thal_7.0` | 0.818491 | 2.267076 |
| `categorical__sex_0.0` | -0.700836 | 0.496170 |
| `categorical__sex_1.0` | 0.690353 | 1.994420 |

These values describe model associations after encoding and scaling. They do not mean that any feature causes disease, explains a patient medically, or justifies treatment. The calibration review is available at `ai/evaluation/logistic_calibration.png` and does not authorize exposing probabilities through an API.

## 16. Bias/fairness analysis

A descriptive source-coded `sex` subgroup analysis was performed on the same 61-record test set. Source value 0 had 20 test records and source value 1 had 41 test records.

| Source-coded sex | Test n | Positive labels | Accuracy | Balanced accuracy | Recall | Specificity | ROC-AUC |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 20 | 7 | 0.950000 | 0.928571 | 0.857143 | 1.000000 | 1.000000 |
| 1 | 41 | 21 | 0.853659 | 0.851190 | 0.952381 | 0.750000 | 0.954762 |

These are descriptive results from a small historical source subset. They do not support a fairness certification or an unbiasedness claim. The unequal subgroup sizes, limited demographic representation, and source-specific sampling prevent reliable fairness conclusions.

## 17. Model artifact

The complete preprocessing plus model pipeline is stored at:

`ai/models/artifacts/uci-heart-disease-logreg-v1.0.0.joblib`

| Artifact property | Value |
|---|---|
| Artifact type | scikit-learn pipeline bundle serialized with joblib |
| Model version | `uci-heart-disease-logreg-v1.0.0` |
| SHA-256 | `e548527e51c67a7b611501acc844b367cecdde53413e33914ed9757fb9bae6cd` |
| Checksum file | `ai/models/artifacts/uci-heart-disease-logreg-v1.0.0.joblib.sha256` |
| Pipeline contents | Feature schema, preprocessing pipeline, Logistic Regression, metadata |
| Loading validation | Passed using fixed artifact path and checksum verification |

No arbitrary user-controlled artifact path is accepted by the local evaluation script. The script validates the expected path, checksum, bundle keys, feature schema, and target schema before loading.

## 18. Model metadata and model card

The model metadata is stored at `ai/evaluation/phase17_metadata.json`. It contains model name/version, dataset and archive hash, source/license, feature list, target transform, preprocessing, algorithms, training configuration, actual metrics, cross-validation, package versions, safety status, and training timestamp.

The updated model card is `ai/models/MODEL_CARD.md`. It states:

> **THIS IS AN ACADEMIC MODEL AND NOT A CLINICALLY VALIDATED DIAGNOSTIC SYSTEM.**

It documents intended/prohibited use, dataset, features, target, algorithm, training/evaluation, explainability, limitations, bias/fairness, healthcare safety, reproducibility, attribution, and version history.

## 19. Training and evaluation scripts

| Script | Purpose |
|---|---|
| `ai/scripts_inspect_dataset.py` | Official-file inspection, validation, processed public dataset, and manifest |
| `ai/phase17_training.py` | Leakage-safe preprocessing, split, baseline, primary/alternative training, metrics, plots, coefficients, artifact, metadata |
| `ai/phase17_evaluate.py` | Fixed-path artifact checksum/schema validation and held-out evaluation |
| `ai/phase17_subgroup_analysis.py` | Fixed-protocol descriptive source-coded sex subgroup analysis |

The scripts do not import Django, connect to PostgreSQL, access MediCare models, query users/patients, call external services, or implement APIs.

## 20. Dependencies

Phase 17 added the dedicated manifest `ai/requirements-phase17.txt` with pinned local scientific dependencies: NumPy 2.5.2, pandas 3.0.5, scikit-learn 1.9.0, joblib 1.5.3, and matplotlib 3.11.1. The existing `backend/requirements.txt` was not changed because Django does not load the offline training pipeline in this phase.

## 21. Reproducibility

The source archive hash, selected raw-file checksums, processed manifest, feature order, target transformation, fixed seed, split, cross-validation folds, preprocessing configuration, model parameters, package versions, evaluation JSON, artifact checksum, and scripts are included in the project. A future rerun can reproduce the workflow from the official archive and pinned dependency manifest without MediCare data.

## 22. Security validation

The following checks passed:

| Security boundary | Result |
|---|---|
| Secrets/API keys/private keys | No secrets found in Phase 17 runtime files; test-only marker strings are assertions, not credentials |
| External AI providers | No OpenAI, Gemini, Claude, Hugging Face inference, cloud ML, or external prediction service used |
| Django/PostgreSQL access | No Django imports, database imports, patient queries, or PostgreSQL access in Phase 17 scripts |
| Real patient data | No MediCare data used; workflow reads only `ai/data` |
| Model loading | Fixed artifact path, checksum verification, schema validation, no `sys.argv` or arbitrary path input |
| AI endpoints | No `/api/ai/` or `/api/chat/` route exists |
| Dataset leakage | Only approved public UCI files are used; no operational application data enters the pipeline |

## 23. Test results and validation

| Validation | Actual result |
|---|---|
| Phase 17 model/data/evaluation/security tests | **9 passed**, 0 failed |
| Complete AI suite: foundation, Phase 12, Phase 15, Phase 16, Phase 17 | **34 passed**, 0 failed |
| Django/Admin/patient/doctor/appointment/clinical regression suite | **58 passed**, 0 failed |
| Combined AI + Django tests | **92 passed**, 0 failed |
| `manage.py check` | Passed: no issues, 0 silenced |
| `makemigrations --check --dry-run` | Passed: no changes detected |
| Python compilation | Passed for `ai` and `backend` |
| JavaScript syntax | Passed for all frontend JavaScript files with `node --check` |
| Frontend local references | Passed: 142 references checked, 0 broken references |
| Artifact loading/inference | Passed: checksum, schema, valid input, missing-value handling, prediction shape/type |
| Visualization review | Passed: confusion matrix and calibration assets visually inspected |

The test suite emitted non-failing dependency warnings: a scikit-learn undefined-precision warning for the expected majority baseline with no positive predictions and a joblib/NumPy deprecation warning during artifact loading. These warnings did not affect test success or fabricate any result.

## 24. Project integrity against Phase 16

The baseline was `/home/ubuntu/audit_project/medicare_phase16_completed.zip`. A normalized comparison excluded generated Python caches and local test databases.

| Area | Result |
|---|---|
| Frontend | **Unchanged**; no `diff -qr` differences |
| Backend application | **Unchanged**; no `diff -qr` differences after excluding generated files |
| Protected frontend/backend checksum | Identical: `89630fcc4c4e0e00c6f814bbf44704457c7414e35054f6fe031e32cafbf355fd` |
| Database models/migrations | Unchanged; migration check passed |
| API routing | Unchanged; no AI route added |

## 25. Files created

| File or directory | Purpose |
|---|---|
| `PHASE17_COMPLETION_REPORT.md` | This report |
| `ai/requirements-phase17.txt` | Pinned offline ML dependencies |
| `ai/data/README.md` | Dataset storage, source, attribution, and privacy boundary |
| `ai/data/raw/uci_heart_disease_45.zip` | Official UCI archive |
| `ai/data/raw/uci_heart_disease_45.zip.sha256` | Archive checksum |
| `ai/data/raw/uci_heart_disease_45/` | Selected official source files and documentation |
| `ai/data/processed/uci_heart_disease_cleveland_processed.csv` | Processed public dataset with normalized target |
| `ai/data/processed/phase17_dataset_inspection.json` | Actual inspection manifest |
| `ai/documentation/PHASE17_DATASET_CARD.md` | Dataset card |
| `ai/scripts_inspect_dataset.py` | Dataset inspection script |
| `ai/phase17_training.py` | Training/evaluation/artifact script |
| `ai/phase17_evaluate.py` | Fixed-path artifact evaluation script |
| `ai/phase17_subgroup_analysis.py` | Descriptive subgroup script |
| `ai/models/artifacts/uci-heart-disease-logreg-v1.0.0.joblib` | Trained pipeline artifact |
| `ai/models/artifacts/uci-heart-disease-logreg-v1.0.0.joblib.sha256` | Artifact checksum |
| `ai/evaluation/PHASE17_EVALUATION_REPORT.md` | Standalone evaluation report |
| `ai/evaluation/phase17_metrics.json` | Actual metrics and cross-validation results |
| `ai/evaluation/phase17_metadata.json` | Model metadata |
| `ai/evaluation/phase17_subgroup_analysis.json` | Actual descriptive subgroup results |
| `ai/evaluation/phase17_evaluation_validation.json` | Artifact reload validation |
| `ai/evaluation/logistic_coefficients.csv` | Actual coefficient associations |
| `ai/evaluation/logistic_confusion_matrix.png` | Actual confusion matrix image |
| `ai/evaluation/logistic_calibration.png` | Calibration-review image |
| `ai/evaluation/test_predictions.csv` | Held-out test predictions used for evaluation evidence |
| `ai/tests/test_phase17_model.py` | Phase 17 dataset/model/evaluation/security tests |
| `ai/documentation/phase17-*.log/json/md` | Training, evaluation, tests, validation, and visual evidence logs |

## 26. Files modified

| File | Modification |
|---|---|
| `ai/algorithms/ALGORITHM_SELECTION.md` | Added actual Phase 17 training/comparison status |
| `ai/datasets/DATASET_SPECIFICATION.md` | Added actual acquisition, inspection, and target results |
| `ai/models/BIAS_FAIRNESS_PLAN.md` | Added actual descriptive source-coded sex subgroup results and limitations |
| `ai/models/EVALUATION_PLAN.md` | Added actual held-out metrics and confusion matrix |
| `ai/models/MODEL_CARD.md` | Replaced pending card with actual academic model card and artifact hash |
| `ai/tests/test_phase15_blocked.py` | Scoped historical artifact gate to permit only explicitly approved Phase 17 outputs |
| `ai/tests/test_phase16_specification.py` | Scoped historical artifact gate to permit only explicitly approved Phase 17 outputs |
| `docs/AI_ROADMAP.md` | Marked Phase 17 complete and Phase 18 deferred |
| `docs/AI_SRS_TRACEABILITY.md` | Added Phase 17 implementation/evaluation traceability |

No frontend or backend application source file was modified.

## 27. Files deleted

No pre-existing project source, frontend, backend, database model, migration, authentication, Admin, or documentation file was deleted. Non-selected files extracted from the UCI archive were intentionally removed from the extracted raw directory after provenance inspection; the official archive remains preserved. No unrelated dataset was retained for training.

## 28. Important unchanged files

All `frontend/` pages, stylesheets, JavaScript, navigation, Patient AI Insights UI, Doctor pages, Admin pages, and assets were unchanged. All Django apps, serializers, permissions, views, URL configuration, models, migrations, authentication/CSRF implementation, Admin module, and `backend/requirements.txt` were unchanged. No AI endpoint was added.

## 29. Frontend impact

There was **no frontend impact**. No UI/UX, CSS, navigation, dashboard, Patient AI Insights, Doctor, or Admin page was modified. No model output appears in the frontend.

## 30. Database impact

There was **no database impact**. No model, migration, database configuration, PostgreSQL installation, Windows database access, or MediCare database query was performed.

## 31. API status

**No AI API was implemented.** The artifact is available only through local/offline scripts. Runtime API integration is deferred to Phase 18 and requires separate authorization and safety review.

## 32. PostgreSQL status

PostgreSQL was not installed in the sandbox. The user’s Windows PostgreSQL instance was not accessed. No claim is made that PostgreSQL was tested.

## 33. Known limitations

The dataset is small and historical, the target is a transformed public label, the test set contains only 61 rows, and the model has not undergone external or clinical validation. The source population may not represent MediCare users. The observed metrics may vary under another split or future data. The subgroup analysis is descriptive and not a fairness certification. Calibration was reviewed visually and through Brier score but does not authorize probability exposure or clinical use.

The artifact serialization depends on the pinned scientific environment. A joblib/NumPy deprecation warning was observed during loading, but the artifact loaded and validated successfully under the pinned environment.

## 34. Model status

| Field | Value |
|---|---|
| MODEL STATUS | **TRAINED** |
| MODEL VERSION | `uci-heart-disease-logreg-v1.0.0` |
| DATASET VERSION/SOURCE | UCI Heart Disease, UCI ID 45, official archive SHA-256 recorded above |
| ALGORITHM | Logistic Regression with complete preprocessing pipeline |
| STATUS CLASSIFICATION | Academic/development only; not clinically validated and not production-ready |

## 35. Recommended next phase

**Phase 18** may be considered only after explicit approval. It would address a separately reviewed runtime API and any integration decision. It must not be started automatically, must not assume patient-facing use, and must preserve the current no-diagnosis/no-autonomous-action safety boundary.

## 36. Strict stop condition

Phase 17 is complete. Phase 18 was not started. No AI API, Patient AI Insights integration, chatbot, RAG, LLM, external AI provider, deployment, or production ML infrastructure was implemented.

## References

[1]: https://archive.ics.uci.edu/dataset/45/heart+disease "UCI Heart Disease dataset"
[2]: https://archive.ics.uci.edu/static/public/45/heart+disease.zip "Official UCI Heart Disease archive"
[3]: https://creativecommons.org/licenses/by/4.0/legalcode "Creative Commons Attribution 4.0 International legal code"
