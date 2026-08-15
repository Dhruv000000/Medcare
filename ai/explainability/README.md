# Explainability Boundary

Explainability is a structured output contract, not a claim that every future model is inherently transparent. A future result may include feature contributions, evidence references, or a plain-language explanation only when those values are produced by a validated model or approved retrieval source.

## Required future properties

An explanation should identify the model and preprocessing versions, describe the relevant input features or retrieved evidence, communicate uncertainty or abstention, and state limitations. It must not invent causal explanations, transform correlation into diagnosis, reveal another patient’s data, or expose model internals unnecessarily.

Advanced SHAP, LIME, attention visualization, counterfactuals, and natural-language explanations are **deferred** because the SRS does not select a model or require a specific method. No explanation is returned by Phase 11 runtime interfaces.
