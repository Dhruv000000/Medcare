# Phase 22 AI Security and Production-Readiness Audit Findings

**Status:** Audit and targeted hardening in progress.  
**Scope:** Existing Phase 17 model, Phase 18 API, Phase 19 patient restriction, and Phase 20–21 doctor workflow only.

## Findings and disposition

| ID | Severity | Finding | Evidence | Disposition |
|---|---|---|---|---|
| F-22-01 | **HIGH before fix; mitigated** | Django settings could silently use a development placeholder secret and `DEBUG=True` if deployment environment variables were omitted. | `backend/config/settings.py` previously defaulted `SECRET_KEY` and `DEBUG` without a production-mode fail-fast guard. | Added an explicit `DJANGO_ENV=production` guard requiring `DJANGO_SECRET_KEY`, `DEBUG=false`, `ALLOWED_HOSTS`, and `FRONTEND_ALLOWED_ORIGINS`. Local development defaults remain available when `DJANGO_ENV` is not production. |
| F-22-02 | **MEDIUM before fix; mitigated** | The request-size check primarily relied on `Content-Length`, which is not sufficient as the only boundary for bodies with missing/untrusted length metadata. | `backend/apps/ai_api/views.py` checked `CONTENT_LENGTH` before parsing. | Added a server-side `request.body` length check and generic 413 handling while preserving the existing 8 KiB contract. |
| F-22-03 | **MEDIUM before fix; mitigated** | The focused API suite did not explicitly verify inactive-doctor denial or that PUT/PATCH/DELETE cannot invoke inference. | Existing tests covered patient denial and GET→405 but lacked inactive-doctor and all non-POST cases. | Added explicit inactive-doctor `403` coverage and non-POST `405` coverage. |
| F-22-04 | **LOW before fix; mitigated** | Model-loading and inference failure paths used `logger.exception`, which emitted stack traces into server logs even though client responses were generic. | `backend/apps/ai_api/services.py` used stack-trace logging for unexpected load/inference exceptions. | Replaced it with safe exception-type metadata logging. Useful operational error classification remains without emitting stack traces from these paths. |
| F-22-05 | **INFORMATIONAL** | `joblib` deserialization is inherently unsafe for untrusted artifacts. | The service uses `joblib.load`. | No code change required: the path is server-controlled, the filename is fixed, the checksum is verified before loading, and no upload/model-selection route exists. Artifact replacement remains a controlled deployment operation. |
| F-22-06 | **INFORMATIONAL** | The model is academic and not clinically validated. | Phase 17 model card/evaluation and Phase 18–21 documentation. | Preserved and reinforced in API/UI wording. This remains a non-clinical limitation, not a software defect. |

## Confirmed clean areas

The audit found no model checksum change, duplicate AI route, patient prediction route, model artifact in frontend/static files, user-selectable model path, upload-based loading, external AI provider, chatbot/RAG/LLM integration, prediction persistence, patient data access from the AI endpoint, browser storage of AI data, CSRF exemption, unsafe result DOM injection in the AI path, or autonomous clinical action.

All AI-related dependencies are explicitly pinned in `backend/requirements.txt`. No dependency upgrade was performed because no safe security-critical dependency issue was identified within Phase 22 scope.

## Residual production requirements

Production deployment must provide a real secret, `DJANGO_ENV=production`, `DEBUG=false`, explicit allowed hosts, explicit frontend/CSRF origins, HTTPS, secure cookie transport, controlled log access, and a trusted deployment process for the checksum-verified artifact. The Phase 22 guard now fails fast when the first four application-level production variables are missing.

The model remains academic/development-only, not clinically validated, not a diagnosis, not medical advice, and not production clinical decision-making.


| F-22-07 | **MEDIUM before fix; mitigated** | Production mode did not explicitly enable HTTPS redirect, HSTS, secure cookies, or baseline response hardening. | `backend/config/settings.py` had development-oriented cookie/origin settings but no production-only transport/header guard. | Added production-only `SECURE_SSL_REDIRECT`, HSTS, secure session/CSRF cookies, `SECURE_CONTENT_TYPE_NOSNIFF`, and same-origin referrer policy. Development behavior remains unchanged when `DJANGO_ENV` is not production. |

**Phase 22 audit disposition:** All confirmed code-level findings identified in the audit were mitigated with targeted changes. No unresolved CRITICAL or HIGH software-security findings remain within the audited application scope. Technical production deployment still requires controlled HTTPS infrastructure, environment secrets, explicit hosts/origins, restricted log access, and a trusted artifact deployment process.
