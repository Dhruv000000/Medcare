# MediCare AI Dataset Specification — Phase 13

**Dataset status:** **NOT AVAILABLE**  
**Decision:** **APPROVED DATASET NOT AVAILABLE**

## Required dataset decision

No dataset in the current repository is approved or suitable for model training. No random public dataset, Kaggle dataset, scraped medical content, online medical record, or real MediCare patient data may be substituted.

A future dataset cannot be approved merely because it is downloadable. It must be reviewed for source, provenance, license, target validity, feature schema, data quality, privacy status, authorization, representativeness, and compatibility with one explicitly approved AI task.

## Minimum required dataset contract

| Requirement | Specification |
|---|---|
| Dataset type | Task-specific, versioned, patient-safe tabular/text/retrieval corpus chosen after capability approval |
| Source | Named source with documented provenance, collection method, time period, population, and data dictionary |
| License | Written license permitting the proposed academic training/evaluation use and redistribution/retention behavior |
| Features | Only the minimum fields needed by the selected task, with types, allowed values/ranges, missingness, units, and privacy classification |
| Target | Explicit label/output definition, allowed values, label-generation process, source, timestamp logic, and label-quality review |
| Data quality | Completeness, duplicates, outliers, inconsistent units, missingness, annotation agreement, and temporal validity reviewed |
| Privacy | No real patient data in the repository; de-identification/consent and access controls documented before use |
| Split | Patient-level or temporal split where appropriate; training/validation/test separation documented before fitting |
| Leakage control | Target-derived fields, future information, duplicate patients, and evaluation-derived transformations excluded from training |
| Imbalance | Class distribution measured; mitigation predeclared without using test labels |
| Reproducibility | Dataset version/hash, preprocessing version, random seed, environment, and configuration recorded |
| Approval | Owner/clinical/privacy approval recorded before training or external processing |

## Candidate task-specific schema

No candidate schema is approved. A future selection must define one of the following without combining unrelated tasks:

| Candidate | Minimum additional schema required |
|---|---|
| Symptom analysis | Structured symptom identifier, onset/duration/severity/context, explicit label or bounded educational policy, and escalation/abstention policy |
| Disease-risk prediction | Cohort definition, time-indexed features, outcome label, observation window, prediction horizon, and clinically reviewed label source |
| Report analysis | Standardized report fields, units/reference ranges, annotation schema, provenance, and permitted text/attachment handling |
| Medicine information | Normalized medicine identifiers and licensed authoritative reference corpus |
| Drug interaction | Normalized medication identifiers, dose/context requirements, authoritative interaction source, severity labels, and update process |
| Health recommendations | Clinician-reviewed content/policy, consented context, intended population, and escalation rules |

## Dataset availability audit

Repository inspection found no candidate dataset file, training artifact, dataset version, target definition, license record, or authorization. The current Django clinical tables are operational application data and are not an approved training dataset.

**Approved dataset unavailable.** The next model phase cannot train until the dataset contract and approval record exist.


## Phase 16 dataset decision addendum

**Phase 16 recommendation:** **UCI Heart Disease, UCI ID 45**  
**Official source:** https://archive.ics.uci.edu/dataset/45/heart+disease  
**DOI:** `10.24432/C52P4X`  
**License stated by official UCI page:** Creative Commons Attribution 4.0 International (CC BY 4.0)  
**Repository facts:** 303 instances, 13 commonly used features, binary classification convention derived from `num`, and missing values documented by the official page.

This addendum resolves the Phase 13–15 *candidate-selection* blocker by identifying one legitimate, task-compatible public source and an implementation-ready feature/target contract. It does not mean that the data has been downloaded, that project-owner training authorization has been granted, or that the dataset is present in the repository. Phase 17 must reverify the source and license, obtain explicit authorization, record the exact file/hash/version, inspect missingness and duplicates, and preserve UCI attribution before any retrieval or training.

The selected future target is `disease_label_present`: source `num=0` maps to 0, source `num=1..4` maps to 1, and all other/missing values are invalid. The selected feature allow-list is `age`, `sex`, `cp`, `trestbps`, `chol`, `fbs`, `restecg`, `thalach`, `exang`, `oldpeak`, `slope`, `ca`, and `thal`. No names, social-security numbers, MediCare identifiers, or operational clinical-table fields are permitted.

**Phase 16 status:** **SPECIFIED / PHASE 17 RECHECK REQUIRED**. The prior “not available” record remains historically accurate for Phases 12–15; this Phase 16 addendum is the new recommendation and must not be interpreted as a downloaded or trained dataset.


## Phase 17 implementation addendum

**Acquisition status:** Acquired from the official UCI archive.  
**Selected raw file:** `processed.cleveland.data` from the official UCI Heart Disease archive.  
**Archive SHA-256:** `b17cd273da9ce1caa4710fce80227ea454d4dbf9fcbc8e6a9121672751563adc`  
**Actual records:** 303.  
**Actual raw columns:** 14, consisting of 13 features plus `num`.  
**Exact duplicates:** 0.

Actual missingness was 4 values in `ca` and 2 values in `thal`; all other selected columns, including `num`, had zero missing values. The observed original target values were 0, 1, 2, 3, and 4. The normalized target distribution was 164 rows with label 0 and 139 rows with label 1. No invalid categorical or target values were observed under the Phase 16 contract.

The processed public dataset is stored at `ai/data/processed/uci_heart_disease_cleveland_processed.csv`, with the inspection manifest at `ai/data/processed/phase17_dataset_inspection.json`. Missing values remain represented as missing in the processed CSV and are imputed only inside the training-fitted pipeline. No MediCare patient data or PostgreSQL data was accessed.

**Phase 17 status:** **ACQUIRED / VERIFIED / USED FOR ACADEMIC TRAINING ONLY**. The dataset remains subject to CC BY 4.0 attribution and the model remains non-clinical and non-production.
