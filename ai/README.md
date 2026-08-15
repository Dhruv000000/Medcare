# MediCare AI Foundation

**Phase 11 status:** Foundation and architecture only. No trained model, prediction algorithm, external AI provider, RAG system, chatbot, or clinical recommendation engine is implemented.

The `ai/` package is the core AI boundary for future MediCare decision-support capabilities. It is intentionally separate from frontend JavaScript and from Django transport/authorization code. Future Django integration must call the service layer only after normal session authentication, role authorization, and patient/doctor ownership checks have succeeded.

## Architecture

```text
Frontend AI UI (currently deferred)
        |
        v
Django API boundary (future; not exposed in Phase 11)
        |
        v
Authentication and authorization
        |
        v
AI service orchestration
        |
        +--> input validation and preprocessing
        |
        +--> versioned model interface
        |
        +--> structured prediction result
        |
        +--> explainability interface
        |
        +--> safety validation and disclaimer
        |
        v
Structured response or safe error

Future and deferred branches:
knowledge ingestion -> retrieval -> provenance -> bounded generation
```

## Module map

| Module | Responsibility | Phase 11 status |
|---|---|---|
| `algorithms/` | Requirement-backed algorithm modules only | No algorithm selected or implemented |
| `preprocessing/` | Reproducible validation and feature preparation | Safe interface implemented; task-specific transforms deferred |
| `models/` | Model protocol, metadata, evaluation, and versioning | Interface implemented; no model artifact |
| `explainability/` | Explanation contract and feature-attribution boundary | Interface implemented; advanced SHAP/LIME deferred |
| `services/` | Django-independent orchestration boundary | Safe unsupported service implemented |
| `safety/` | Input/output safety, authorization context, disclaimers, and safe errors | Implemented as fail-closed checks |
| `rag/` | Future clinical knowledge retrieval boundary | Documentation only; no ingestion, embeddings, vector store, or LLM |
| `datasets/` | Dataset governance and provenance | Documentation only; no data downloaded |
| `tests/` | AI foundation tests | Tests cover interfaces and safety, not accuracy |

## Core safety position

MediCare remains an **Intelligent Clinical Decision Support System**, not an autonomous medical decision maker. Future AI output may support qualified clinical judgment and provide bounded educational information, but it must not independently diagnose, prescribe, modify medication or records, order tests, approve treatment, claim certainty, or fabricate evidence.

Phase 11 deliberately returns explicit unsupported/deferred errors where no validated model exists. It never returns a fabricated prediction, confidence value, clinical recommendation, medical explanation, dataset metric, or provider response.

## Current data boundary

The current Django models provide authorized profiles, appointments, medical records, prescriptions, prescription items, medical reports, report findings, and ownership relationships. There is no approved symptom table, normalized medication vocabulary, laboratory-unit schema, clinical target label, training dataset, model artifact, or consented AI persistence model. Future services must use only the minimum authorized data required for a documented task.

## Configuration and dependencies

No provider, model, API URL, API key, embedding system, vector database, or AI/ML dependency is selected in Phase 11. The existing Python dependency footprint remains unchanged. Future configuration must use safe environment placeholders and must never place secrets in source code, HTML, JavaScript, reports, tests, or model files.

## Traceability

See `docs/AI_REQUIREMENTS_MATRIX.md`, `docs/AI_SRS_TRACEABILITY.md`, and `docs/AI_ROADMAP.md` for requirement status, deferred decisions, and future sequencing.
