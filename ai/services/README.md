# AI Service Boundary

The service layer is the only intended boundary between Django transport code and AI core modules. A future Django view must perform authentication, role authorization, ownership checks, request validation, rate limiting, and audit-context creation before invoking a service.

## Future orchestration

```text
authorized request context
  -> task-specific input schema
  -> preprocessing
  -> versioned model adapter or approved retriever
  -> structured result
  -> explanation contract
  -> safety validation
  -> API serializer
```

Phase 11 exposes no Django AI endpoint and does not connect the frontend to this package. The service interface returns an explicit unsupported/deferred error when no approved implementation exists.

## Response shape

A future response should contain only fields supported by the selected task, such as a request identifier, task, model/version when applicable, result or abstention, confidence only when calibrated, explanation only when available, provenance where relevant, warnings, and a mandatory clinical-safety disclaimer. Missing confidence and explanation remain null/omitted; they are never invented.

## Safe error categories

Future transport adapters should map invalid input, missing clinical information, unavailable model, model failure, service unavailable, unauthorized request, unsafe output, and unsupported request to stable user-safe error codes. Stack traces, model internals, credentials, server paths, and unnecessary clinical data must remain server-side.
