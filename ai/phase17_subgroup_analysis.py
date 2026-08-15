from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from joblib import load
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "ai" / "data" / "processed" / "uci_heart_disease_cleveland_processed.csv"
ARTIFACT_PATH = PROJECT_ROOT / "ai" / "models" / "artifacts" / "uci-heart-disease-logreg-v1.0.0.joblib"
OUTPUT_PATH = PROJECT_ROOT / "ai" / "evaluation" / "phase17_subgroup_analysis.json"
FEATURES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach",
    "exang", "oldpeak", "slope", "ca", "thal",
]
SEED = 42


def main() -> None:
    frame = pd.read_csv(DATA_PATH)
    X = frame[FEATURES]
    y = frame["disease_label_present"].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, stratify=y, random_state=SEED)
    bundle = load(ARTIFACT_PATH)
    model = bundle["pipeline"]
    prediction = model.predict(X_test)
    score = model.predict_proba(X_test)[:, 1]
    rows = []
    for value in sorted(X_test["sex"].dropna().astype(int).unique()):
        mask = X_test["sex"].astype(int).to_numpy() == value
        actual = y_test.to_numpy()[mask]
        predicted = prediction[mask]
        subgroup_score = score[mask]
        tn, fp, fn, tp = confusion_matrix(actual, predicted, labels=[0, 1]).ravel()
        result = {
            "source_feature": "sex",
            "source_value": int(value),
            "n": int(mask.sum()),
            "positive_label_count": int(actual.sum()),
            "accuracy": float(accuracy_score(actual, predicted)),
            "balanced_accuracy": float(balanced_accuracy_score(actual, predicted)),
            "precision": float(precision_score(actual, predicted, zero_division=0)),
            "recall_sensitivity": float(recall_score(actual, predicted, zero_division=0)),
            "specificity": float(tn / (tn + fp)) if (tn + fp) else None,
            "f1": float(f1_score(actual, predicted, zero_division=0)),
            "roc_auc": float(roc_auc_score(actual, subgroup_score)) if len(set(actual)) == 2 else None,
            "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
        }
        rows.append(result)
    result = {
        "model_version": bundle["model_version"],
        "protocol": "Same fixed stratified 80/20 split and seed 42 as primary evaluation; subgrouping uses source-coded sex only.",
        "interpretation": "Descriptive subgroup results only; small sample sizes and historical source bias prevent fairness or generalization conclusions.",
        "subgroups": rows,
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
