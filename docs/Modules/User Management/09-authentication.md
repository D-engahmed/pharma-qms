# Authentication

## Login

Users authenticate with:

- Email
- Password

## Login Flow
```

Enter Email + Password
        |
        v
Normalize Email
        |
        v
Find User
        |
        +---- User missing ----> Generic authentication failure
        |
        v
Check ACTIVE
        |
        +---- INACTIVE ----> Reject
        |
        v
Check temporary lock
        |
        +---- Locked ----> Reject with appropriate message
        |
        v
Check active session
        |
        +---- Active session ----> Reject concurrent login
        |
        v
Verify password
        |
        +---- Failure ----> increment failure counter/rate limit
        |
        v
Create session
        |
        v
Return authenticated session/token
```

## Security

- Never reveal whether an email exists through an unnecessarily specific authentication error.
- Passwords must be hashed using Django's supported password hashing.
- Do not log passwords.
- Do not return password hashes through APIs.
- Rate-limit authentication attempts.
- Use secure cookies/tokens according to the selected authentication architecture.
- Production deployment must use HTTPS.

## Password Policy

Minimum:

- 8 characters
- At least one number

No unnecessary complexity requirements are imposed in Version 1.

## Password Reset

Administrator-driven reset.

After reset, the user should normally be required to change the temporary password at next login.

## Password Change

A logged-in user can change their own password if authorized by policy.

The current password should be required unless the operation is an administrator reset.

## Forced Password Change

When `force_password_change = true`:

- User may authenticate.
- User is directed to the change-password flow.
- Other application functionality is blocked until the password is changed, except for required account/session/logout operations.
- Successful password change clears the flag.
