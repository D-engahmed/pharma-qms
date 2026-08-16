# State Transitions and Authorization Rules

## User Status

| Current | Action | Next | Permission |
|---|---|---|---|
| ACTIVE | Deactivate | INACTIVE | users.deactivate |
| INACTIVE | Activate | ACTIVE | users.activate |

## Role Status

| Current | Action | Next | Permission |
|---|---|---|---|
| ACTIVE | Deactivate | INACTIVE | roles.deactivate |
| INACTIVE | Activate | ACTIVE | roles.activate |

## Authentication State

Authentication is not a business status. It is affected by:

- Employment status
- Lock state
- Active session state
- Password state
- Session expiry

## Authorization Evaluation

For each protected request:


Authenticated?
   ↓
User ACTIVE?
   ↓
Session valid?
   ↓
Required permission present?
   ↓
Business rule valid?
   ↓
Allow operation


All checks are server-side.

## Separation of Duties

A user must not approve/review a controlled action they personally performed when the action requires independent review.

The backend must compare the actor with the original performer and reject prohibited self-approval.
