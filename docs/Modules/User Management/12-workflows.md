# User Management Workflows

## Workflow 1 — Create User


Admin
  ↓
Open Users
  ↓
Create User
  ↓
Enter Employee Number / Name / Email / Phone /
Department / Job Title / Status / Roles
  ↓
Validate
  ↓
Create User
  ↓
Set initial password/reset mechanism
  ↓
Force password change if configured
  ↓
Audit


## Workflow 2 — Assign Roles


System Administrator
  ↓
Open User
  ↓
Edit Roles
  ↓
Select one or more active roles
  ↓
Save
  ↓
Recalculate effective permissions
  ↓
Audit role change


## Workflow 3 — Create Role


System Administrator
  ↓
Create Role
  ↓
Define name/code
  ↓
Select permissions
  ↓
Save
  ↓
Audit


## Workflow 4 — Modify Role

Role permission changes immediately affect effective authorization for users assigned to that role.

The change must be audited with before/after permission sets.

## Workflow 5 — Login

See authentication specification.

## Workflow 6 — Deactivate User

See lifecycle specification.

## Workflow 7 — Reset Password


System Administrator
  ↓
Select User
  ↓
Reset Password
  ↓
Set temporary password through approved mechanism
  ↓
Set force_password_change = true
  ↓
Audit


The administrator must not be able to view the user's existing password.

## Workflow 8 — Unlock

If a user is temporarily locked due to failed authentication:


System Administrator
  ↓
User Profile
  ↓
Unlock
  ↓
Clear lock state
  ↓
Reset failed-attempt counter
  ↓
Audit

