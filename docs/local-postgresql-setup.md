# MediCare Local PostgreSQL 18.6 Setup on Windows

## Scope and environment boundary

This guide is for the user’s **actual Windows computer**, where PostgreSQL 18.6 is installed and verified at `localhost:5432`. It must not be executed in the Manus Ubuntu sandbox. The sandbox cannot access the user’s Windows `localhost`, so PostgreSQL connectivity cannot be verified here.

The target connection is:

```text
PostgreSQL 18.6
host: localhost
port: 5432
database: medicare_db
application user: medicare_app
```

The application user’s password must be chosen and entered locally by the user. It is intentionally not included in this guide, the repository, `.env.example`, the SQL template, or the completion report.

## 1. Confirm PostgreSQL on Windows

Open **PowerShell** and confirm the local service and client. The exact service display name can vary by installer, so use the PostgreSQL service shown in Windows Services if the first command does not match.

```powershell
Get-Service *postgres*
psql --version
pg_isready -h localhost -p 5432
Test-NetConnection localhost -Port 5432
```

The expected readiness result is equivalent to:

```text
localhost:5432 - accepting connections
```

Do not expose PostgreSQL to the internet. Keep the server bound to local development access unless a later, explicitly approved deployment design requires otherwise.

## 2. Create the application role and database

The repository includes a password-free setup template at:

```text
database/scripts/create_medicare_db.sql
```

From **PowerShell at the MediCare project root**, run it against the PostgreSQL installation on the Windows computer:

```powershell
psql -U postgres -h localhost -p 5432 -d postgres -f database\scripts\create_medicare_db.sql
```

Enter the PostgreSQL administrator password when `psql` requests it. The script conditionally creates the `medicare_app` login role, then uses the interactive `\password medicare_app` command so you supply the application password privately. It conditionally creates `medicare_db` owned by `medicare_app`, revokes public database access, and grants the application role database connection access.

The script creates no MediCare business tables. It is safe to keep as a setup template, but do not place a real password inside it.

If you prefer to run SQL Shell manually, connect to the maintenance database:

```powershell
psql -U postgres -h localhost -p 5432 -d postgres
```

Then use the following statements, entering the password only through the interactive command:

```sql
CREATE ROLE medicare_app LOGIN;
\password medicare_app
CREATE DATABASE medicare_db OWNER medicare_app;
REVOKE ALL ON DATABASE medicare_db FROM PUBLIC;
GRANT CONNECT ON DATABASE medicare_db TO medicare_app;
\q
```

If a role or database already exists, use the repository script or inspect the existing object rather than blindly repeating the manual `CREATE` commands.

## 3. Create the local backend environment file

The canonical placeholder is:

```text
backend\.env.example
```

Create the ignored local file on Windows:

```powershell
Copy-Item backend\.env.example backend\.env
notepad backend\.env
```

Set the values locally. Replace only `CHANGE_ME`; do not paste the password into source control, documentation, JavaScript, HTML, or a report.

```dotenv
DJANGO_SECRET_KEY=replace-with-a-local-development-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=medicare_db
DB_USER=medicare_app
DB_PASSWORD=CHANGE_ME
DB_HOST=localhost
DB_PORT=5432

AI_API_KEY=
OTHER_SERVICE_KEYS=
```

The Django settings load `backend/.env` for local development without overriding variables already present in the process environment. `backend/.env` is ignored by Git. `backend/.env.example` contains placeholders only.

## 4. Recreate the Python virtual environment on Windows

The Phase 3 `backend/venv` created in the Ubuntu sandbox is not portable to Windows. Create a new Windows virtual environment inside the downloaded project:

```powershell
cd backend
py -3.12 -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

The requirements currently include only the backend foundation dependencies and the PostgreSQL driver:

```text
Django==5.2.17
djangorestframework==3.18.0
psycopg[binary]==3.3.4
```

## 5. Check Django’s PostgreSQL configuration

From `backend\`, run:

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default']['ENGINE'])"
```

The database engine should be:

```text
django.db.backends.postgresql
```

If it prints SQLite, Django did not receive all required `DB_*` values. Check that `backend\.env` exists, contains a non-empty `DB_PASSWORD`, and uses the exact variable names shown above.

## 6. Verify Django’s database connection without exposing credentials

