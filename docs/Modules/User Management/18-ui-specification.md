# UI Specification

## Main Navigation

System Administrator:

```
Administration
├── Users
├── Departments
├── Roles
└── Permissions / Permission Matrix
```

Permissions should determine which menu items and actions are visible.

## Users Screen

Features:

- Search
- Filter
- Sort
- Pagination
- Create User
- Edit User
- Activate
- Deactivate
- Reset Password
- Unlock
- Manage Roles
- View Effective Permissions

Columns:

- Employee Number
- Name
- Email
- Department
- Job Title
- Status
- Roles
- Last Login

## User Form

Fields:

- Employee Number
- First Name
- Last Name
- Email
- Phone
- Department
- Job Title
- Status
- Roles

Use confirmation dialogs for:

- Deactivation
- Role changes with significant permission impact
- Password reset
- Unlock

## Department Screen

Tree/table hybrid:

```
Department
  ├── Child Department
  └── Child Department
```

## Role Screen

Show:

- Role name
- Code
- Status
- Assigned permissions
- Assigned users

Permission assignment should be grouped by module.

## User Profile

Tabs/sections:

1. Profile
2. Roles
3. Effective Permissions
4. Security
5. Audit History

## UX Rules

- Never display passwords.
- Explain inactive/locked status.
- Show validation errors near fields.
- Confirm destructive-looking security actions.
- Do not expose security-sensitive implementation details in errors.
