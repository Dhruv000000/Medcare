# AI Preprocessing Boundary

Preprocessing is the single reproducible boundary shared by future training and inference. It must validate the request schema before any feature extraction, reject impossible or unsupported clinical values, record the preprocessing version, and produce a typed feature representation for a versioned model.

Phase 11 implements only a safe interface. It does not normalize free text, infer missing clinical facts, impute measurements, encode categories, or create features that are not justified by a selected task. The same function must eventually be used during training and inference to prevent training/serving skew.

## Future pipeline

```text
raw authorized input
  -> schema validation
  -> allowed-value/range validation
  -> missing-value policy
  -> task-approved feature extraction
  -> deterministic transformation
  -> versioned feature payload
```

A preprocessing failure is explicit and safe. It must not silently convert malformed clinical input into a plausible value.