Run this command from `backend\`:

```powershell
.\venv\Scripts\python.exe manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('Django PostgreSQL connection: OK')"
```

A successful result confirms that the Windows PostgreSQL server, `medicare_db`, `medicare_app`, password, host, port, psycopg driver, and Django settings work together. Do not print `connection.settings_dict` or connection parameters because those may include the password.

## 7. Run the Phase 5 migrations

Phase 5 now includes project migration files for the justified database foundation: the custom User identity foundation, patient and doctor profiles, patient preferences, appointments, medical records, prescriptions and prescription items, medical reports, and report findings. It does not include authentication flows, API endpoints, AI models, or sample data.

Run the consistency check and migrations from `backend\\`:

```powershell
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate
```

These migrations create the Django framework tables and the Phase 5 model tables only. They do not create or populate Patient, Doctor, Administrator, Appointment, MedicalRecord, Prescription, MedicalReport, Prediction, AIInsight, ChatConversation, ChatMessage, AuditLog, or any other model outside the generated Phase 5 applications.

## 8. Validate Phase 6 authentication

Phase 6 uses Django session authentication. The authentication endpoints are:

```text
GET  /api/auth/csrf/
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
GET  /api/auth/me/
```

The existing HTML frontend must be served from an origin listed in `FRONTEND_ALLOWED_ORIGINS`, such as `http://127.0.0.1:8010`. The Django API runs at `http://127.0.0.1:8000` by default. Do not put passwords, session cookies, or tokens into URLs, source files, or screenshots.

Run the automated backend authentication tests from `backend\\`:

```powershell
.\\venv\\Scripts\\python.exe manage.py test apps.accounts -v 2
```

The tests use an isolated test database and cover registration, duplicate handling, password hashing, login, wrong-password rejection, unknown-user rejection, CSRF, logout, current-user privacy, role mismatch, and backend role permissions.

For a manual local smoke test, configure `backend\\.env`, start Django, and serve the unchanged static frontend from a second PowerShell window:

```powershell
.\\venv\\Scripts\\python.exe manage.py runserver 127.0.0.1:8000
cd ..
py -m http.server 8010 --directory frontend
```

Open `http://127.0.0.1:8010/pages/auth/register.html`, create a non-production test account, then log in at `http://127.0.0.1:8010/pages/auth/login.html`. Confirm that the patient or doctor dashboard loads only for the matching authenticated role and that logout returns to login.

## 9. Start Django and test the health endpoint

Start the backend on loopback:

```powershell
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

In a second PowerShell window, call the existing health endpoint:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health/
```

Expected response:

```text
status service
------ -------
ok     MediCare API
```

The endpoint confirms that Django and DRF are running. It is not a substitute for the explicit database connection command in Section 6.

## 10. Common local errors

| Error | Meaning and action |
|---|---|
| `password authentication failed for user "medicare_app"` | Reset the role password locally with `psql` and update only `backend/.env`. |
| `database "medicare_db" does not exist` | Run the local database setup script or create the database through SQL Shell. |
| `role "medicare_app" does not exist` | Create the role locally; do not use the PostgreSQL superuser as the application user. |
| `connection refused` | Confirm the Windows PostgreSQL service is running and that `localhost:5432` is accepting connections. |
| `ModuleNotFoundError: No module named 'psycopg'` | Recreate or activate the Windows virtual environment and install `requirements.txt`. |
| Django selects SQLite | Check that all five `DB_*` variables are present and non-empty in `backend/.env`. |

## 11. Phase 10 boundary and startup scope

This setup prepares and validates the current Phase 1–10 application. The completed Phase 10 scope includes session authentication, patient profile/settings, patient and doctor dashboards, appointments and lifecycle management, patient clinical-data reads, and appointment-authorized doctor clinical-data creation/listing. The existing frontend remains HTML5, CSS3, and Vanilla JavaScript, and the UI is preserved.

The following remain intentionally deferred because no corresponding backend workflow exists in the current SRS/application: AI, chatbot, RAG, machine learning, personalized diagnosis or prediction, secure file upload/download, password changes, two-factor authentication, photo upload, account deletion, logout-all-devices, persistent refill requests, notifications, payments, and deployment. Do not treat the deferred controls as successful operations.

## References

[1]: [PostgreSQL Windows downloads](https://www.postgresql.org/download/windows/)  
[2]: [PostgreSQL Ubuntu downloads and package guidance](https://www.postgresql.org/download/linux/ubuntu/)  
[3]: [Django database configuration](https://docs.djangoproject.com/en/5.2/ref/settings/#databases)  
[4]: [Psycopg documentation](https://www.psycopg.org/psycopg3/docs/)  
