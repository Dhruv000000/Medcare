# Phase 17 UCI Heart Disease Data

## Authoritative source

This directory contains the approved **UCI Heart Disease** dataset, UCI Repository ID 45, retrieved from the official UCI Machine Learning Repository archive:

- Dataset page: https://archive.ics.uci.edu/dataset/45/heart+disease
- Official archive used: https://archive.ics.uci.edu/static/public/45/heart+disease.zip
- Dataset DOI: `10.24432/C52P4X`
- License stated by UCI: **Creative Commons Attribution 4.0 International (CC BY 4.0)**

The source archive checksum and file checksums are recorded in `data/raw/uci_heart_disease_45.zip.sha256` and `data/raw/uci_heart_disease_45.files.sha256`.

## Selected file

Phase 17 uses only the official archive’s `processed.cleveland.data` file because Phase 16 specified the 303-row Cleveland subset with the 13-feature allow-list plus the original `num` target. Other files in the official archive are retained as source archive contents for provenance but are not used for training.

The target is normalized exactly as approved in Phase 16: source `num=0` becomes `disease_label_present=0`, and source `num=1,2,3,4` becomes `disease_label_present=1`. Missing or other target values are invalid.

## Privacy boundary

No MediCare patient records, users, appointments, medical records, prescriptions, reports, or PostgreSQL data were accessed or mixed with this dataset. No dataset identifiers are used as model features. The model artifact and logs contain schema/metric metadata only and no raw patient rows.

## Attribution and modification

The public source must be attributed to the UCI Machine Learning Repository and linked to the official dataset page and DOI. The processed CSV is a project-generated representation of the official Cleveland file, with missing tokens normalized to missing values and the approved binary target column added. The raw archive is preserved for provenance.
