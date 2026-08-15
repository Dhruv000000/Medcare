# AI Model Boundary

The model layer owns versioned model metadata and inference interfaces. It must not own Django request parsing, patient authorization, database queries, frontend rendering, or secret management.

Phase 11 provides an abstract contract for future model adapters. No trained model artifact, serialized weights, model binary, or prediction implementation is included. A missing model must produce an explicit unavailable/deferred outcome rather than a fabricated result.

## Training versus inference

```text
approved dataset + versioned preprocessing
  -> training/evaluation pipeline (offline, future)
  -> reviewed model artifact and metadata
  -> model version registry (future)
  -> inference adapter (runtime, future)
```

The production application must never retrain a model when a patient opens a dashboard. Training and inference require separate controls, versions, logs, and rollback procedures.

## Minimum metadata

A future model record should include model name, semantic version, training date, dataset version, preprocessing version, evaluation artifact, intended use, limitations, approval status, and retirement date. It must not contain real patient records or secrets.
