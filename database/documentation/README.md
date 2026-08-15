# MediCare Database Documentation

Phase 4 prepares the Django backend for the user’s Windows PostgreSQL 18.6 installation at `localhost:5432`. No PostgreSQL server was installed in the Manus Ubuntu sandbox, no database or role was created here, and no MediCare business tables or models were added.

Read the setup guide:

- [`docs/local-postgresql-setup.md`](../../docs/local-postgresql-setup.md) — Windows PostgreSQL 18.6 database, role, environment, migration, and connection instructions.
- [`database/scripts/create_medicare_db.sql`](../scripts/create_medicare_db.sql) — password-free `psql` setup template intended for user-side execution only.
- [`phase5-schema.md`](phase5-schema.md) — Phase 5 model fields, relationships, constraints, and deferred scope.
- [`docs/phase5-erd.png`](../../docs/phase5-erd.png) — rendered Phase 5 ER diagram.
- [`phase8-appointment-schema.md`](phase8-appointment-schema.md) — Phase 8 appointment lifecycle, status choices, constraints, and migration note.

Phase 8 reuses the existing appointment schema and adds only the documented status and patient-slot constraint migration. Clinical schema and later-phase data domains remain deferred.
