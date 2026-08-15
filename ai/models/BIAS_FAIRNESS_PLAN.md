# MediCare AI Bias and Fairness Plan — Phase 13

**Status:** Specification only; no fairness metric is measured.

## Potential bias sources

| Risk | How it could arise | Required control before training |
|---|---|---|
| Dataset imbalance | Rare outcomes or underrepresented symptom/interaction classes | Measure class distribution; predeclare resampling/weighting without test-label leakage |
| Representation gaps | Dataset population does not represent intended MediCare users | Compare dataset population, setting, age ranges, language, sex/gender where relevant, and care context; document non-generalizability |
| Demographic bias | Sensitive attributes correlate with labels or access patterns | Exclude protected attributes by default; conduct fairness review if clinically justified; never use them without documented purpose |
| Label bias | Labels reflect inconsistent clinician judgment, access, or historical practice | Define label generation, annotation guidance, agreement review, and disagreement handling |
| Measurement bias | Different groups have different documentation, testing, or recording quality | Assess missingness and measurement processes by subgroup; avoid treating missingness as disease without justification |
| Distribution shift | Data source, population, workflow, or clinical practice changes | Temporal validation, drift monitoring, retraining/retirement policy, and abstention when out of scope |
| Proxy leakage | Identifiers or workflow fields encode access, provider, location, or protected characteristics | Feature review, direct-identifier exclusion, proxy analysis, and leakage tests |

## Future analysis

A future approved dataset must define relevant subgroups before model fitting and report subgroup sample sizes, performance, calibration, missingness, error types, and confidence intervals where justified. No fairness threshold is invented in Phase 13. A model must not be exposed if an observed disparity has not been investigated and reviewed.

## Clinical fairness boundary

Fairness analysis does not override clinical validity or privacy. Sensitive attributes must not be collected or used merely to improve a metric. Any use requires a documented legitimate purpose, access restriction, privacy review, and clinician/data-governance approval.


## Phase 16 task-specific addendum

The UCI Heart Disease dataset is a small historical cohort and must not be treated as representative of MediCare users. Phase 17 must record source population/context as documented by UCI, class balance, age and sex distributions, missingness patterns, and duplicate policy before fitting.

`sex` is a source feature and a possible subgroup-analysis dimension. Subgroup reporting requires predeclared minimum sample-size rules, privacy review, and uncertainty-aware interpretation. If subgroup sizes are too small, report that analysis is not reliable rather than publishing unstable estimates. The model must not be advertised as validated for any population outside the source cohort.

Potential risks include historical sampling bias, label bias, sex representation imbalance, measurement differences, missingness in `ca`/`thal`, and distribution shift. No fairness metric or disparity result is claimed in Phase 16.


## Phase 17 actual subgroup addendum

A descriptive analysis was performed on the source-coded binary `sex` feature using the same fixed 61-record test set and seed 42. Source value 0 had 20 test records and source value 1 had 41 test records. The recorded results are in `ai/evaluation/phase17_subgroup_analysis.json`.

| Source-coded sex value | Test n | Positive labels | Accuracy | Balanced accuracy | Recall | Specificity | ROC-AUC |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 20 | 7 | 0.950000 | 0.928571 | 0.857143 | 1.000000 | 1.000000 |
| 1 | 41 | 21 | 0.853659 | 0.851190 | 0.952381 | 0.750000 | 0.954762 |

These are descriptive results from a small historical source subset, not fairness certification, clinical validation, or evidence that the model is unbiased. The unequal sample sizes, limited demographic representation, and source-specific sampling prevent reliable fairness conclusions. No additional demographic categories were invented.
