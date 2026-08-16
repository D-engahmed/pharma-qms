# Session Management

## Goals

- Prevent concurrent sessions.
- Enforce idle timeout.
- Allow server-side session revocation.
- Preserve auditability.

## Concurrent Login Policy

Only one active session per user is allowed.

If a user attempts to log in while an active session exists:

```text
Login rejected:
"This account already has an active session. Please log out from the other session or wait for it to expire."
```

Do not provide a mechanism for ordinary users to bypass this rule.

## Idle Timeout

Recommended initial value: 30 minutes of inactivity.

Make the value configurable so it can be changed without code modification.

The timeout must be clearly documented and tested.

## Activity

Valid authenticated requests may update `last_activity_at`.

Do not update activity indiscriminately for health checks or unauthenticated requests.

## Session Expiry

When idle timeout is exceeded:

- Session becomes invalid.
- User must log in again.
- An audit event is generated where appropriate.

## Logout

Logout revokes the current session.

## Administrator Actions

System Administrator may revoke a user's active session if the permission is granted.

## Employee Deactivation

When a user is changed to INACTIVE:

- Reject future login.
- Revoke/invalidate active session(s).
- Audit the action.
