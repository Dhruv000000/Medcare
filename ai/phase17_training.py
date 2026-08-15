from __future__ import annotations

import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
import joblib
from joblib import dump
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "ai" / "data" / "processed" / "uci_heart_disease_cleveland_processed.csv"
MANIFEST_PATH = PROJECT_ROOT / "ai" / "data" / "processed" / "phase17_dataset_inspection.json"
ARTIFACT_DIR = PROJECT_ROOT / "ai" / "models" / "artifacts"
EVALUATION_DIR = PROJECT_ROOT / "ai" / "evaluation"
ARTIFACT_PATH = ARTIFACT_DIR / "uci-heart-disease-logreg-v1.0.0.joblib"
ARTIFACT_SHA_PATH = ARTIFACT_DIR / "uci-heart-disease-logreg-v1.0.0.joblib.sha256"

SEED = 42
TEST_SIZE = 0.20
CV_SPLITS = 5
MODEL_VERSION = "uci-heart-disease-logreg-v1.0.0"
TARGET_COLUMN = "disease_label_present"
FEATURE_COLUMNS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach",
    "exang", "oldpeak", "slope", "ca", "thal",
]
NUMERIC_COLUMNS = ["age", "trestbps", "chol", "thalach", "oldpeak"]
CATEGORICAL_COLUMNS = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_preprocessor() -> ColumnTransformer:
    numeric = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric, NUMERIC_COLUMNS),
            ("categorical", categorical, CATEGORICAL_COLUMNS),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )


def build_models() -> dict[str, object]:
    return {
        "majority_baseline": DummyClassifier(strategy="most_frequent"),
        "logistic_regression": Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                ("model", LogisticRegression(solver="lbfgs", max_iter=2000, random_state=SEED)),
            ]
        ),
        "decision_tree": Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                ("model", DecisionTreeClassifier(max_depth=4, min_samples_leaf=5, random_state=SEED)),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                ("model", RandomForestClassifier(n_estimators=200, max_depth=5, min_samples_leaf=2, random_state=SEED, n_jobs=1)),
            ]
        ),
    }


def validate_dataframe(df: pd.DataFrame) -> None:
    expected = FEATURE_COLUMNS + [TARGET_COLUMN, "num"]
    missing = [column for column in expected if column not in df.columns]
    if missing:
        raise ValueError(f"Missing expected processed columns: {missing}")
    extra = [column for column in df.columns if column not in expected]
    if extra:
        raise ValueError(f"Unexpected processed columns: {extra}")
    if df[TARGET_COLUMN].isna().any() or df["num"].isna().any():
        raise ValueError("Processed target contains missing values")
    if not set(df[TARGET_COLUMN].astype(int).unique()).issubset({0, 1}):
        raise ValueError("Processed target is not binary")
    expected_target = (df["num"].astype(int) != 0).astype(int)
    if not expected_target.equals(df[TARGET_COLUMN].astype(int)):
        raise ValueError("Normalized target does not match the approved num transformation")
    if df.duplicated(subset=FEATURE_COLUMNS + [TARGET_COLUMN]).any():
        raise ValueError("Exact duplicate rows remain in processed training data")


def metric_record(y_true: pd.Series, y_pred: np.ndarray, y_score: np.ndarray | None) -> dict[str, object]:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    record: dict[str, object] = {
        "n": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall_sensitivity": float(recall_score(y_true, y_pred, zero_division=0)),
        "specificity": float(tn / (tn + fp)) if (tn + fp) else None,
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
    }
    if y_score is not None:
        record["roc_auc"] = float(roc_auc_score(y_true, y_score))
        record["pr_auc"] = float(average_precision_score(y_true, y_score))
        record["brier_score"] = float(brier_score_loss(y_true, y_score))
    else:
        record["roc_auc"] = None
        record["pr_auc"] = None
        record["brier_score"] = None
    return record


