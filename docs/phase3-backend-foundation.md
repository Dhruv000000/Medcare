# MediCare Phase 3 Backend Foundation

## Scope

Phase 3 establishes a minimal Django and Django REST Framework backend foundation inside the organized MediCare project. It does not implement authentication, PostgreSQL, business database models, AI algorithms, complete APIs, or frontend integration.

## Environment inspection

| Component | Result |
|---|---|
| Python | 3.12.3 |
| pip | Available through the project virtual environment; system `pip3` is managed by the environment’s `uv` wrapper |
| Virtual environment support | Available via `python3 -m venv` |
| System Django | Not installed before Phase 3 |
| System Django REST Framework | Not installed before Phase 3 |
| PostgreSQL client/server | `psql` and `pg_isready` were not available; PostgreSQL is not currently installed |

A project-local virtual environment is located at `backend/venv/` and is excluded by `.gitignore`.

## Backend structure

```text
backend/
├── manage.py
├── requirements.txt
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── __init__.py
│   └── health/
│       ├── __init__.py
│       ├── apps.py
│       ├── urls.py
│       └── views.py
└── README.md
```

The `health` application is a real minimal service boundary for the foundation endpoint. No business application, model, serializer, authentication flow, or fake domain logic was added.

## Dependencies

The current direct dependencies are deliberately minimal:

```text
Django==5.2.17
djangorestframework==3.18.0
```

## Configuration

Django reads `DJANGO_SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` from environment variables with development-safe defaults. `.env.example` contains placeholders only. SQLite remains the temporary Django development database because PostgreSQL is explicitly deferred. No business migrations were created.

No CORS package was added because the frontend is not connected to the backend in Phase 3. The future integration phase should define the development origin explicitly and avoid unrestricted production origins.

## Health endpoint

The only implemented API route is:

```text
GET /api/health/
```

It returns:

```json
{
  "status": "ok",
  "service": "MediCare API"
}
```

## Deferred work

Authentication, JWT, user registration, role-based authorization, PostgreSQL, patient/doctor/admin models, appointments, medical records, prescriptions, reports, AI services, SHAP, RAG, chatbot, medicine and interaction APIs, and frontend/backend integration remain future work. Phase 3 stops after the backend foundation and health endpoint are verified.
