from rest_framework.permissions import BasePermission


class HasRolePermission(BasePermission):
    """
    Legacy permission class for role-based access.
    Deprecated: use HasPermission with permission codes instead.
    Still imported by apps/packaging/views.py — do not remove without
    updating that app first.
    """
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in self.allowed_roles


class HasPermission(BasePermission):
    """
    Permission class for granular permission checks.
    Usage: permission_classes = [HasPermission('users.view')]
    """
    def __init__(self, permission_code):
        self.permission_code = permission_code

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_perm(self.permission_code)


def role_permission(allowed_roles):
    return type('RolePermission', (BasePermission,), {
        'allowed_roles': allowed_roles,
        'has_permission': lambda self, request, view: request.user.is_authenticated and request.user.role in self.allowed_roles
    })


def permission_required(perm_code):
    return type('PermissionRequired', (BasePermission,), {
        'perm_code': perm_code,
        'has_permission': lambda self, request, view: request.user.is_authenticated and request.user.has_perm(self.perm_code)
    })
