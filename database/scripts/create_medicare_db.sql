-- MediCare local PostgreSQL 18.6 setup template for Windows.
-- Run this file only on the user's Windows PostgreSQL installation.
-- Do not execute it in the Manus Ubuntu sandbox.
-- Supply the application password interactively when prompted by \password.

-- Run this file while connected to the maintenance database as a PostgreSQL
-- administrator, for example with psql -U postgres -h localhost -p 5432 -d postgres.

SELECT format('CREATE ROLE %I LOGIN', 'medicare_app')
WHERE NOT EXISTS (
    SELECT FROM pg_roles WHERE rolname = 'medicare_app'
)\gexec

\password medicare_app

SELECT format('CREATE DATABASE %I OWNER %I', 'medicare_db', 'medicare_app')
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'medicare_db'
)\gexec

\connect medicare_db

REVOKE ALL ON DATABASE medicare_db FROM PUBLIC;
GRANT CONNECT ON DATABASE medicare_db TO medicare_app;

-- No MediCare business tables are created in Phase 4.
-- Django's built-in migrations are run later from the project backend:
--     python manage.py migrate
