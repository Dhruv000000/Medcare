# MediCare AI Requirements Specification — Phase 13

**Outcome:** **BLOCKED** for first-capability selection and model implementation.  
**Purpose:** Convert the broad SRS AI aspirations into an explicit specification boundary without inventing a capability, dataset, algorithm, or model.

## 1. Functional requirements reviewed

The supplied project material identifies the following candidate functional areas: symptom analysis, disease/risk prediction, medical-report analysis, medicine information, drug-interaction detection, health recommendations, explainable AI, medical knowledge retrieval/RAG, and a medical chatbot. These are candidate requirements, not approved implementation tasks. The current project has no runtime AI endpoint or model.

A future first capability must specify one task, authorized input contract, target/output, user, safe error behavior, human escalation path, and evidence/provenance requirements before implementation.

## 2. Non-functional requirements

Any future AI component must be modular, reproducible, server-controlled, testable, versioned, privacy-preserving, auditable, and independent of frontend JavaScript. It must use the existing Django authentication, role authorization, and patient/doctor ownership rules. It must fail closed for missing, malformed, unauthorized, unsupported, unavailable, or unsafe requests.

No future component may add an unapproved provider, secret, dependency, model artifact, database table, or endpoint. Training and inference preprocessing must be identical by version and configuration.

## 3. Input requirements

Inputs must be task-specific, minimal, typed, range/choice validated, ownership-authorized, and accompanied by a documented missing-value policy. Free text, attachments, demographics, prescriptions, reports, and records must not be included merely because they are available in the database. Every feature requires a clinical purpose and privacy review.

## 4. Output requirements

A future output must identify the task, model/algorithm and version where applicable, preprocessing/schema version, result or abstention, warnings, limitations, provenance where relevant, and a decision-support disclaimer. Model probabilities may be exposed only if the model genuinely produces them and calibration/interpretation are documented. Confidence, diagnosis, treatment advice, and evidence must never be fabricated.

## 5. Performance requirements

No performance target is specified by the supplied SRS. Future targets must be task-specific and predeclared before evaluation. For a clinical-support classifier, sensitivity, specificity, recall, precision, F1, calibration, and subgroup performance may be considered; the operating point must reflect the harm of false positives and false negatives. No Phase 13 performance metric is measured.

## 6. Safety requirements

The system must remain **Clinical Decision Support / Informational Assistance**. It must not independently diagnose, prescribe, select medication dosage, modify treatment or records, order tests, approve/reject treatment, or replace a physician. Future outputs require qualified clinical review and a clear escalation path for urgent or uncertain situations.

## 7. Privacy requirements

Patient scope must derive from the authenticated session and existing ownership rules. Doctors may only use data for authorized patients under the existing appointment-based clinical rule. Real patient records must not be used for training without explicit authorization, de-identification, governance review, and approved retention. External AI providers are prohibited until separately approved.

## 8. Explainability requirements

A future model must define what an explanation means for its task. Explanations must distinguish correlation from causation, identify model/version and relevant features or evidence, communicate limitations and abstention, and avoid exposing unnecessary clinical text. SHAP/LIME or another method is not selected in Phase 13.

## 9. Human oversight

A qualified clinician must remain responsible for interpreting any future result. The application must not automatically turn an AI result into a diagnosis, medication change, record change, test order, or treatment decision. Future workflows require review, override/escalation, audit metadata, and a documented response to unsafe or uncertain outputs.

## 10. Prohibited behavior

The system must not fabricate predictions, confidence, accuracy, medical evidence, patient history, or recommendations; use real patient data as a convenient dataset; access another patient’s data; expose raw model internals or secrets; connect an unapproved external provider; or call a deterministic demo an AI model.

## 11. Current status

The requirements remain **BLOCKED** because no single capability, problem, target, feature schema, dataset/corpus, or final algorithm is supported sufficiently by the supplied requirements. See `docs/AI_CAPABILITY_INVENTORY.md`, `ai/datasets/DATASET_SPECIFICATION.md`, and `docs/PHASE13_NEXT_PHASE_REQUIREMENTS.md`.
