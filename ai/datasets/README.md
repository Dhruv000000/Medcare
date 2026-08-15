# AI Dataset Governance

No dataset is downloaded or added in Phase 11. No real MediCare patient record is used as a training dataset.

## Future dataset requirements

A future task must identify the clinical target, source, collection process, consent/privacy status, licensing terms, data dictionary, de-identification approach, population, time period, and known limitations. The dataset version must be recorded together with preprocessing and model versions.

## Split and leakage controls

Training, validation, and test partitions must be defined before model fitting. Splits should occur at the patient level where repeated observations could otherwise leak identity, and temporal separation should be used when the task is time-dependent. No record, report, prescription, or derived feature from an evaluation patient may influence training preprocessing or label construction.

## Imbalance and reproducibility

Class imbalance must be measured and handled with a documented strategy that does not leak test labels. Seeds, environment versions, preprocessing configuration, and data snapshots must be recorded. Results must be reproducible from approved, versioned inputs.

## Privacy and retention

Only the minimum authorized fields may be exported for a documented task. Real patient data must not be committed to the repository, model artifacts, logs, tests, or screenshots. Retention, deletion, access, and audit rules require explicit approval before any training or evaluation run.
