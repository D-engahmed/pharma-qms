# pharma-qms backend fixes — users & audit modules

All files here were verified against the actual repo: `python manage.py check`
passes, `makemigrations` produces a clean diff, `migrate` applies end to end,
and a real HTTP smoke test (login success/failure, then hitting the
previously-crashing `/api/v1/audit/audit-logs/` endpoint) behaves correctly.

## How to apply

Copy each file over the matching path in `Backend/`, preserving the directory
structure shown below. Then, on a fresh/dev database:

```bash
python manage.py migrate
python manage.py seed_initial_data
```

**Important — migrations were regenerated from scratch, not patched
incrementally.** The old `apps/users/migrations/0001_initial.py` and
`apps/audit/migrations/0001_initial.py` / `0002_initial.py` described a
schema that no longer matches `models.py` at all (missing `Department`,
`Role`, `Permission` tables; wrong `AuditLog` column names — see the earlier
analysis). If nobody has real data in a database built from the *old*
migrations, delete the old migration files and drop in the new ones as-is.
If a real database already exists on the old schema, you'll need a proper
incremental migration path instead of dropping these in — say the word and
I'll write that instead.

`apps/session/migrations/` didn't exist at all before (the app had no
migrations directory), which breaks `LoginView`/`LogoutView` since both
write to `UserSession`. Added `0001_initial.py` for it too.

## Files included

```
apps/users/models.py         — through_fields fix (fields.E334)
apps/users/admin.py          — roles moved to inline (admin.E013)
apps/users/permissions.py    — HasPermission no longer usable-but-broken directly
apps/users/views.py          — all HasPermission(...) call sites → permission_required(...)
                                + trusted-proxy IP check
apps/users/migrations/0001_initial.py   — regenerated, matches current models.py

apps/audit/models.py         — user FK: CASCADE → SET_NULL
apps/audit/serializers.py    — null-safe user_email / user_full_name
apps/audit/services.py       — session_id=None → '' (NOT NULL fix)
apps/audit/views.py          — permission_classes fix
apps/audit/middleware.py     — trusted-proxy IP check
apps/audit/migrations/0001_initial.py   — regenerated
apps/audit/migrations/0002_initial.py   — regenerated (adds `user` FK)

apps/session/migrations/0001_initial.py — new, was missing entirely

apps/materials/views.py      — HasPermission(...) → permission_required(...)
apps/products/views.py       — same
apps/sampling/views.py       — same
apps/coa/views.py            — same
```

The last four are included only because changing `permissions.py`'s
`HasPermission` signature would otherwise strand them (they use the exact
same broken pattern as `audit/views.py`). Nothing else in those four files
was touched — `apps/packaging/views.py` still uses the separate
`HasRolePermission` class and wasn't affected by this change.

## New bug found while verifying (not in the earlier writeup)

`apps/audit/services.py`'s `log_audit()` / `log_event_sync()` defaulted
`session_id=None`, but `AuditLog.session_id` is `CharField(blank=True)`
— blank, but **not** nullable. Since almost every call site (login failure,
account-locked/inactive/concurrent-session rejections, logout, and the
generic CRUD audit mixin whenever `request.audit_session` is `None`) never
passes `session_id` explicitly, this raised
`IntegrityError: NOT NULL constraint failed: audit_auditlog.session_id`
on essentially every audit-logged action in the system. Fixed by coercing
to `''` in both functions.

## Not fixed (flagged, out of scope for users/audit)

- `apps/materials`, `apps/packaging`, `apps/products`, `apps/sampling`,
  `apps/coa` have no migrations directories at all — same class of problem
  as the `session` app had. A full `Employee.delete()` will currently error
  with `no such table: materials_material` etc. because those apps'
  models were never migrated. Say the word if you want these generated too.
- `full_name` on `Employee` is still a dead, unpopulated field (flagged in
  the model's own comments) — `AuditLogSerializer` now falls back to the
  `username` snapshot instead of crashing on it, but nothing populates
  `full_name` itself. Low priority since `full_name_prop` is the real
  source of truth and is what `EmployeeSerializer` actually uses.
