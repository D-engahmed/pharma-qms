# Audit Requirements

## Scope

All security-sensitive User Management actions must be audited.

## Audited Events

### User

- USER_CREATED
- USER_UPDATED
- USER_ACTIVATED
- USER_DEACTIVATED
- USER_EMAIL_CHANGED
- USER_ROLE_CHANGED
- USER_PASSWORD_RESET
- USER_PASSWORD_CHANGED
- USER_FORCE_PASSWORD_CHANGE_SET
- USER_UNLOCKED
- USER_SESSION_REVOKED

### Authentication

- LOGIN_SUCCESS
- LOGIN_FAILURE
- LOGIN_REJECTED_INACTIVE
- LOGIN_REJECTED_LOCKED
- LOGIN_REJECTED_CONCURRENT_SESSION
- SESSION_EXPIRED
- LOGOUT

### Role

- ROLE_CREATED
- ROLE_UPDATED
- ROLE_ACTIVATED
- ROLE_DEACTIVATED
- ROLE_PERMISSIONS_CHANGED

### Department

- DEPARTMENT_CREATED
- DEPARTMENT_UPDATED
- DEPARTMENT_ACTIVATED
- DEPARTMENT_DEACTIVATED

## Audit Data

Each event should capture where applicable:

- Timestamp
- Actor user
- Action
- Module
- Entity type
- Entity ID
- Before values
- After values
- IP address
- Correlation/request ID
- Description

Never store passwords, authentication tokens, or other secrets in audit data.

## Immutability

Audit records are append-only from the application's perspective.

Normal users and administrators must not be able to edit or delete audit events.

## Historical Identity

Historical business records must retain the original user identity even after the user becomes INACTIVE.
