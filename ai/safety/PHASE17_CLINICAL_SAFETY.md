# Phase 17 Clinical Safety Plan

## Scope

The future model is an academic classifier for a public dataset label. It is not a medical device, diagnostic system, prognosis tool, treatment recommender, triage service, or substitute for a clinician.

## Prohibited uses

The model must not be used to diagnose a MediCare patient, make emergency decisions, prescribe or discontinue medication, change a medical record, make an appointment decision, or issue individualized treatment or prevention advice. It must not be connected to patient self-service or doctor clinical workflows without a separately approved integration phase.

## Fail-closed behavior

The future inference path must reject missing required features, unsupported categories, non-finite values, out-of-range values, unknown model versions, missing artifacts, schema mismatches, and failed preprocessing. It must return an explicit unsupported/invalid status rather than fabricate a result.

## Human oversight and wording

Any later authorized display must identify the result as model-generated and academic, state that it is not a diagnosis or medical advice, and direct users to a qualified healthcare professional for real concerns. It must never use copy that implies certainty, causality, clinical validation, or institutional endorsement.

## Privacy and security

Phase 17 must use only the approved public dataset and must not access real MediCare patient data. It must remove identifiers, avoid raw-payload retention, keep artifacts outside public web directories, avoid secrets in code, and restrict any future endpoint by server-side role/permission checks. No endpoint is created in Phase 16.

## Release gate

A future release requires data authorization, license attribution, data-quality report, reproducible evaluation, bias/fairness review, security review, explainability review, artifact integrity check, and explicit project-owner approval. Phase 16 only produces the specification and does not satisfy those release gates.
