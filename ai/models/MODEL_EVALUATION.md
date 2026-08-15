# Model Evaluation Plan

## Current status

No model has been trained or evaluated in Phase 11. Therefore there are **no measured accuracy, calibration, clinical utility, or safety results** to report. Any future report must keep planned metrics separate from actual measured metrics.

## Task-specific evaluation requirements

| Future task | Planned metrics, only if the task is approved | Additional requirements |
|---|---|---|
| Binary or multiclass disease-risk task | ROC-AUC and PR-AUC where appropriate; precision, recall, F1; sensitivity and specificity at a predeclared operating point; confusion matrix | Calibration, subgroup performance, temporal validation, clinically reviewed threshold |
| Structured symptom classification | Macro/micro F1, class-wise recall, confusion matrix, abstention/unsupported-input rate | Clear label definition and human-reviewed error analysis |
| Report extraction/explanation | Field-level precision/recall/F1 or agreement metric appropriate to the output | Provenance, missing-field behavior, clinician review, no unsupported inference |
| Drug interaction detection | Sensitivity/recall for clinically important interactions, precision, severity-stratified results | Authoritative reference set, versioned knowledge source, false-negative review |
| Retrieval/RAG | Retrieval recall/precision, citation completeness, groundedness review, abstention rate | Licensed corpus, provenance, temporal freshness, adversarial testing |

## Evaluation controls

Future datasets require documented source, license, patient/privacy status, preprocessing version, train/validation/test split, leakage prevention, temporal separation where appropriate, class-imbalance strategy, reproducible seeds, and an independent review set. Patient-level splitting is required wherever repeated records could otherwise leak identity across partitions.

## Clinical safety

No metric alone establishes clinical safety. A future model requires intended-use definition, human-review workflow, failure-mode analysis, subgroup/fairness review, calibrated uncertainty or explicit abstention, monitoring, version rollback, and approval before exposure to users.
