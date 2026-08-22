from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import Employee, Department, Role, Permission
from .serializers import (
    EmployeeSerializer, EmployeeCreateSerializer, LoginSerializer,
    PasswordChangeSerializer, DepartmentSerializer, RoleSerializer,
    RoleCreateUpdateSerializer, PermissionSerializer
)
from .permissions import permission_required, role_required
from apps.audit.services import log_audit
from apps.session.models import UserSession


def get_client_ip(request):
    """Get client IP address, respecting trusted proxies"""
    remote_addr = request.META.get('REMOTE_ADDR')
    trusted_proxies = getattr(settings, 'TRUSTED_PROXIES', [])
    if remote_addr in trusted_proxies:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
    return remote_addr


class LoginView(APIView):
    """Authentication login view with account lockout protection"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email'].lower()
        password = serializer.validated_data['password']
        
        # Get user by email for lockout checking
        try:
            user = Employee.objects.get(email__iexact=email)
        except Employee.DoesNotExist:
            log_audit(
                user_id=None,
                username=email,
                action_type='LOGIN_FAILURE',
                module='auth',
                ip_address=get_client_ip(request),
                description='Invalid credentials - user not found'
            )
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if account is locked
        if user.is_locked():
            log_audit(
                user_id=user.id,
                username=user.email,
                action_type='LOGIN_REJECTED_LOCKED',
                module='auth',
                ip_address=get_client_ip(request),
                description='Account temporarily locked'
            )
            return Response(
                {'error': 'Account is temporarily locked. Try again later.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if account is active
        if not user.is_active or user.employment_status != 'ACTIVE':
            log_audit(
                user_id=user.id,
                username=user.email,
                action_type='LOGIN_REJECTED_INACTIVE',
                module='auth',
                ip_address=get_client_ip(request),
                description='Account inactive'
            )
            return Response(
                {'error': 'Account is inactive'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Authenticate
        authenticated_user = authenticate(request, username=email, password=password)
        
        if authenticated_user is None:
            # Increment failed login attempts
            user.increment_failed_login()
            log_audit(
                user_id=user.id,
                username=user.email,
                action_type='LOGIN_FAILURE',
                module='auth',
                ip_address=get_client_ip(request),
                description=f'Invalid credentials - attempt {user.failed_login_count}'
            )
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check for concurrent sessions
        active_session = UserSession.objects.filter(
            user=authenticated_user,
            revoked_at__isnull=True,
            expires_at__gt=timezone.now()
        ).first()
        
        if active_session:
            log_audit(
                user_id=authenticated_user.id,
                username=authenticated_user.email,
                action_type='LOGIN_REJECTED_CONCURRENT',
                module='auth',
                ip_address=get_client_ip(request),
                description='Concurrent session attempted'
            )
            return Response(
                {'error': 'This account already has an active session. Please log out from the other session.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Login successful
        login(request, authenticated_user)
        authenticated_user.reset_failed_login()
        authenticated_user.last_login = timezone.now()
        authenticated_user.save(update_fields=['failed_login_count', 'locked_until', 'last_login'])
        
        # Create session record
        request.session.create()
        UserSession.objects.create(
            user=authenticated_user,
            session_key=request.session.session_key,
            expires_at=timezone.now() + timedelta(seconds=settings.SESSION_COOKIE_AGE),
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        csrf_token = get_token(request)
        
        log_audit(
            user_id=authenticated_user.id,
            username=authenticated_user.email,
            action_type='LOGIN_SUCCESS',
            module='auth',
            ip_address=get_client_ip(request),
            description='Login successful'
        )
        
        # Determine redirect URL based on role
        role_map = {
            'admin': '/dashboard/admin',
            'sysadmin': '/dashboard/admin',
            'storekeeper': '/dashboard/storekeeper',
            'sampler': '/dashboard/sampler',
            'qc_analyst': '/dashboard/analyst',
            'qc_supervisor': '/dashboard/qcmanager',
            'manager': '/dashboard/manager',
        }
        first_role = authenticated_user.roles.first()
        redirect_url = role_map.get(first_role.code, '/dashboard/') if first_role else '/dashboard/'
        
        return Response({
            'user': EmployeeSerializer(authenticated_user).data,
            'csrf_token': csrf_token,
            'redirect_url': redirect_url
        })


class LogoutView(APIView):
    """Logout view"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            user_session = UserSession.objects.get(session_key=request.session.session_key)
            user_session.revoked_at = timezone.now()
            user_session.save()
        except UserSession.DoesNotExist:
            pass
        
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='LOGOUT',
            module='auth',
            ip_address=get_client_ip(request),
            description='User logged out'
        )
        
        logout(request)
        return Response({'message': 'Logged out successfully'})


