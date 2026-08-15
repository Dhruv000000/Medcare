# MediCare Phase 11 AI Requirements Matrix

**Status:** Phase 11 foundation analysis  
**Source of truth:** Supplied MediCare SRS/project documentation and the current Phase 1–10 implementation.  
**Decision rule:** A capability is not considered implemented unless the current system has a real backend workflow, authorized data path, validated model/service, and tests appropriate to that capability.

## 1. Requirements matrix

| AI requirement | Evidence in supplied requirements | Legitimate current input data | Expected output | Algorithm/model specified? | Current status | Phase 11 decision |
|---|---|---|---|---|---|---|
| Symptom analysis | SRS lists symptom analysis and the prior frontend contained a demo symptom checker | No persistent symptom model or approved symptom dataset exists; the former browser matcher was disabled in Phase 10 | Structured educational decision-support result, if later approved | No | UI/deferred only | Foundation interface only; no predictor or result |
| Disease-risk prediction | SRS lists disease prediction/risk estimation | Current models contain profiles, records, prescriptions, and reports but no approved labels, feature schema, or dataset | Calibrated risk estimate with uncertainty and explanation, if later approved | No | Missing/deferred | No algorithm selection or model implementation |
| Medical-report analysis | SRS lists report analysis/explanation | Report title, type, summary, interpretation, and structured findings exist; attachments exist but secure file processing is deferred | Structured explanation with provenance and clinician disclaimer, if later approved | No | Data model exists; AI capability deferred | Define input/output/safety boundaries only |
| Medicine information | SRS lists medicine information | Prescription items contain medicine, dosage, frequency, duration, instructions, and side effects | Reference information from an approved source, if later approved | No | Missing/deferred | No external medical source or lookup implementation |
| Drug-interaction detection | SRS lists drug interaction detection | Prescription items are available, but no normalized medicine vocabulary or interaction knowledge source exists | Evidence-backed interaction warning with provenance, if later approved | No | Missing/deferred | No interaction engine or claims |
| Explainable AI | SRS lists explainable AI and prior architecture mentions future SHAP | No trained model or feature-attribution contract exists | Explanation tied to a versioned model and input features | No SHAP/LIME requirement is sufficiently specified | Architecture only | Define explanation contract; advanced methods deferred |
| Health recommendations | SRS lists health recommendations | No approved recommendation policy, clinical rules, or personalization consent model exists | Non-autonomous educational information, if later approved | No | UI/deferred only | No personalized or clinical recommendation output |
| Medical knowledge retrieval/RAG | SRS and prior architecture mention future RAG/knowledge assistant | No approved corpus, licensing decision, embeddings, vector store, or citations pipeline exists | Retrieved evidence with provenance and safety filtering | No provider/vector store specified | Architecture only | Document boundary; do not implement RAG |
| Medical chatbot | SRS and prior architecture mention future chatbot | No intent policy, knowledge boundary, LLM provider, or safety evaluation exists | Authenticated, bounded informational response | No provider/model specified | Architecture only | Document boundary; no chatbot or external LLM |
| AI auditability | SRS/prior architecture mention audit logs as future data responsibility | Current authentication and clinical ownership exist; no AI request/audit model exists | Non-sensitive audit metadata for future requests | Not applicable | Architecture only | Define minimum audit fields; no broad audit system |
| Model evaluation | Phase 11 explicitly requires an evaluation plan | No approved dataset or trained model exists | Task-appropriate measured metrics | No task/model selected | Planned only | Document planned versus actual metrics; report no results |

## 2. Explicitly not specified in the supplied requirements

The supplied material does not specify a production algorithm, clinical target label, approved training dataset, data license, feature schema, model family, cloud AI provider, LLM provider, embedding model, vector database, calibration procedure, confidence threshold, clinical validation protocol, or regulatory classification. These are recorded as **Not specified in supplied requirements — deferred decision** rather than filled with generic AI choices.

The supplied material also does not authorize using real patient records as a training corpus. No real patient data is added to the repository, and no random public medical dataset is downloaded.

## 3. Current data inventory relevant to future AI

| Source | Available fields | Legitimate future use | Important limitation |
|---|---|---|---|
| `User` and `PatientProfile` | Name, email, phone, date of birth, gender, role, blood group, address | Authorized demographic/context features only if a later task explicitly requires them | Sensitive attributes are not included by default; authorization and minimization are mandatory |
| `DoctorProfile` | Specialization, license identifier, contact details | Provider context or authorization metadata | Not a patient clinical feature source |
| `MedicalRecord` | Patient, doctor, appointment, record type, date, diagnosis, notes, optional attachment | Structured history context after explicit task/schema approval | No structured symptom table; free text and attachments require separate governance |
| `Prescription` and `PrescriptionItem` | Status, dates, medicine, dosage, frequency, duration, instructions, side effects | Medication context or future interaction task | No normalized drug identifiers or approved interaction source |
| `MedicalReport` and `ReportFinding` | Type, laboratory name, date, status, summary, interpretation, finding label/value/normality | Report explanation or laboratory feature task after validation | No standardized units/reference ranges; attachment processing is deferred |
| `Appointment` | Patient, doctor, date/time, status, reason, notes | Temporal and authorization context | Appointment reason/notes are not an approved diagnosis label or training target |

## 4. Phase 11 implementation boundary

Phase 11 creates reusable interfaces and documentation for validation, preprocessing, model invocation, structured output, explainability, service orchestration, safety, dataset governance, and future RAG/chatbot boundaries. The interfaces fail closed with explicit unsupported/deferred errors. They do not return diagnoses, risk percentages, confidence values, clinical recommendations, fabricated evidence, or fake model results.

The existing Phase 10 AI Insights page remains visually present but stays in a deferred state. No frontend JavaScript is connected to the Phase 11 foundation, and no AI endpoint is exposed from Django.

## References

[1]: ../upload/pasted_content_12.txt "Supplied Phase 11 authoritative requirements"
[2]: pasted_content.txt "Original MediCare project audit/SRS context"
[3]: PHASE10_COMPLETION_REPORT.md "Current Phase 1–10 implementation and deferred boundaries"
[4]: phase2-architecture.md "Approved future AI and backend architecture boundaries"
