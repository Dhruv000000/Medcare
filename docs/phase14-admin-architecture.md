# MediCare Phase 14 Admin Architecture

**Status:** Implementation plan for the Admin module.  
**Source of truth:** Current Phase 1–13 repository and the authoritative Phase 14 prompt.

## Role and authentication

The existing custom `accounts.User` model already contains the `administrator` role, the existing login endpoint validates the requested role against the authenticated account, and administrator registration is protected by the server-side `ADMIN_REGISTRATION_CODE`. Phase 14 reuses this session/CSRF authentication flow. No second authentication system, hardcoded credential, or separate admin user model is introduced.

The shared frontend auth client will add the existing Admin page path to its role guard and role dashboard map. The backend `IsAdministrator` permission remains authoritative.

## Admin API boundary

A new Django app, `apps.admin_api`, will expose only explicit read or narrowly bounded management serializers under `/api/admin/`:

| Endpoint | Method | Purpose |
|---|---:|---|
| `/api/admin/dashboard/` | GET | Real counts and a bounded recent appointment summary |
| `/api/admin/patients/` | GET | Searchable patient account list |
| `/api/admin/patients/<id>/` | GET | One patient account-management detail |
| `/api/admin/doctors/` | GET | Searchable doctor account/profile list |
| `/api/admin/doctors/<id>/` | GET | One doctor account-management detail |
| `/api/admin/appointments/` | GET | Read-only appointment oversight with filters |
| `/api/admin/users/<id>/status/` | PATCH | Safe activate/deactivate for patient/doctor accounts; self-deactivation is rejected |
| `/api/admin/profile/` | GET | Read-only authenticated administrator profile |

Every endpoint uses session authentication, `IsAuthenticated`, and `IsAdministrator`. Admin serializers use explicit allow-lists. Passwords, password hashes, sessions, CSRF tokens, environment values, and unnecessary clinical data are excluded.

## Clinical-data decision

Phase 14 does not create Admin medical-record, prescription, or report endpoints. The supplied SRS does not clearly authorize unrestricted administrative clinical-data access, and the existing Phase 9 model design intentionally scopes clinical data to patients and authorized doctors. Admin oversight therefore remains limited to account and appointment metadata. Clinical access is **deferred** pending an explicit privacy/legal requirement.

## Permission matrix

| Function | Patient | Doctor | Administrator |
|---|---|---|---|
| Own patient dashboard | Own only | No | Not part of Admin module |
| Own doctor dashboard | No | Own only | Not part of Admin module |
| Patient management | No | No | Yes; account metadata only |
| Doctor management | No | No | Yes; account/profile metadata only |
| Appointment oversight | Own appointments | Authorized/assigned appointments | Read-only all appointments through Admin API |
| Account activation status | No | No | Patient/doctor targets only; not self |
| Clinical data | Own | Authorized patients | Deferred/minimal; no Phase 14 clinical endpoints |
| Admin dashboard/profile | No | No | Yes |
| Admin APIs | 403 | 403 | Yes |

## Frontend structure

New files will be placed only in the existing organized areas:

```text
frontend/pages/admin/
frontend/css/admin/
frontend/js/admin/
```

The Admin dashboard, patient list/detail, doctor list/detail, appointments, and profile pages will reuse the MediCare sidebar/topbar/card/table language. Patient and doctor pages will not be redesigned. Existing CSS files will not be modified; the Admin stylesheet will use the same visual tokens and responsive patterns.

## Audit and limitations

No audit-log model exists. Phase 14 will not create a large unrelated logging subsystem. Administrative status changes should be audited in a future dedicated phase. Empty databases render empty states, not fabricated counters. AI remains blocked exactly as documented in Phase 13; no AI code is touched.
