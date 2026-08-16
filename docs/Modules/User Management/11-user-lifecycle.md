# User Lifecycle

## States


ACTIVE
  |
  | deactivate
  v
INACTIVE
  |
  | activate
  v
ACTIVE


There is no DELETE state for normal application use.

## Create User


System Administrator
        |
        v
Enter user information
        |
        v
Validate fields
        |
        v
Validate unique Employee Number
        |
        v
Validate unique Email
        |
        v
Validate Department
        |
        v
Validate at least one active Role
        |
        v
Create account
        |
        v
Audit User Created
```

## Deactivate User

Preconditions:

- Authorized System Administrator
- Target user exists
- Target is currently ACTIVE

Actions:

1. Change status to INACTIVE.
2. Revoke active session.
3. Prevent future authentication.
4. Preserve historical references.
5. Generate audit event.

## Reactivate User

Actions:

1. Change status to ACTIVE.
2. Preserve existing roles unless explicitly changed.
3. Optionally require password reset according to policy.
4. Audit the activation.

## Employee Leaving Company

The account is changed to INACTIVE. It is not deleted.

Historical records continue to reference the same user identity.
