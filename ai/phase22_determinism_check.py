from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
from joblib import load


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "ai" / "models" / "artifacts" / "uci-heart-disease-logreg-v1.0.0.joblib"
CHECKSUM = ARTIFACT.with_name(ARTIFACT.name + ".sha256")
FEATURES = {
    "age": 55.0,
    "sex": 1,
    "cp": 3,
    "trestbps": 130.0,
    "chol": 240.0,
    "fbs": 0,
    "restecg": 1,
    "thalach": 150.0,
    "exang": 0,
    "oldpeak": 1.0,
    "slope": 2,
    "ca": 0,
    "thal": 3,
}
ORDER = tuple(FEATURES)
EXPECTED = {
    "prediction": "label_absent",
    "model_probability": 0.16164121253810007,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


bundle = load(ARTIFACT)
frame = pd.DataFrame([[FEATURES[field] for field in ORDER]], columns=ORDER)
prediction = int(bundle["pipeline"].predict(frame)[0])
probability = float(bundle["pipeline"].predict_proba(frame)[0][1])
actual = {
    "prediction": "label_present" if prediction == 1 else "label_absent",
    "model_probability": probability,
    "model": bundle["model_version"],
    "artifact_sha256": sha256(ARTIFACT),
    "expected_sha256": CHECKSUM.read_text(encoding="utf-8").split()[0],
}
if actual["prediction"] != EXPECTED["prediction"] or actual["model_probability"] != EXPECTED["model_probability"]:
    raise SystemExit(json.dumps({"status": "FAIL", "actual": actual, "expected": EXPECTED}))
if actual["artifact_sha256"] != actual["expected_sha256"]:
    raise SystemExit(json.dumps({"status": "FAIL", "reason": "checksum mismatch", "actual": actual}))
print(json.dumps({"status": "PASS", "actual": actual, "expected": EXPECTED}, sort_keys=True))
