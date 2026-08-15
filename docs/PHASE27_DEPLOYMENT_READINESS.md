# Phase 27 Deployment Readiness

**Status:** `EXTERNAL DEPENDENCY — PRODUCTION DEPLOYMENT REQUIRED`  
**Validation environment:** Ubuntu sandbox with SQLite fallback only  
**PostgreSQL:** Not installed, accessed, or validated

## 1. Readiness decision

The MediCare source contains production-oriented configuration guards and a documented PostgreSQL setup path, but no production server, domain, HTTPS certificate, PostgreSQL instance, durable protected-media store, secret manager, monitoring service, backup system, or rollback environment was available in the sandbox. Therefore, the project is **functionally complete for the implemented academic/development scope, with production deployment pending**.

Passing sandbox checks does not prove production deployment, PostgreSQL operation, clinical validation, regulatory approval, real-patient safety, or production load performance.

## 2. Required production environment

A deployment owner must provision a supported Python runtime, pinned dependencies, a production WSGI/ASGI serving layer, a reverse proxy, a domain or controlled internal origin, HTTPS certificates, a PostgreSQL database, durable protected-media storage, a secret-management mechanism, system monitoring, centralized log handling, backup storage, and an incident/rollback process.

The frontend must be served from an origin explicitly listed in `FRONTEND_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS`. The backend must not be exposed with Django’s development server as the production serving layer.

## 3. Environment variables

The current settings require the following production configuration. Values must be supplied through the deployment environment or an approved secret manager and must not be committed, placed in HTML/JavaScript, or included in reports.

| Variable | Required production meaning |
|---|---|
| `DJANGO_ENV=production` | Enables production guards and secure defaults |
| `DJANGO_SECRET_KEY` | Long, random, secret signing key; rotate through an approved procedure |
| `DEBUG=false` | Required by production guard |
| `ALLOWED_HOSTS` | Explicit backend host allowlist |
| `FRONTEND_ALLOWED_ORIGINS` | Explicit frontend origin allowlist; also drives CSRF trusted origins |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | Least-privilege application role |
| `DB_PASSWORD` | PostgreSQL application-role secret; never printed or committed |
| `DB_HOST` | Approved PostgreSQL host |
| `DB_PORT=5432` | PostgreSQL port unless a controlled deployment differs |
| `ADMIN_REGISTRATION_CODE` | Only if the approved Admin-registration workflow requires it; handle as a secret |

The current settings intentionally fall back to SQLite when all PostgreSQL variables are not present. This is suitable for sandbox/development validation only and must not be mistaken for production verification.

## 4. PostgreSQL procedure

The repository’s `docs/local-postgresql-setup.md` is the authoritative local guide. The user-side or deployment-owner procedure is:

1. Provision PostgreSQL and verify the service locally or in the approved environment.
2. Create a least-privilege `medicare_app` role and `medicare_db` database through the password-free SQL template, supplying the password interactively.
3. Create the ignored backend environment file with the five `DB_*` variables and production settings.
4. Recreate the target environment’s virtual environment from the pinned `backend/requirements.txt`; the Ubuntu sandbox virtual environment is not portable.
5. Run `manage.py check` and verify that Django reports `django.db.backends.postgresql` without printing credentials.
6. Run `manage.py makemigrations --check --dry-run`, then `manage.py migrate` from a reviewed release package.
7. Run a controlled database connection check and the approved regression suite.

No step above was executed against Windows PostgreSQL or a production server in Phase 27.

## 5. Static and frontend files

The frontend is static HTML5/CSS3/Vanilla JavaScript. A deployment owner must serve the `frontend/` directory from the approved origin over HTTPS, preserve its relative paths, configure correct MIME types, and avoid exposing backend source, model artifacts, `.env` files, SQLite files, Python caches, or protected media through the static server.

If Django static assets are collected, run `manage.py collectstatic` in the target environment into a controlled `STATIC_ROOT` and configure the reverse proxy or approved static-file service to serve only that output. This procedure was not executed in Phase 27.

## 6. Protected clinical media