def fit_predict_metrics(name: str, model: object, X_train: pd.DataFrame, X_test: pd.DataFrame, y_train: pd.Series, y_test: pd.Series) -> tuple[dict[str, object], object, np.ndarray, np.ndarray | None]:
    model.fit(X_train, y_train)
    prediction = model.predict(X_test)
    score = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
    return metric_record(y_test, prediction, score), model, prediction, score


def cross_validation_summary(models: dict[str, object], X_train: pd.DataFrame, y_train: pd.Series) -> dict[str, dict[str, object]]:
    cv = StratifiedKFold(n_splits=CV_SPLITS, shuffle=True, random_state=SEED)
    scoring = {
        "accuracy": "accuracy",
        "balanced_accuracy": "balanced_accuracy",
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
        "roc_auc": "roc_auc",
        "pr_auc": "average_precision",
    }
    output: dict[str, dict[str, object]] = {}
    for name, model in models.items():
        result = cross_validate(model, X_train, y_train, cv=cv, scoring=scoring, n_jobs=1, error_score="raise")
        output[name] = {
            metric: {
                "mean": float(np.mean(result[f"test_{metric}"])),
                "std": float(np.std(result[f"test_{metric}"])),
                "folds": [float(value) for value in result[f"test_{metric}"]],
            }
            for metric in scoring
        }
    return output


