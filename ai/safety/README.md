# AI Safety Boundary

MediCare AI is a future decision-support and educational-assistance capability. It is not an autonomous diagnosis, prescription, treatment, or clinical approval system.

## Prohibited behavior

A future AI component must not claim certainty, independently diagnose, prescribe or modify medication, change medical records, order tests, approve or reject treatment, fabricate patient information, fabricate medical evidence, expose another patient’s information, or bypass Django authorization.

## Required request context

Every future request must carry an authorization context containing the authenticated user identifier, role, authorized patient scope, request type, and correlation/request identifier. Patient scope must be derived server-side from the existing ownership rules. A doctor’s clinical scope must remain appointment-authorized as established in Phase 9.

## Input safety

Reject missing required fields, invalid types, unsupported values, impossible dates/ranges, malformed payloads, unauthorized patient references, unsupported tasks, and attempts to submit ownership or role fields from the frontend. Do not silently infer or repair clinically meaningful values.

## Output safety

Before an output can reach a future API serializer, validate its schema, task identity, model/preprocessing versions, authorized patient scope, warning/disclaimer presence, evidence/provenance where required, confidence availability, explanation availability, and prohibited claims. No output is returned when no validated model exists.

## Safe user-facing boundary

Every future clinical-support response should communicate that it is informational/decision support and requires qualified professional judgment. Unsafe, unsupported, unavailable, or unauthorized requests should return a stable safe error rather than a partial or fabricated result.

## Auditability and logging

Future AI request metadata should include authenticated user, role, timestamp, request type, model version, preprocessing version, request identifier, and minimal non-sensitive metadata. Logs must exclude passwords, API keys, database credentials, unnecessary medical text, raw attachments, and other data not required for auditability.
