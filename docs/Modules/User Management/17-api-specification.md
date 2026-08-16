# API Specification

Base path:

`/api/v1/`

## Authentication

### POST /auth/login/

Request:

```json
{
  "email": "user@example.com",
  "password": "..."
}
```

### POST /auth/logout/

Revokes current session.

### POST /auth/change-password/

Changes current user's password.

## Users

### GET /users/

List/search users.

Supported filters:

- status
- department
- role
- employee_number
- email
- search

### POST /users/

Create user.

### GET /users/{id}/

Retrieve user profile without security secrets.

### PATCH /users/{id}/

Edit permitted profile fields.

### POST /users/{id}/activate/

Activate user.

### POST /users/{id}/deactivate/

Deactivate user.

### POST /users/{id}/reset-password/

Administrator password reset.

### POST /users/{id}/unlock/

Unlock temporary account lock.

### PUT /users/{id}/roles/

Replace role assignment set.

## Departments

- GET /departments/
- POST /departments/
- GET /departments/{id}/
- PATCH /departments/{id}/
- POST /departments/{id}/activate/
- POST /departments/{id}/deactivate/

## Roles

- GET /roles/
- POST /roles/
- GET /roles/{id}/
- PATCH /roles/{id}/
- POST /roles/{id}/activate/
- POST /roles/{id}/deactivate/
- PUT /roles/{id}/permissions/

## Permissions

- GET /permissions/

Permission creation should normally be controlled by application deployment/code rather than arbitrary production users. System Administrators assign existing permissions to roles.

## Effective Permissions

### GET /users/me/permissions/

Returns effective permissions for the authenticated user.

## Session

### GET /users/me/session/

Returns safe session metadata.

### POST /users/me/logout/

Alternative explicit current-session logout endpoint if desired.

## API Rules

- Use consistent error format.
- Validate all inputs server-side.
- Return appropriate HTTP status codes.
- Enforce permissions at the endpoint/service layer.
- Audit state-changing security operations.
