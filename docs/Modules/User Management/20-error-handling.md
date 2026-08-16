# Error Handling

## General

Errors must be consistent between backend and frontend.

Suggested response:

```json
{
  "code": "USER_ALREADY_EXISTS",
  "message": "A user with this employee number or email already exists.",
  "field_errors": {
    "email": ["This email is already registered."]
  }
}
```

## Authentication Errors

Avoid unnecessarily revealing whether an account exists.

Examples:

- Invalid credentials
- Account inactive
- Account temporarily locked
- Concurrent session detected

Messages should be clear enough for legitimate users without exposing sensitive security information.

## Authorization

Unauthorized operations should return an appropriate authorization error.

Do not hide authorization failures by implementing only frontend restrictions.

## Business Rule Errors

Examples:

- Cannot deactivate the only System Administrator.
- Cannot assign an inactive role.
- Cannot assign a user to an inactive department.
- Cannot approve own controlled work.
- Cannot create a circular department hierarchy.
