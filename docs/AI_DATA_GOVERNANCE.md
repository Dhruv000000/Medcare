# MediCare AI Data Governance — Phase 13

## Ownership and accountability

The MediCare project owner remains responsible for approving the first AI capability, dataset use, target definition, and clinical safety boundary. A future dataset custodian must document provenance, transformations, access, versions, and retention. Clinical reviewers must approve label meaning and intended use before training.

## Provenance and licensing

Every future dataset or knowledge source must have a named origin, collection method, date/time scope, data dictionary, version/hash, license, permitted academic/commercial use, and redistribution/retention terms. Public downloadability is not approval.

## Patient-data restrictions

Real MediCare patient records must not be used as a convenient training dataset. Patient data may be used only for an explicitly approved task with authorization, minimization, access control, de-identification where appropriate, retention limits, auditability, and test-data separation. No patient data may be sent to an external AI provider in Phase 13.

## Anonymization and minimization

Direct identifiers must be excluded. Quasi-identifiers and free text require separate risk review because they may re-identify a person. Attachments and raw clinical narratives must not enter a dataset by default. Only the minimum feature subset for the approved task may be retained.

## Retention and access

Future dataset copies, preprocessing outputs, model artifacts, logs, and evaluation files require access controls and documented retention/deletion rules. Secrets, credentials, and raw clinical payloads must not be committed to the repository, model artifacts, test fixtures, or screenshots.

## Approval and separation

Training, validation, and test partitions must be created and controlled separately. A test partition must not influence feature engineering, preprocessing fitting, model selection, threshold selection, or hyperparameter decisions. Approval must be recorded before a training phase begins.

## Phase 13 status

No dataset exists or is approved. No real or synthetic training data is added. The status is **APPROVED DATASET NOT AVAILABLE**.
