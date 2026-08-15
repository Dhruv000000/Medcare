# MediCare Phase 2 Architecture

## Purpose

This document records the safe architecture established during Phase 2. The existing frontend remains HTML5, CSS3, and Vanilla JavaScript. The organization separates public, authentication, patient, and doctor pages from their styles and scripts without replacing the visual design.

## Current frontend boundaries

The frontend is organized by responsibility:

| Area | Responsibility |
|---|---|
| `frontend/pages/public/` | Public landing page and marketing content |
| `frontend/pages/auth/` | Existing login and registration interfaces |
| `frontend/pages/patient/` | Existing patient dashboard and patient feature pages |
| `frontend/pages/doctor/` | Existing doctor dashboard prototype |
| `frontend/pages/admin/` | Reserved for a future administrator module; no Admin implementation exists yet |
| `frontend/css/shared/` | Existing shared landing-page stylesheet |
| `frontend/css/auth/` | Existing login and registration stylesheets |
| `frontend/css/patient/` | Existing patient page stylesheets |
| `frontend/css/doctor/` | Existing doctor dashboard stylesheet |
| `frontend/js/shared/` | Existing landing-page behavior |
| `frontend/js/auth/` | Existing client-side login and registration behavior |
| `frontend/js/patient/` | Existing patient page behavior |
| `frontend/js/doctor/` | Existing doctor dashboard behavior |
| `frontend/assets/` | Reserved for future local images and static assets; no supplied assets were present |

The page-specific file structure is intentionally retained. JavaScript and CSS were not merged into large global files, because doing so would increase regression risk and obscure the existing page boundaries.

## Deferred system boundaries

The following directories are architectural boundaries only. Phase 2 does not create Django code, database tables, API implementations, authentication services, AI algorithms, or real secrets.

| Directory | Future responsibility |
|---|---|
| `backend/` | Django and Django REST Framework project, domain apps, services, serializers, and server-side authorization |
| `ai/algorithms/` | Python symptom analysis, disease prediction, report analysis, medicine information, interaction detection, and recommendation logic |
| `ai/models/` | Versioned trained model artifacts and model metadata |
| `ai/preprocessing/` | Feature preparation, input normalization, and validation pipelines |
| `ai/explainability/` | Explainability methods, including future SHAP integration where appropriate |
| `ai/rag/` | Future retrieval, medical knowledge, and chatbot services |
| `database/documentation/` | Future PostgreSQL schema, relationships, migrations, and data ownership documentation |
| `tests/` | Future frontend, backend, API, security, database, authorization, and AI tests |
| `deployment/` | Future local setup, environment, deployment, backup, and release documentation |

## Future REST API areas

The eventual backend should keep responsibilities separated under stable route namespaces such as `/api/auth/`, `/api/patients/`, `/api/doctors/`, `/api/admin/`, `/api/appointments/`, `/api/medical-records/`, `/api/prescriptions/`, `/api/reports/`, `/api/predictions/`, `/api/ai/`, and `/api/chat/`. These are design targets only; no endpoints were implemented in Phase 2.

## Future data responsibilities

PostgreSQL should become the authoritative store for users, roles, patient and doctor profiles, appointments, medical records, prescriptions, reports, prediction metadata, AI insights, conversations, messages, and audit logs. Medical files should eventually use controlled storage with ownership and authorization checks rather than public frontend files. Database credentials and all sensitive configuration must be supplied through environment variables in a later backend phase.

## Future hybrid AI boundary

Python-based models and algorithms should handle appropriate prediction, classification, preprocessing, and explainability work. External AI services may later support conversational language, report explanation, or chatbot functionality after the provider, privacy policy, and safety boundary are approved. No provider was selected or integrated in Phase 2. Existing browser-side symptom matching remains a demo and was not converted into a fake backend or fake algorithm.

## UI/UX preservation policy

The current colors, typography, spacing, layouts, sidebar, navigation appearance, cards, tables, forms, dashboards, icons, and responsive styles are preserved. Phase 2 changes are limited to relative paths, the known navigation-blocking event handler, and the invalid duplicate homepage script reference. Any later functional integration must continue to use the existing pages as the visual foundation.

## Phase 2 validation policy

Validation must cover every HTML page, stylesheet reference, JavaScript reference, local navigation target, inline asset reference, and external resource declaration. Expected future gaps, such as the absent Admin dashboard, must remain documented rather than hidden by meaningless placeholder application files.
