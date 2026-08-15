# AI Algorithms

This directory is reserved for requirement-backed, independently testable algorithm modules. Each future algorithm must live in its own clearly named module and must be accompanied by a selection rationale, data contract, evaluation plan, limitations, and clinical-safety review.

Phase 11 created no algorithm implementation, and Phase 12 cannot add one because no final algorithm was selected and no approved dataset or target exists. The former browser-side symptom matcher was disabled in Phase 10 and is not promoted to an AI algorithm. No generic `model1.py`, random classifier, rules engine, or placeholder predictor is added.

**Phase 12 status:** Actual model implementation is blocked by missing approved algorithm selection, dataset, target variable, feature schema, and evaluation protocol. See `docs/PHASE12_IMPLEMENTATION_BLOCKER.md`.

Potential future modules identified from the SRS are:

| Candidate module | Intended task | Status |
|---|---|---|
| `symptom_analysis.py` | Structured symptom analysis | Deferred; no persistent symptom schema, dataset, or model specified |
| `disease_risk.py` | Disease-risk estimation | Deferred; no target, labels, dataset, or algorithm specified |
| `report_analysis.py` | Medical-report explanation | Deferred; no approved text/image model or evidence source specified |
| `medicine_information.py` | Medication information | Deferred; no approved reference source or lookup contract specified |
| `drug_interaction.py` | Interaction detection | Deferred; no normalized vocabulary or interaction corpus specified |
| `health_recommendation.py` | Bounded educational information | Deferred; no clinical policy, consent, or personalization contract specified |

These names are architectural candidates, not commitments to implement them in Phase 11.
