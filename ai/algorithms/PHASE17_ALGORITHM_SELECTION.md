# Phase 17 Algorithm Selection

**Primary algorithm:** Logistic Regression  
**Task:** Binary classification of the UCI Heart Disease dataset label transformation  
**Training status:** Not performed in Phase 16

## Decision

Logistic Regression is the selected primary algorithm because it matches a compact binary classification task, supports categorical encoding and numeric scaling, is computationally modest, is reproducible, and permits bounded coefficient-based explanation. The coefficients must be described as model associations, not causal medical reasoning.

## Alternatives

| Algorithm | Strengths | Limitations | Decision |
|---|---|---|---|
| Shallow Decision Tree | Visual split paths, mixed-type support | Instability, overfitting, apparent certainty | Comparison alternative |
| Random Forest | Nonlinear interactions and robust tabular behavior | Lower transparency, calibration/explanation burden | Rejected as primary |
| Gradient Boosting | Strong tabular performance potential | Tuning, overfitting, larger governance burden | Rejected as primary |

## Future implementation constraints

The Phase 17 implementation must freeze the feature schema, target transformation, split protocol, random seed, and evaluation metrics before fitting. It must compare against a training-derived majority-class baseline and report only actual held-out results. No confidence/probability is exposed by default.

The model must remain offline and academic-only until a separate phase authorizes any API or frontend integration.