Clinical attachments are stored beneath the protected `MEDIA_ROOT` and are returned only by authorized API views. A production deployment must use durable storage with restrictive filesystem/object-storage permissions, encryption at rest where required, access logging without raw clinical content, backup coverage, malware/content validation appropriate to the threat model, and a tested restore process.

The deployment must never publish `protected_media` as a public static directory or expose direct object URLs that bypass ownership/appointment authorization.

## 7. HTTPS, cookies, CSRF, and headers

Production settings enable secure session/CSRF cookies, HTTPS redirect, HSTS, content-type nosniff, and same-origin referrer policy when `DJANGO_ENV=production`. The deployment owner must still verify the reverse-proxy TLS termination, forwarded-header configuration, HTTPS redirect behavior, domain/origin allowlists, cookie flags, clickjacking policy, and error-page behavior in the actual environment.

These settings were source-reviewed and covered by prior production-configuration tests; the live HTTPS behavior was not deployed or tested in Phase 27.

## 8. Secret management and logging

Secrets must be stored in the platform’s approved secret manager or protected environment configuration. They must not appear in source control, archives, browser storage, URL parameters, logs, screenshots, crash reports, or support bundles.

Operational logging must retain safe event context while excluding passwords, session cookies, CSRF tokens, raw clinical payloads, patient identifiers where not strictly necessary, model inputs, and protected file contents. Production retention periods and access roles require governance approval.

## 9. Backup and recovery requirements

Before production use, the deployment owner must approve recovery-point and recovery-time objectives and test restoration for:

| Asset | Required production control |
|---|---|
| PostgreSQL | Encrypted scheduled backups, point-in-time recovery where justified, retention policy, restore drill |
| Protected clinical files | Encrypted durable backup, object/version integrity, ownership-preserving restore test |
| AI model artifact | Immutable versioned copy, checksum verification at deploy/startup, rollback copy |
| Configuration | Versioned non-secret configuration plus separately managed secrets |
| AI audit records | Approved retention, access control, backup, and restoration procedure |

No actual production backup or restore was performed in Phase 27.

## 10. Monitoring and incident response

A production deployment requires health/availability monitoring, error-rate and latency metrics, database/storage capacity monitoring, authentication and authorization anomaly monitoring, protected-download/upload event monitoring, AI endpoint rate-limit/error monitoring, model checksum alerts, drift/quality monitoring if AI is ever clinically considered, and an incident response runbook.

The project currently provides bounded application errors and safe logging patterns but does not include a production monitoring platform, alert routing, on-call schedule, or clinical safety incident system.

## 11. Model artifact deployment

The model artifact must be deployed only from a reviewed release package. The deployment pipeline must verify the model identity and SHA-256 before service startup and record the deployed model version in a release manifest. The required checksum is:

```text
uci-heart-disease-logreg-v1.0.0
SHA-256: e548527e51c67a7b611501acc844b367cecdde53413e33914ed9757fb9bae6cd
```

A checksum change must fail the deployment and trigger investigation. Phase 27 did not retrain, re-export, or modify the artifact.

## 12. Rollback procedure

The deployment owner must maintain a prior application release, database migration compatibility plan, protected-media compatibility plan, configuration version, and model artifact version. Rollback must be rehearsed with synthetic data or an approved non-production environment and must specify how to handle migrations that cannot be reversed, audit records generated by a newer release, and model-version reporting.

No production rollback rehearsal was performed in the sandbox.

## 13. Final deployment status

> **EXTERNAL DEPENDENCY — PRODUCTION DEPLOYMENT REQUIRED**

The source is deployment-prepared in configuration and documentation terms, but production deployment, PostgreSQL validation, backup/restore, monitoring, rollback, independent security testing, accessibility testing, and clinical validation remain outside the available environment and approval scope.

## References

[1]: local-postgresql-setup.md "MediCare local PostgreSQL setup guide"

[2]: ../backend/config/settings.py "MediCare deployment settings"

[3]: ../backend/requirements.txt "Pinned backend dependencies"

[4]: PHASE27_CLINICAL_VALIDATION_READINESS.md "Phase 27 clinical-validation readiness"