def save_confusion_matrix(matrix: list[list[int]], path: Path) -> None:
    fig, axis = plt.subplots(figsize=(5, 4), dpi=160)
    image = axis.imshow(matrix, interpolation="nearest", cmap="Blues")
    fig.colorbar(image, ax=axis)
    axis.set(
        xticks=[0, 1], yticks=[0, 1],
        xticklabels=["Label absent", "Label present"],
        yticklabels=["Label absent", "Label present"],
        ylabel="Actual label", xlabel="Predicted label", title="Logistic Regression confusion matrix",
    )
    threshold = max(max(row) for row in matrix) / 2 if matrix else 0
    for row in range(2):
        for column in range(2):
            axis.text(column, row, str(matrix[row][column]), ha="center", va="center", color="white" if matrix[row][column] > threshold else "black")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def save_calibration_plot(y_true: pd.Series, score: np.ndarray, path: Path) -> None:
    from sklearn.calibration import calibration_curve

    fraction_positive, mean_predicted = calibration_curve(y_true, score, n_bins=5, strategy="uniform")
    fig, axis = plt.subplots(figsize=(5, 4), dpi=160)
    axis.plot([0, 1], [0, 1], "--", label="Perfect calibration")
    axis.plot(mean_predicted, fraction_positive, "o-", label="Logistic Regression")
    axis.set(xlabel="Mean predicted probability", ylabel="Fraction positive", title="Calibration review")
    axis.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def save_coefficients(model: Pipeline, path: Path) -> None:
    preprocessor = model.named_steps["preprocess"]
    classifier = model.named_steps["model"]
    names = preprocessor.get_feature_names_out()
    coefficients = classifier.coef_[0]
    table = pd.DataFrame({"encoded_feature": names, "coefficient": coefficients})
    table["absolute_coefficient"] = table["coefficient"].abs()
    table["odds_ratio_per_unit"] = np.exp(table["coefficient"])
    table.sort_values("absolute_coefficient", ascending=False).to_csv(path, index=False)


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(DATA_PATH)
    df = pd.read_csv(DATA_PATH)
    validate_dataframe(df)
    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE, stratify=y, random_state=SEED)

    models = build_models()
    cv_summary = cross_validation_summary(models, X_train, y_train)
    test_metrics: dict[str, dict[str, object]] = {}
    fitted: dict[str, object] = {}
    test_predictions: dict[str, np.ndarray] = {}
    test_scores: dict[str, np.ndarray | None] = {}
    for name, model in models.items():
        metrics, fitted_model, prediction, score = fit_predict_metrics(name, model, X_train, X_test, y_train, y_test)
        test_metrics[name] = metrics
        fitted[name] = fitted_model
        test_predictions[name] = prediction
        test_scores[name] = score

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    EVALUATION_DIR.mkdir(parents=True, exist_ok=True)
    dataset_manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    source_archive = PROJECT_ROOT / "ai" / "data" / "raw" / "uci_heart_disease_45.zip"
    metadata = {
        "model_name": "MediCare academic heart disease label classifier",
        "model_version": MODEL_VERSION,
        "status": "academic_development_not_clinically_validated",
        "dataset": dataset_manifest,
        "dataset_archive_sha256": file_sha256(source_archive),
        "feature_columns": FEATURE_COLUMNS,
        "numeric_columns": NUMERIC_COLUMNS,
        "categorical_columns": CATEGORICAL_COLUMNS,
        "target": "disease_label_present: num=0 -> 0; num in 1..4 -> 1",
        "preprocessing": "numeric median imputation + StandardScaler; categorical most-frequent imputation + OneHotEncoder(handle_unknown=ignore), fitted inside Pipeline on training partitions",
        "algorithm": "LogisticRegression(solver=lbfgs, max_iter=2000, random_state=42, class_weight=None)",
        "baseline": "DummyClassifier(strategy=most_frequent)",
        "alternative_models": {
            "decision_tree": "DecisionTreeClassifier(max_depth=4, min_samples_leaf=5, random_state=42)",
            "random_forest": "RandomForestClassifier(n_estimators=200, max_depth=5, min_samples_leaf=2, random_state=42, n_jobs=1)",
        },
        "training_configuration": {
            "test_size": TEST_SIZE,
            "random_seed": SEED,
            "cv_splits": CV_SPLITS,
            "stratification": True,
            "train_records": int(len(X_train)),
            "test_records": int(len(X_test)),
        },
        "evaluation_metrics": test_metrics,
        "cross_validation": cv_summary,
        "safety": "Academic model output only; not a diagnosis, medical advice, prognosis, treatment recommendation, or clinical validation.",
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "scikit_learn_version": sklearn.__version__,
        "joblib_version": joblib.__version__,
        "matplotlib_version": matplotlib.__version__,
    }

    artifact_bundle = {
        "artifact_type": "sklearn_pipeline_bundle",
        "artifact_version": 1,
        "model_version": MODEL_VERSION,
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "pipeline": fitted["logistic_regression"],
        "metadata": metadata,
    }
    dump(artifact_bundle, ARTIFACT_PATH, compress=3)
    artifact_hash = file_sha256(ARTIFACT_PATH)
    ARTIFACT_SHA_PATH.write_text(f"{artifact_hash}  {ARTIFACT_PATH.name}\n", encoding="utf-8")

    logistic = fitted["logistic_regression"]
    save_coefficients(logistic, EVALUATION_DIR / "logistic_coefficients.csv")
    save_confusion_matrix(test_metrics["logistic_regression"]["confusion_matrix"], EVALUATION_DIR / "logistic_confusion_matrix.png")
    save_calibration_plot(y_test, test_scores["logistic_regression"], EVALUATION_DIR / "logistic_calibration.png")

    prediction_frame = pd.DataFrame({"test_row_index": y_test.index, "actual_label": y_test.values})
    for name, prediction in test_predictions.items():
        prediction_frame[f"{name}_prediction"] = prediction
    prediction_frame.to_csv(EVALUATION_DIR / "test_predictions.csv", index=False)

    (EVALUATION_DIR / "phase17_metrics.json").write_text(
        json.dumps({
            "model_version": MODEL_VERSION,
            "dataset_records": int(len(df)),
            "feature_count": len(FEATURE_COLUMNS),
            "target_distribution": {str(key): int(value) for key, value in y.value_counts().sort_index().items()},
            "split": metadata["training_configuration"],
            "test_metrics": test_metrics,
            "cross_validation": cv_summary,
            "artifact_sha256": artifact_hash,
        }, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (EVALUATION_DIR / "phase17_metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({"metadata": metadata, "artifact_sha256": artifact_hash}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
