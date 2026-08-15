# Phase 17 Dataset Card

**Dataset:** UCI Heart Disease, UCI ID 45  
**Selected file:** official archive `processed.cleveland.data`  
**License:** CC BY 4.0, as stated by UCI  
**Acquisition status:** Acquired from the official UCI archive  
**Archive SHA-256:** `b17cd273da9ce1caa4710fce80227ea454d4dbf9fcbc8e6a9121672751563adc`

## Actual inspection

| Property | Actual result |
|---|---:|
| Records | 303 |
| Raw columns | 14 |
| Model features | 13 |
| Exact duplicate rows | 0 |
| Missing `ca` | 4 |
| Missing `thal` | 2 |
| Missing target `num` | 0 |
| Invalid categorical values | 0 observed |
| Invalid target values | 0 observed |
| Original target values | 0, 1, 2, 3, 4 |
| Normalized label-absent rows | 164 |
| Normalized label-present rows | 139 |

The source file contains the 13 Phase 16 features plus the original `num` field. The normalized target is `disease_label_present`, where `num=0` becomes 0 and `num=1..4` becomes 1. Missing feature values remain missing in the processed CSV and are imputed only inside the training-fitted pipeline.

## Privacy and use boundary

The training workflow used only the public UCI dataset. It did not access MediCare users, patients, appointments, medical records, prescriptions, reports, or PostgreSQL. No source identifier column was included in the selected file or model feature list. The model remains academic/development-only and is not clinically validated.

## Source and attribution

Official page: https://archive.ics.uci.edu/dataset/45/heart+disease  
Official archive: https://archive.ics.uci.edu/static/public/45/heart+disease.zip  
DOI: `10.24432/C52P4X`

Redistribution or adaptation must preserve UCI attribution, the source link/DOI, CC BY 4.0 notice, and any required modification notice.
