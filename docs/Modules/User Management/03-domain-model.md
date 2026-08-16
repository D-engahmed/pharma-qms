# Domain Model

## User

The User entity represents both the employee and the application account.

### Attributes

| Field | Required | Notes |
|---|---|---|
| id | Yes | Primary key |
| employee_number | Yes | Unique |
| first_name | Yes | |
| last_name | Yes | |
| email | Yes | Unique login identity |
| phone | No | |
| department_id | Yes | Primary department |
| job_title | Yes | |
| employment_status | Yes | ACTIVE / INACTIVE |
| password_hash | Yes | Never exposed through API |
| force_password_change | Yes | Boolean |
| failed_login_count | Yes | Security control |
| locked_until | No | Temporary lockout |
| last_login_at | No | Successful login |
| created_at | Yes | |
| updated_at | Yes | |
| created_by_id | No | Auditability |
| updated_by_id | No | Auditability |

## Department

| Field | Required | Notes |
|---|---|---|
| id | Yes | |
| code | Yes | Unique |
| name | Yes | |
| parent_id | No | Self-reference for hierarchy |
| is_active | Yes | |
| created_at | Yes | |
| updated_at | Yes | |

## Role

| Field | Required | Notes |
|---|---|---|
| id | Yes | |
| code | Yes | Unique |
| name | Yes | Unique |
| description | No | |
| is_active | Yes | |
| created_at | Yes | |
| updated_at | Yes | |

## Permission

| Field | Required | Notes |
|---|---|---|
| id | Yes | |
| code | Yes | Unique |
| name | Yes | |
| module | Yes | |
| description | No | |
| is_active | Yes | |

## UserRole

Many-to-many relationship:

```text
User 1 ───────< UserRole >─────── 1 Role
```

A user must have at least one active role.

## RolePermission

```text
Role 1 ───────< RolePermission >─────── 1 Permission
```

## Session

A session record is recommended so concurrent-session prevention and idle timeout can be enforced centrally.

Suggested fields:

- id
- user_id
- session_token/reference
- created_at
- last_activity_at
- expires_at
- revoked_at
- ip_address
- user_agent

Do not store raw authentication tokens in ordinary application tables.

## AuditEvent

Security and business actions are stored separately from technical application logs.

Suggested fields:

- id
- timestamp
- actor_user_id
- action
- module
- entity_type
- entity_id
- old_values JSONB
- new_values JSONB
- ip_address
- correlation_id
- description
