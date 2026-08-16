# Database Design

## Tables

Version 1 requires at least:

- users
- departments
- roles
- permissions
- user_roles
- role_permissions
- sessions 
- audit_events

## Key Constraints

### Users

- `employee_number` UNIQUE
- normalized `email` UNIQUE
- `employment_status` CHECK IN (`ACTIVE`, `INACTIVE`)
- email NOT NULL
- first_name NOT NULL
- last_name NOT NULL
- department_id NOT NULL
- job_title NOT NULL

### Departments

- code UNIQUE
- name should be unique within the desired organizational scope
- parent_id may be NULL for root departments
- prevent circular parent relationships in application logic

### Roles

- code UNIQUE
- name UNIQUE

### Permissions

- code UNIQUE

### User Roles

- UNIQUE(user_id, role_id)

### Role Permissions

- UNIQUE(role_id, permission_id)

## Recommended Indexes

Users:

- email
- employee_number
- employment_status
- department_id

Audit:

- timestamp
- actor_user_id
- entity_type + entity_id
- action

Sessions:

- user_id
- revoked_at
- expires_at

## Deletion Policy

Do not hard-delete users or audit events through normal application functionality.

Roles and departments should preferably be deactivated when historical references exist.

Permissions are controlled system metadata and should normally be deactivated rather than deleted once referenced.

## Email Normalization

Normalize email consistently before uniqueness checks and authentication.