class MeView(APIView):
    """Get current user information"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response(EmployeeSerializer(request.user).data)


class ChangePasswordView(APIView):
    """Change password view"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        if not request.user.check_password(old_password):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.set_password(new_password)
        request.user.force_password_change = False
        request.user.save()
        
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='USER_PASSWORD_CHANGED',
            module='users',
            entity_type='User',
            entity_id=str(request.user.id),
            description='Password changed'
        )
        
        return Response({'message': 'Password changed successfully'})


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet for Employee CRUD operations"""
    queryset = Employee.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeCreateSerializer
        return EmployeeSerializer
    
    def get_permissions(self):
        action_permission_map = {
            'create': 'users.create',
            'update': 'users.edit',
            'partial_update': 'users.edit',
            'destroy': 'users.deactivate',
            'deactivate': 'users.deactivate',
            'activate': 'users.activate',
            'reset_password': 'users.reset_password',
            'unlock': 'users.unlock',
            'roles': 'users.edit',
        }
        required_permission = action_permission_map.get(self.action, 'users.view')
        self.permission_classes = [IsAuthenticated, permission_required(required_permission)]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        user = serializer.save()
        log_audit(
            user_id=self.request.user.id,
            username=self.request.user.email,
            action_type='USER_CREATED',
            module='users',
            entity_type='User',
            entity_id=str(user.id),
            after_values={
                'email': user.email,
                'employee_number': user.employee_number
            },
            description=f"User {user.email} created"
        )
    
    def perform_update(self, serializer):
        old_email = serializer.instance.email
        user = serializer.save()
        log_audit(
            user_id=self.request.user.id,
            username=self.request.user.email,
            action_type='USER_UPDATED',
            module='users',
            entity_type='User',
            entity_id=str(user.id),
            description=f"User {user.email} updated"
        )
        if user.email != old_email:
            log_audit(
                user_id=self.request.user.id,
                username=self.request.user.email,
                action_type='USER_EMAIL_CHANGED',
                module='users',
                entity_type='User',
                entity_id=str(user.id),
                before_values={'email': old_email},
                after_values={'email': user.email},
            )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.employment_status = 'ACTIVE'
        user.is_active = True
        user.save()
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='USER_ACTIVATED',
            module='users',
            entity_type='User',
            entity_id=str(user.id),
            description=f"User {user.email} activated"
        )
        return Response({'status': 'activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        if user.is_last_active_sysadmin():
            return Response(
                {'error': 'Cannot deactivate the last active System Administrator.'},
                status=status.HTTP_409_CONFLICT
            )
        user.employment_status = 'INACTIVE'
        user.is_active = False
        user.save()
        # Revoke all active sessions
        user.usersession_set.filter(revoked_at__isnull=True).update(revoked_at=timezone.now())
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='USER_DEACTIVATED',
            module='users',
            entity_type='User',
            entity_id=str(user.id),
            description=f"User {user.email} deactivated"
        )
        return Response({'status': 'deactivated'})
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        user = self.get_object()
        new_password = request.data.get('password')
        if not new_password or len(new_password) < 12:
            return Response(
                {'error': 'Password must be at least 12 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.force_password_change = True
        user.save()
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='USER_PASSWORD_RESET',
            module='users',
            entity_type='User',
            entity_id=str(user.id),
            description=f"Password reset for {user.email}"
        )
        return Response({'message': 'Password reset successful'})
    
    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        user = self.get_object()
        user.locked_until = None
        user.failed_login_count = 0
        user.save()
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='USER_UNLOCKED',
            module='users',
            entity_type='User',
            entity_id=str(user.id),
            description=f"Account {user.email} unlocked"
        )
        return Response({'message': 'Account unlocked'})
    
    @action(detail=True, methods=['put'])
    def roles(self, request, pk=None):
        user = self.get_object()
        role_ids = request.data.get('role_ids', [])
        if not role_ids:
            return Response(
                {'error': 'At least one role required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_currently_sysadmin = user.roles.filter(code='sysadmin').exists()
        will_remain_sysadmin = Role.objects.filter(id__in=role_ids, code='sysadmin').exists()
        if is_currently_sysadmin and not will_remain_sysadmin and user.is_last_active_sysadmin():
            return Response(
                {'error': 'Cannot remove the System Administrator role from the last active administrator.'},
                status=status.HTTP_409_CONFLICT
            )
        
        roles = Role.objects.filter(id__in=role_ids, is_active=True)
        user.roles.set(roles)
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='USER_ROLE_CHANGED',
            module='users',
            entity_type='User',
            entity_id=str(user.id),
            after_values={'role_ids': role_ids}
        )
        return Response({'message': 'Roles updated'})


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Department CRUD operations"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    
    def get_permissions(self):
        action_permission_map = {
            'create': 'departments.create',
            'update': 'departments.edit',
            'partial_update': 'departments.edit',
            'destroy': 'departments.deactivate',
            'activate': 'departments.activate',
            'deactivate': 'departments.deactivate',
        }
        required_permission = action_permission_map.get(self.action, 'departments.view')
        self.permission_classes = [IsAuthenticated, permission_required(required_permission)]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        dept = serializer.save()
        log_audit(
            user_id=self.request.user.id,
            username=self.request.user.email,
            action_type='DEPARTMENT_CREATED',
            module='departments',
            entity_type='Department',
            entity_id=str(dept.id),
            description=f"Department {dept.name} created"
        )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        dept = self.get_object()
        dept.is_active = True
        dept.save()
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='DEPARTMENT_ACTIVATED',
            module='departments',
            entity_type='Department',
            entity_id=str(dept.id),
        )
        return Response({'status': 'activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        dept = self.get_object()
        active_dependents = dept.employee_set.filter(is_active=True).count()
        if active_dependents:
            raise ValidationError(
                f"Cannot deactivate: {active_dependents} active user(s) are still assigned to this department."
            )
        dept.is_active = False
        dept.save()
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='DEPARTMENT_DEACTIVATED',
            module='departments',
            entity_type='Department',
            entity_id=str(dept.id),
        )
        return Response({'status': 'deactivated'})


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet for Role CRUD operations"""
    queryset = Role.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RoleCreateUpdateSerializer
        return RoleSerializer
    
    def get_permissions(self):
        action_permission_map = {
            'create': 'roles.create',
            'update': 'roles.edit',
            'partial_update': 'roles.edit',
            'destroy': 'roles.deactivate',
            'activate': 'roles.activate',
            'deactivate': 'roles.deactivate',
        }
        required_permission = action_permission_map.get(self.action, 'roles.view')
        self.permission_classes = [IsAuthenticated, permission_required(required_permission)]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        role = serializer.save()
        log_audit(
            user_id=self.request.user.id,
            username=self.request.user.email,
            action_type='ROLE_CREATED',
            module='roles',
            entity_type='Role',
            entity_id=str(role.id),
            description=f"Role {role.name} created"
        )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        role = self.get_object()
        role.is_active = True
        role.save()
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='ROLE_ACTIVATED',
            module='roles',
            entity_type='Role',
            entity_id=str(role.id),
        )
        return Response({'status': 'activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        role = self.get_object()
        if role.code == 'sysadmin':
            if Employee.objects.filter(roles__code='sysadmin', is_active=True).exists():
                raise ValidationError(
                    "Cannot deactivate the System Administrator role while active users hold it."
                )
        role.is_active = False
        role.save()
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='ROLE_DEACTIVATED',
            module='roles',
            entity_type='Role',
            entity_id=str(role.id),
        )
        return Response({'status': 'deactivated'})


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Permission (read-only)"""
    queryset = Permission.objects.filter(is_active=True)
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, permission_required('permissions.view')]