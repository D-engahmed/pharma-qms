from rest_framework.permissions import BasePermission, IsAuthenticated


class HasPermission(BasePermission):
    """Base permission class for granular permission checks"""
    permission_code = None
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.has_perm(self.permission_code)
        )


def permission_required(perm_code):
    """Returns a HasPermission subclass bound to perm_code"""
    return type(
        'PermissionRequired',
        (HasPermission,),
        {'permission_code': perm_code}
    )


class HasRole(BasePermission):
    """Permission class for role-based access control"""
    allowed_roles = []
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return any(request.user.has_role(role) for role in self.allowed_roles)


def role_required(*roles):
    """Returns a HasRole subclass with specified allowed roles"""
    return type(
        'RoleRequired',
        (HasRole,),
        {'allowed_roles': list(roles)}
    )


class SegregationOfDuties(BasePermission):
    """
    Permission class to enforce segregation of duties.
    Prevents users from approving their own work.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # For object-level permissions, check if user created the object
        if hasattr(view, 'get_object'):
            try:
                obj = view.get_object()
                if hasattr(obj, 'created_by') and obj.created_by == request.user:
                    return False
            except:
                pass
        
        return True


class IsOwnerOrReadOnly(BasePermission):
    """Permission to only allow owners to edit objects"""
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return obj.created_by == request.user