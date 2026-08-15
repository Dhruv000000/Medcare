# Phase 23 Model-Tied Explainable AI Design

## Decision

Phase 23 uses the Logistic Regression pipeline's **native signed coefficient contribution method**. SHAP and LIME are not added because neither dependency is present, and the existing Phase 17 specification already selects coefficient-based associations for this exact model. Grad-CAM is not appropriate for the current tabular Logistic Regression model and is not implemented.

This method is model-tied: it reads the loaded, checksum-verified pipeline's fitted preprocessor and classifier coefficients, transforms the validated input through that same preprocessor, and calculates the contribution of each transformed feature as:

```text
transformed_value × fitted_logistic_coefficient
```

The intercept is returned as a model base value. The sum of the base value and all transformed contributions is checked against the pipeline's `decision_function` for the same input. The API presents a safe aggregation back to the original 13 human-readable feature names.

## Preprocessing and mapping

The existing Phase 17 pipeline is reused without fitting, retraining, refitting, exporting, or modifying it. Numeric fields use the fitted median-imputer and scaler; categorical fields use the fitted most-frequent imputer and one-hot encoder. Each transformed feature name is mapped from `numeric__<feature>` or `categorical__<feature>_<source-code>` back to its original source feature. Contributions for each original feature are summed, which is exact for the current one-hot representation because only the active category contributes for each validated input.

The explanation returns all 13 original feature names in the existing feature order, the validated input value, the aggregated signed contribution in **logit units**, and a direction relative to the predicted class. Direction labels are limited to `supports_predicted_class`, `opposes_predicted_class`, or `neutral`; they do not imply causation or clinical importance.

## Safety and privacy

The explanation describes model behavior, not biological causation, diagnosis, treatment, medical certainty, or patient-specific clinical risk. The response includes a separate explanation disclaimer. Inputs, explanations, patient identifiers, and prediction history remain transient. No patient ID, database lookup, new model, new endpoint, migration, external provider, or browser storage is introduced.

The existing endpoint authorization, CSRF, 60-per-minute user throttle, 13-feature validation, fixed artifact loading, safe logging, and generic error behavior remain unchanged. Explanation generation occurs only after the existing serializer validates the request and only for an already-authorized request.

## Frontend presentation

The existing doctor AI result card gains a small model-contribution section. Each row uses the original feature name, accepted value, signed contribution, explicit textual direction, and a responsive bar whose width is normalized only for visual comparison. Text labels do not rely on color alone. Values are rendered with `textContent`, `replaceChildren`, and `createElement`; no raw API HTML, browser storage, or unsafe script execution is used.

## Limitations

Coefficient contributions are local model-behavior explanations in the model's logit space. They are not causal explanations, clinical reasoning, calibrated uncertainty, or evidence that a feature is clinically important. Aggregation from transformed columns to source fields is exact for this fitted one-hot/scaled pipeline, but the explanation remains subject to the model, dataset, preprocessing, and academic-development limitations documented in the Phase 17 model card.
