# AI Foundation Tests

Phase 11 tests validate architecture and safety boundaries, not clinical accuracy. There is no trained model and therefore no accuracy, calibration, sensitivity, specificity, or prediction-quality test result.

The foundation test suite must cover:

| Test area | Required assertion |
|---|---|
| Input validation | Malformed, missing, unsupported, and impossible values are rejected |
| Preprocessing interface | Valid input remains deterministic; unsupported transformations fail closed |
| Model interface | A missing/unavailable model cannot return a prediction |
| Output schema | Structured result fields are explicit; confidence/explanation are not fabricated |
| Service interface | Unsupported tasks return stable safe errors |
| Safety boundary | Prohibited claims, missing disclaimers, and missing authorization context are rejected |
| Authorization context | Patient/doctor scope is required and cannot be supplied as an untrusted frontend ownership override |
| Privacy/logging boundary | Sensitive values are not included in safe error text or audit metadata |

The explicit statement for Phase 11 is: **No model accuracy testing performed because no trained model exists.**
