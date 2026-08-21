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

    DO NOT put `HasPermission('code')` directly in `permission_classes`.
    DRF instantiates every entry in that list itself (`permission()`), so
    each entry must be a *class*. `HasPermission('code')` is already an
    *instance*; DRF would then try to call that instance again and raise
    TypeError: 'HasPermission' object is not callable.

    Use the `permission_required('code')` factory below instead, which
    returns a class:
        permission_classes = [IsAuthenticated, permission_required('users.view')]
    """
    permission_code = None  # set via subclass / permission_required()

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_perm(self.permission_code)


def role_permission(allowed_roles):
    return type('RolePermission', (BasePermission,), {
        'allowed_roles': allowed_roles,
        'has_permission': lambda self, request, view: request.user.is_authenticated and request.user.role in self.allowed_roles
    })


def permission_required(perm_code):
    """Returns a HasPermission subclass bound to perm_code — safe to use directly in permission_classes."""
    return type('PermissionRequired', (HasPermission,), {'permission_code': perm_code})
