# MediCare Django–AI Integration Boundary

## Phase 11 decision

No `backend/apps/ai_support` Django app is created or registered in Phase 11. The current application does not have an approved runtime AI task, model, provider, response schema, persistence requirement, or frontend action that would justify an active endpoint. Creating an endpoint that only returns an unsupported placeholder would create a misleading API surface.

The AI core lives in the top-level `ai/` package and is independent of Django. It contains contracts for authorization context, preprocessing, model adapters, structured responses, safety, explainability, service orchestration, datasets, and future RAG. It does not query Django models directly.

## Future integration sequence

```text
Django URL/view
  -> SessionAuthentication and role permission
  -> server-derived patient/doctor ownership scope
  -> request serializer and rate limit
  -> AI service request with AuthorizationContext
  -> top-level ai/ service
  -> structured validated response
  -> Django serializer
```

A future Django integration must not accept `patient_id`, `doctor_id`, `user_id`, record identifiers, or model/version overrides as proof of authorization. It must derive scope from the authenticated request and existing Phase 9 doctor-patient appointment rule.

## Future endpoint policy

Potential routes such as `/api/ai/predict/`, `/api/ai/explain/`, and `/api/ai/chat/` remain documentation-only design candidates. They must not be added until an actual task, model/service, safety review, audit approach, and frontend behavior are approved. No endpoint is exposed in Phase 11.
