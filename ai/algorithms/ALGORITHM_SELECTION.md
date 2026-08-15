# MediCare Algorithm Selection — Phase 13

**Status:** **BLOCKED**  
**Selected capability:** None  
**Selected algorithm:** None

## Capability and problem

The supplied requirements identify symptom analysis, disease/risk prediction, medical-report analysis, medicine information, drug interaction, and health recommendations as candidate areas. They do not justify choosing one first capability. The former symptom checker is a UI demonstration, not a defined production ML problem.

No exact problem statement, task type, input contract, unit of prediction, intended user workflow, prohibited-use policy, target variable, or approved dataset exists for any candidate.

## Candidate comparison

| Candidate algorithm/family | Potential task | Advantages | Limitations and data requirements | Interpretability/safety | Status |
|---|---|---|---|---|---|
| Logistic Regression | Binary/multiclass symptom or disease-risk classification | Simple baseline, coefficient interpretation, low computational cost | Requires defined labels, numerical/encoded features, linear assumptions, calibration review | Relatively interpretable; still unsafe without validated labels and thresholds | Not selectable |
| Decision Tree | Small structured classification/rule-like task | Visual paths, handles mixed features, modest compute | Can overfit, unstable, requires labels and pruning strategy | Paths may be explainable but can appear more certain than justified | Not selectable |
| Random Forest | Structured classification/risk task | Nonlinear patterns, robust baseline, moderate inference cost | Less transparent, needs labels/features, probability calibration required | Feature importance is not causal explanation; clinical review required | Not selectable |
| Gradient Boosting | Tabular risk/classification task | Strong tabular performance potential | More tuning, overfitting/calibration risk, greater governance burden | Requires careful explanation and threshold review | Not selectable |
| SVM | Small structured classification task | Useful in some high-dimensional settings | Scaling/kernel choice, probability calibration, lower clinical transparency | Harder to explain and tune safely | Not selectable |
| Approved NLP/retrieval model | Report analysis or medicine information | May handle text/reference retrieval | Requires corpus/annotations/licensing/provenance and strong safety controls | Explanation/citation must be evidence-backed | Not selectable |

## Required dataset and features

A future selection must define one task-specific dataset, minimum feature schema, label/target schema, missingness, patient-level/temporal split, licensing, privacy approval, and evaluation protocol. Current models do not supply an approved symptom schema, clinical outcome labels, standardized laboratory units/reference ranges, normalized medicines, or a labeled report corpus.

## Selection reasoning

No final algorithm is selected because the problem definition and data characteristics are unknown. Choosing an algorithm now would be arbitrary and could create unsupported clinical claims. The only compliant Phase 13 decision is **BLOCKED**.

## Required next decision

Before model implementation, approve one capability and document its problem statement, task type, intended user/use, prohibited use, inputs/features, target, dataset/corpus, label-generation process, safety threshold/abstention policy, evaluation metrics, fairness review, and algorithm selection. Until those decisions exist, no algorithm file or model artifact should be created.


## Phase 16 final decision addendum

**Selected capability:** Academic disease-risk classification using UCI Heart Disease dataset label  
**Primary algorithm:** Logistic Regression  
**Comparison alternatives:** Shallow Decision Tree and Random Forest  
**Training status:** Not trained

Phase 16 resolves the prior algorithm ambiguity by fixing the first future task as binary classification of the UCI `num` field after the explicit transformation `0 -> 0` and `1..4 -> 1`. Logistic Regression is selected because it is a conservative, reproducible, interpretable baseline for a compact mixed-type dataset. It supports coefficient-based model-association explanations after one-hot encoding and scaling, but its output is not causal or diagnostic.

A majority-class classifier must be evaluated as the baseline. Any future comparison against a shallow Decision Tree or Random Forest must be predeclared, use the same leakage-controlled splits, and report actual held-out metrics only. No metric, prediction, model artifact, endpoint, or confidence value exists from Phase 16.

**Phase 16 status:** **SPECIFIED / READY FOR PHASE 17 MODEL IMPLEMENTATION**, subject to final dataset retrieval authorization, source/license recheck, schema/hash verification, and the pre-training safety gate.


## Phase 17 implementation addendum

The approved Logistic Regression pipeline was trained locally on the 242-record training partition and evaluated on the fixed 61-record stratified test partition. The majority-class baseline, Decision Tree, and Random Forest were evaluated using the same split and leakage-safe pipeline methodology. Actual metrics are recorded in `ai/evaluation/phase17_metrics.json` and the Phase 17 completion report.

The primary algorithm decision remains Logistic Regression. The alternative models were comparison models only and did not replace the approved primary decision. The trained Logistic Regression artifact is `ai/models/artifacts/uci-heart-disease-logreg-v1.0.0.joblib` with a recorded SHA-256 checksum.
