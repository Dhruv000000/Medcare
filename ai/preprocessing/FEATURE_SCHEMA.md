# MediCare AI Feature Schema — Phase 13

**Status:** **BLOCKED**; no final feature schema is approved because no first AI capability or target variable has been selected.

## Schema governance

A feature may be used only when it is necessary for one approved task, available from an approved dataset/source, typed and validated, privacy-reviewed, and covered by a documented missing-value and leakage policy. Names, email addresses, phone numbers, addresses, license IDs, and other direct identifiers are excluded by default.

## Candidate source fields requiring task approval

| Candidate feature | Source | Type/constraints | Default status |
|---|---|---|---|
| Structured symptom identifier | Not currently modeled | Controlled categorical value; task-specific | Missing from current schema |
| Symptom onset/duration/severity | Not currently modeled | Typed temporal/numeric values with defined ranges | Missing from current schema |
| Medical record type/date | `MedicalRecord.record_type`, `occurred_on` | Existing choices/date | Not approved as a predictive feature |
| Report type/status | `MedicalReport.report_type`, `status` | Existing choices | Not approved as a predictive feature |
| Report finding value | `ReportFinding.value` | String with units/reference range not currently modeled | Not approved; requires standardization |
| Prescription status/date | `Prescription.status`, `issued_on`, dates | Existing choices/dates | Not approved as a predictive feature |
| Normalized medicine identifier | Not currently modeled | Controlled identifier from approved vocabulary | Missing from current schema |
| Age/sex/blood group | `User`/`PatientProfile` | Sensitive demographic/clinical attributes | Excluded by default; fairness review required |

## Future schema requirements

The selected task must define feature name, semantic meaning, source, type, allowed values/range/units, requiredness, missing-value behavior, sensitivity, preprocessing, label leakage risk, and retention. Features derived from future records, labels, post-outcome events, or protected attributes require explicit review.

No feature is sent to a model in Phase 13, and no real patient record is used for schema experimentation.


## Phase 16 final feature addendum

**Capability:** Academic disease-risk classification  
**Dataset:** UCI Heart Disease, UCI ID 45  
**Status:** **SPECIFIED / PHASE 17 RECHECK REQUIRED**

The approved future feature allow-list is: `age`, `sex`, `cp`, `trestbps`, `chol`, `fbs`, `restecg`, `thalach`, `exang`, `oldpeak`, `slope`, `ca`, and `thal`. The target is not a feature: `disease_label_present` is derived from source `num` with `0 -> 0` and `1..4 -> 1`.

Numeric features require finite-value and plausible-range validation, training-only median imputation, and training-only scaling. Categorical features require explicit source-code validation, training-only category fitting, one-hot encoding, and an explicit unknown-category policy. Source missingness, especially in `ca` and `thal`, must be profiled and handled only under the frozen Phase 17 protocol. Identifier columns, names, social-security numbers, MediCare IDs, and operational Django clinical fields are prohibited.

See `ai/preprocessing/PHASE17_FEATURE_SCHEMA.md` and `docs/PHASE16_AI_SPECIFICATION.md` for the complete table and leakage controls.
