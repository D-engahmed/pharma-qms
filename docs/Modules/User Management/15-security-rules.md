# Security Rules

## Core Rules

1. Backend authorization is authoritative.
2. Passwords are never stored in plaintext.
3. Passwords are never logged.
4. Authentication tokens/session secrets are never logged.
5. User deletion is not available through normal UI/API.
6. Inactive users cannot authenticate.
7. Only System Administrators manage roles and permissions.
8. Only System Administrators can create/deactivate users.
9. Multiple roles are allowed.
10. Effective permissions are the union of active-role permissions.
11. No deny-permission model in Version 1.
12. Concurrent sessions are prohibited.
13. Idle timeout is enforced server-side.
14. Authentication attempts are rate-limited.
15. Security-sensitive actions are audited.
16. Self-approval is prohibited where separation of duties applies.
17. Production uses HTTPS.
18. Secrets are provided through environment/secret management, not Git.
19. Database migrations are version-controlled.
20. Permission checks must occur before sensitive business operations.

## Administrator Protection

System Administrators must not be able to accidentally remove the last effective administrative authorization from their own account if doing so would leave the system without an administrative account.

## Data Exposure

User APIs must never return:

- password hash
- session tokens
- reset tokens
- internal security secrets
