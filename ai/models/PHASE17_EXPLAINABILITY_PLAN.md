# Phase 17 Explainability Plan

The primary Logistic Regression explanation will map signed coefficients back to source feature names after preprocessing. The explanation will describe which accepted feature values are associated with the model output and will not describe causes, medical reasoning, diagnosis, prognosis, or treatment advice.

Each future explanation record must include the model version, preprocessing version, accepted feature names/values, output label, and a fixed disclaimer. It must not reveal hidden training rows or any patient identifier. SHAP/LIME are not required for the primary implementation; adding them would require a separate method review and dependency decision.

The explanation layer must fail closed for invalid input, unsupported feature categories, missing required fields, missing model artifacts, or version mismatch. No probability or confidence value is exposed by default. Any later probability output requires calibration analysis, uncertainty communication, and explicit safety approval.
