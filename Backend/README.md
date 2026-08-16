# RM Receiving System — Access Control Layer (v1.0 implementation)

This is the shared Access Control Layer that all four business apps
(Storekeeper, Sampler, Analyst, QC Manager) will sit behind. It is not the
full RM Receiving System — the business apps themselves are built next,
each importing from these three apps.

## What's included

| App | Responsibility |
|---|---|
| `access_control` | Custom `User` model with GMP roles, admin-only role assignment, session login/logout, lockout policy |
| `audit_trail` | Append-only `AuditLog` (generic — works across every future business-app model), `AuditLogMixin` for DRF viewsets |
| `esignature` | `ESignatureEvent` (immutable), `RequiresESignature` mixin — password re-auth + mandatory "meaning" statement on GMP-critical actions |
| `integration_example` | **Reference only** — a stand-in `ExampleMaterial` model/viewset showing how a real business app wires into RBAC + audit + e-signature + segregation of duties. Delete this app once Storekeeper/QC Manager apps exist; copy its pattern instead. |

## Assumptions applied (open items from the v1.0 design doc)

These were flagged as pending confirmation. Defaults below were chosen as
reasonable GMP-standard values — **confirm with the client and adjust via
`.env` before go-live; nothing below requires a code change to override.**

| Item | Default applied | Where to change |
|---|---|---|
| Session idle timeout | 30 minutes, sliding | `SESSION_IDLE_TIMEOUT_SECONDS` in `.env` |
| Account lockout | 5 consecutive failed attempts → 30 min lock | `ACCOUNT_LOCKOUT_THRESHOLD` / `ACCOUNT_LOCKOUT_DURATION_MINUTES` |
| Analyst "Mark COA Completed" e-signature | **Required** (treated as GMP-critical, same as QC release) | `signed_actions` dict on the Analyst COA viewset, once built |
| Audit trail retention | Indefinite — no auto-purge. If the client confirms a finite retention period, add a scheduled archive (not hard-delete) Celery task | `audit_trail/models.py` docstring |
| Audit VIEW-logging (who read a record, not just who changed it) | Off by default per-endpoint (`log_view = False`), opt-in per viewset since it adds volume | `AuditLogMixin.log_view` on each viewset |
| Admin segregation-of-duties self-enforcement | `SegregationOfDutiesPermission` blocks a user from releasing/approving a record they created — applied in the reference viewset's `release`/`reject` actions | `access_control/permissions.py` |

Auth mechanism (Django session-based, not JWT) and e-signature method
(password re-entry, not a separate PIN) were confirmed in the v1.0 design
and are implemented as decided — not defaults.

## Running it

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit as needed; DATABASE_ENGINE=sqlite works with no setup
python manage.py migrate
python manage.py createsuperuser   # first admin — assign your own role via /admin/
python manage.py runserver
python manage.py test   # 13 tests covering RBAC, lockout, e-signature, audit append-only
```

## API surface so far

```
POST   /api/auth/login/                        {username, password}
POST   /api/auth/logout/
GET    /api/auth/me/                            -> current user + role (frontend uses this to route to the right dashboard)
POST   /api/admin/users/{id}/role/              admin-only {role, reason}

# Reference pattern (integration_example — delete once real apps exist):
GET    /api/example/materials/
POST   /api/example/materials/                  {name}
POST   /api/example/materials/{id}/release/      {password, reason}  -- e-signed, QC-Manager-only, blocked if you created it
POST   /api/example/materials/{id}/reject/       {password, reason}  -- e-signed
```

## Building the next business app (Storekeeper, Sampler, Analyst, QC Manager)

Follow `integration_example/views.py` as the template:
1. Model gets a `created_by` FK (or set `sod_field_name` if named differently).
2. Viewset extends `AuditLogMixin, RequiresESignature, viewsets.ModelViewSet`.
3. `get_permissions()` returns `HasRole.for_roles(Role.X, ...)` per action.
4. Any GMP-critical action (release, reject, mark-completed) gets an entry
   in `signed_actions` and calls `self.perform_esignature(...)` before
   mutating state.
5. Register the app in `INSTALLED_APPS` and mount its `urls.py` in
   `config/urls.py`.

## Still open / needs client confirmation before this goes to production

- Password complexity policy beyond Django's defaults (currently: min
  length + common-password + similarity + non-numeric-only validators).
- Whether failed e-signature attempts (wrong password on a release action)
  should be visible to the QC Manager's own supervisor, not just logged.
- Multi-factor authentication — not in the v1.0 design or this
  implementation; flag if the client's regulatory environment requires it.
