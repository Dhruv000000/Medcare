# Requirements Before the Next AI Model Phase

Phase 13 outcome is **BLOCKED**. The next model phase must not begin until the following decisions are approved and recorded.

## Required approvals

| Decision | Required content |
|---|---|
| First capability | Choose exactly one candidate capability and explain why it is appropriate for MediCare and the academic scope |
| Problem definition | Task type, unit of prediction, intended user/use, prohibited use, input boundary, output/abstention behavior |
| Feature schema | Feature names, meanings, sources, types, units/ranges, requiredness, missingness, sensitivity, preprocessing, leakage review |
| Target variable | Name, type, possible values, clinical meaning, label-generation method/source, label-quality review, timestamp/horizon |
| Dataset/corpus | Named source, provenance, version, license, schema, target, data quality, privacy/de-identification, authorization, retention |
| Data split | Patient-level/temporal methodology, train/validation/test partitions, random seed, stratification, leakage prevention |
| Algorithm | Candidate comparison and one final selection justified by task/data/interpretability/safety/compute |
| Preprocessing | Training/inference-shared pipeline, fit-on-training-only behavior, transformations, version |
| Evaluation | Predeclared metrics, calibration, subgroup/fairness analysis, error review, clinical safety interpretation |
| Explainability | Method appropriate to the selected model and limitations of explanation |
| Safety | Human oversight, escalation, false-positive/negative risks, abstention, disclaimer, prohibited actions |
| Security/privacy | Authorization, patient ownership, logging minimization, secret management, external-provider policy |

## Phase 14 cannot begin until

The project owner has approved at least the capability, problem, features, target, dataset/corpus, algorithm, safety boundary, and evaluation plan. A model must not be trained or integrated into Django/frontend before those approvals exist.

No real patient data, unapproved public dataset, external AI provider, model artifact, prediction endpoint, or frontend connection may be introduced as a substitute for the missing approvals.
