from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_ROOT / "ai" / "data" / "raw" / "uci_heart_disease_45" / "processed.cleveland.data"
PROCESSED_DIR = PROJECT_ROOT / "ai" / "data" / "processed"
MANIFEST_PATH = PROCESSED_DIR / "phase17_dataset_inspection.json"
PROCESSED_PATH = PROCESSED_DIR / "uci_heart_disease_cleveland_processed.csv"

ALL_COLUMNS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach",
    "exang", "oldpeak", "slope", "ca", "thal", "num",
]
FEATURE_COLUMNS = ALL_COLUMNS[:-1]
CATEGORICAL_COLUMNS = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]
NUMERIC_COLUMNS = ["age", "trestbps", "chol", "thalach", "oldpeak"]
ALLOWED_CATEGORIES = {
    "sex": {0, 1},
    "cp": {1, 2, 3, 4},
    "fbs": {0, 1},
    "restecg": {0, 1, 2},
    "exang": {0, 1},
    "slope": {1, 2, 3},
    "ca": {0, 1, 2, 3},
    "thal": {3, 6, 7},
}


def _json_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Official Cleveland file not found: {RAW_FILE}")

    df = pd.read_csv(
        RAW_FILE,
        header=None,
        names=ALL_COLUMNS,
        na_values=["?"],
        keep_default_na=True,
    )
    for column in ALL_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if list(df.columns) != ALL_COLUMNS:
        raise AssertionError(f"Unexpected columns: {list(df.columns)}")

    invalid = {}
    for column, allowed in ALLOWED_CATEGORIES.items():
        values = set(df[column].dropna().astype(int).unique().tolist())
        invalid[column] = sorted(values - allowed)
    invalid["num"] = sorted(set(df["num"].dropna().astype(int).unique().tolist()) - {0, 1, 2, 3, 4})
    invalid["numeric_nonpositive"] = {
        column: int((df[column].dropna() <= 0).sum())
        for column in ["age", "trestbps", "chol", "thalach"]
    }
    invalid["oldpeak_negative"] = int((df["oldpeak"].dropna() < 0).sum())

    target_missing = int(df["num"].isna().sum())
    target_invalid_rows = int(sum(bool(values) for values in [invalid["num"]]))
    duplicate_rows = int(df.duplicated().sum())
    missing_counts = {column: int(count) for column, count in df.isna().sum().items()}
    target_distribution = {
        str(int(key)): int(value)
        for key, value in df["num"].dropna().astype(int).value_counts().sort_index().items()
    }
    binary_target = df["num"].map(lambda value: None if pd.isna(value) else int(value != 0))
    binary_distribution = {
        str(int(key)): int(value)
        for key, value in binary_target.dropna().astype(int).value_counts().sort_index().items()
    }
    categorical_values = {
        column: sorted(int(value) for value in df[column].dropna().unique())
        for column in CATEGORICAL_COLUMNS
    }
    dtype_map = {column: str(dtype) for column, dtype in df.dtypes.items()}

    processed = df.copy()
    processed["disease_label_present"] = binary_target
    processed.to_csv(PROCESSED_PATH, index=False, na_rep="")

    manifest = {
        "dataset": "UCI Heart Disease",
        "uci_id": 45,
        "official_source": "https://archive.ics.uci.edu/dataset/45/heart+disease",
        "download_source": "https://archive.ics.uci.edu/static/public/45/heart+disease.zip",
        "license": "CC BY 4.0",
        "raw_file": str(RAW_FILE.relative_to(PROJECT_ROOT)),
        "processed_file": str(PROCESSED_PATH.relative_to(PROJECT_ROOT)),
        "records": int(df.shape[0]),
        "raw_columns": int(df.shape[1]),
        "feature_columns": FEATURE_COLUMNS,
        "target_column_original": "num",
        "target_column_normalized": "disease_label_present",
        "dtypes": dtype_map,
        "missing_counts": missing_counts,
        "duplicate_rows": duplicate_rows,
        "original_target_values": sorted(int(value) for value in df["num"].dropna().unique()),
        "original_target_distribution": target_distribution,
        "normalized_target_distribution": binary_distribution,
        "categorical_values": categorical_values,
        "invalid_values": invalid,
        "target_missing_rows": target_missing,
        "target_invalid_rows": target_invalid_rows,
        "cleaning_decisions": {
            "source_file": "Official UCI processed.cleveland.data only",
            "missing_values": "Preserved as missing in processed CSV; imputation is fitted inside training pipeline only",
            "duplicates": "Counted and reported; no exact duplicate rows were removed before split unless manifest says otherwise",
            "target": "Explicitly map num == 0 to 0 and num in 1..4 to 1; missing/other target values are invalid",
            "identifiers": "No identifier columns included in the selected 14-column Cleveland file",
            "invalid_values": "Reported; training script fails closed if invalid rows remain after the predeclared contract",
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
