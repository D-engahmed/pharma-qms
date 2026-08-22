from rest_framework.permissions import BasePermission

class HasPermission(BasePermission):
    permission_code = None
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_perm(self.permission_code)

def permission_required(perm_code):
    return type('PermissionRequired', (HasPermission,), {'permission_code': perm_code})

class SegregationOfDuties(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if hasattr(view, 'get_object'):
            try:
                obj = view.get_object()
                if hasattr(obj, 'created_by') and obj.created_by == request.user:
                    return False
            except:
                pass
        return True