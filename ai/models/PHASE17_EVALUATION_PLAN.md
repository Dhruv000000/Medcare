# Phase 17 Evaluation Plan

**Task:** Binary classification of the UCI Heart Disease public dataset label  
**Primary model:** Logistic Regression  
**Status:** Specification only; no metrics exist yet

## Validation protocol

Use a reproducible stratified 80/20 holdout for final evaluation, with fixed stratified cross-validation within the training set for model and baseline decisions. Freeze the random seed, fold count, preprocessing pipeline, feature order, and threshold policy before inspecting the final test labels.

All imputation, category discovery, encoding, scaling, feature selection, and threshold decisions must be fitted inside training folds. The final test set remains untouched until the protocol is frozen. Duplicate and near-duplicate records must be audited before splitting.

## Baseline

Evaluate a majority-class classifier derived from the training labels only. The baseline is required to contextualize any future Logistic Regression result.

## Metrics

| Metric | Required interpretation |
|---|---|
| Accuracy | Overall correctness; report with class distribution |
| Balanced accuracy | Class-balanced correctness |
| Precision | Positive dataset-label correctness |
| Recall/sensitivity | Positive dataset-label capture |
| Specificity | Negative dataset-label recognition |
| F1 | Precision/recall harmonic mean |
| ROC-AUC | Threshold-independent ranking discrimination when valid |
| PR-AUC | Positive-class ranking under imbalance |
| Confusion matrix | Explicit false-positive and false-negative counts |
| Calibration review | Required before any probability-like output is considered |

No metric, prediction, or performance claim is made in Phase 16.

## Reporting requirements

The future report must include data version/hash, row counts, class distribution, exclusions, seed, split/fold protocol, preprocessing version, algorithm settings, baseline comparison, confidence intervals where feasible, failure cases, subgroup analysis where sample sizes support it, and a clear statement that the result is not clinically validated.
