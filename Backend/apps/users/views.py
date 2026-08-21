from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.utils.timezone import now
from django.conf import settings
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError

from .models import Employee, Department, Role, Permission, UserRole
from .serializers import (
    EmployeeSerializer, EmployeeCreateSerializer, EmployeeUpdateSerializer,
    DepartmentSerializer, RoleSerializer, RoleCreateUpdateSerializer,
    PermissionSerializer
)
from .permissions import permission_required
from apps.audit.services import log_audit
from apps.session.models import UserSession


def _get_client_ip(request):
    # Was duplicated (and in LogoutView's case, stubbed to `pass` -> always
    # None) across LoginView/LogoutView. One implementation now.
    #
    # X-Forwarded-For is only trusted when REMOTE_ADDR is a known proxy
    # (settings.TRUSTED_PROXIES) — otherwise any client can spoof the IP
    # that ends up in LOGIN_SUCCESS/LOGIN_FAILURE audit rows. Mirrors
    # apps.audit.middleware.AuditMiddleware.get_client_ip.
    remote_addr = request.META.get('REMOTE_ADDR')
    trusted_proxies = getattr(settings, 'TRUSTED_PROXIES', [])
    if remote_addr in trusted_proxies:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
    return remote_addr


# ---------- Authentication Views ----------
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'error': 'Email and password required'}, status=400)

        email = Employee.objects.normalize_email(email).lower()
        user = authenticate(request, username=email, password=password)
        if user is None:
            log_audit(
                user_id=None, username=email, action_type='LOGIN_FAILURE',
                module='auth', ip_address=_get_client_ip(request),
                description='Invalid credentials'
            )
            return Response({'error': 'Invalid credentials'}, status=401)

        if user.employment_status != 'ACTIVE':
            log_audit(
                user_id=user.id, username=user.email, action_type='LOGIN_REJECTED_INACTIVE',
                module='auth', ip_address=_get_client_ip(request),
                description='Account inactive'
            )
            return Response({'error': 'Account is inactive'}, status=403)

        if user.locked_until and user.locked_until > now():
            log_audit(
                user_id=user.id, username=user.email, action_type='LOGIN_REJECTED_LOCKED',
                module='auth', ip_address=_get_client_ip(request),
                description='Account temporarily locked'
            )
            return Response({'error': 'Account temporarily locked'}, status=403)

        active_session = UserSession.objects.filter(
            user=user, revoked_at__isnull=True, expires_at__gt=now()
        ).first()
        if active_session:
            log_audit(
                user_id=user.id, username=user.email, action_type='LOGIN_REJECTED_CONCURRENT',
                module='auth', ip_address=_get_client_ip(request),
                description='Concurrent session attempted'
            )
            return Response({
                'error': 'This account already has an active session. Please log out from the other session or wait for it to expire.'
            }, status=403)

        login(request, user)
        user.failed_login_count = 0
        user.last_login = now()
        user.save(update_fields=['failed_login_count', 'last_login'])

        request.session.create()
        UserSession.objects.create(
            user=user,
            session_key=request.session.session_key,
            expires_at=now() + timedelta(seconds=settings.SESSION_COOKIE_AGE),
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        csrf_token = get_token(request)

        log_audit(
            user_id=user.id, username=user.email, action_type='LOGIN_SUCCESS',
            module='auth', ip_address=_get_client_ip(request),
            description='Login successful'
        )

        # Codes updated to match the 7-role taxonomy from 07-roles.md.
        role_map = {
            'admin': '/dashboard/admin',
            'sysadmin': '/dashboard/admin',
            'storekeeper': '/dashboard/storekeeper',
            'sampler': '/dashboard/sampler',
            'qc_analyst': '/dashboard/analyst',
            'qc_supervisor': '/dashboard/qcmanager',
            'manager': '/dashboard/manager',
        }
        first_role = user.roles.first()
        redirect_url = role_map.get(first_role.code, '/dashboard/') if first_role else '/dashboard/'

        return Response({
            'user': EmployeeSerializer(user).data,
            'csrf_token': csrf_token,
            'redirect_url': redirect_url,
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_session = UserSession.objects.get(session_key=request.session.session_key)
            user_session.revoked_at = now()
            user_session.save()
        except UserSession.DoesNotExist:
            pass

        log_audit(
            user_id=request.user.id, username=request.user.email, action_type='LOGOUT',
            module='auth', ip_address=_get_client_ip(request), description='User logged out'
        )
        logout(request)
        return Response({'message': 'Logged out'})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(EmployeeSerializer(request.user).data)


# ---------- Employee ViewSet ----------
class UserViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('-created_at')
    permission_classes = [IsAuthenticated, permission_required('users.view')]

    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EmployeeUpdateSerializer
        return EmployeeSerializer

    def get_permissions(self):
        # Previously only mapped create/update/partial_update/destroy —
        # activate/deactivate/reset_password/unlock/roles fell through to
        # the class default (users.view), letting read-only users perform
        # all of them. Fixed.
        action_permission_map = {
            'create': 'users.create',
            'update': 'users.edit',
            'partial_update': 'users.edit',
            'destroy': 'users.deactivate',
            'deactivate': 'users.deactivate',
            'activate': 'users.activate',
            'reset_password': 'users.reset_password',
            'unlock': 'users.unlock',
            'roles': 'users.edit',  # spec names no dedicated permission for this
        }
        required_permission = action_permission_map.get(self.action, 'users.view')
        self.permission_classes = [IsAuthenticated, permission_required(required_permission)]
        return super().get_permissions()

    def perform_create(self, serializer):
        user = serializer.save()
        log_audit(
            user_id=self.request.user.id, username=self.request.user.email,
            action_type='USER_CREATED', module='users',
            entity_type='User', entity_id=str(user.id),
            after_values={
                'email': user.email, 'employee_number': user.employee_number,
                'department_id': user.department_id,
            },
            description=f"User {user.email} created"
        )

    def perform_update(self, serializer):
        old_email = serializer.instance.email
        user = serializer.save()
        log_audit(
            user_id=self.request.user.id, username=self.request.user.email,
            action_type='USER_UPDATED', module='users',
            entity_type='User', entity_id=str(user.id),
            after_values={
                'first_name': user.first_name, 'last_name': user.last_name,
                'email': user.email, 'job_title': user.job_title,
            },
        )
        if user.email != old_email:
            log_audit(
                user_id=self.request.user.id, username=self.request.user.email,
                action_type='USER_EMAIL_CHANGED', module='users',
                entity_type='User', entity_id=str(user.id),
                before_values={'email': old_email}, after_values={'email': user.email},
            )

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_last_active_sysadmin():
            return Response(
                {'error': 'Cannot deactivate the last active System Administrator.'},
                status=status.HTTP_409_CONFLICT
            )
        user.employment_status = 'INACTIVE'
        user.is_active = False
        user.save()
        user.usersession_set.filter(revoked_at__isnull=True).update(revoked_at=now())
        log_audit(
            user_id=request.user.id, username=request.user.email,
            action_type='USER_DEACTIVATED', module='users',
            entity_type='User', entity_id=str(user.id),
            after_values={'status': 'INACTIVE'},
            description=f"User {user.email} deactivated"
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.employment_status = 'ACTIVE'
        user.is_active = True
        user.save()
        log_audit(
            user_id=request.user.id, username=request.user.email,
            action_type='USER_ACTIVATED', module='users',
            entity_type='User', entity_id=str(user.id),
            after_values={'status': 'ACTIVE'}
        )
        return Response({'status': 'activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        return self.destroy(request, pk)

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        user = self.get_object()
        new_password = request.data.get('password')
        if not new_password or len(new_password) < 8:
            return Response({'error': 'Password must be at least 8 characters'}, status=400)
        user.set_password(new_password)
        user.force_password_change = True
        user.save()
        log_audit(
            user_id=request.user.id, username=request.user.email,
            action_type='USER_PASSWORD_RESET', module='users',
            entity_type='User', entity_id=str(user.id),
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
            user_id=request.user.id, username=request.user.email,
            action_type='USER_UNLOCKED', module='users',
            entity_type='User', entity_id=str(user.id)
        )
        return Response({'message': 'Account unlocked'})

    @action(detail=True, methods=['put'])
    def roles(self, request, pk=None):
        user = self.get_object()
        role_ids = request.data.get('role_ids', [])
        if not role_ids:
            return Response({'error': 'At least one role required'}, status=400)

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
            user_id=request.user.id, username=request.user.email,
            action_type='USER_ROLE_CHANGED', module='users',
            entity_type='User', entity_id=str(user.id),
            after_values={'role_ids': role_ids}
        )
        return Response({'message': 'Roles updated'})


# ---------- Department ViewSet ----------
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, permission_required('departments.view')]

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
            user_id=self.request.user.id, username=self.request.user.email,
            action_type='DEPARTMENT_CREATED', module='departments',
            entity_type='Department', entity_id=str(dept.id),
            after_values={'code': dept.code, 'name': dept.name},
        )

    def perform_update(self, serializer):
        dept = serializer.save()
        log_audit(
            user_id=self.request.user.id, username=self.request.user.email,
            action_type='DEPARTMENT_UPDATED', module='departments',
            entity_type='Department', entity_id=str(dept.id),
            after_values={'name': dept.name, 'is_active': dept.is_active},
        )

    def _deactivate(self, request, dept):
        # 06-departments.md: cannot deactivate while active users depend on
        # it, unless reassigned. No reassignment endpoint exists yet, so
        # this hard-blocks rather than guessing a reassignment target.
        active_dependents = dept.employee_set.filter(is_active=True).count()
        if active_dependents:
            raise ValidationError(
                f"Cannot deactivate: {active_dependents} active user(s) are still assigned to this department."
            )
        dept.is_active = False
        dept.save(update_fields=['is_active'])
        log_audit(
            user_id=request.user.id, username=request.user.email,
            action_type='DEPARTMENT_DEACTIVATED', module='departments',
            entity_type='Department', entity_id=str(dept.id),
            after_values={'is_active': False},
        )

    def destroy(self, request, *args, **kwargs):
        dept = self.get_object()
        self._deactivate(request, dept)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        dept = self.get_object()
        self._deactivate(request, dept)
        return Response({'status': 'deactivated'})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        dept = self.get_object()
        dept.is_active = True
        dept.save(update_fields=['is_active'])
        log_audit(
            user_id=request.user.id, username=request.user.email,
            action_type='DEPARTMENT_ACTIVATED', module='departments',
            entity_type='Department', entity_id=str(dept.id),
            after_values={'is_active': True},
        )
        return Response({'status': 'activated'})


# ---------- Role ViewSet ----------
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    permission_classes = [IsAuthenticated, permission_required('roles.view')]

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
            user_id=self.request.user.id, username=self.request.user.email,
            action_type='ROLE_CREATED', module='roles',
            entity_type='Role', entity_id=str(role.id),
            after_values={'code': role.code, 'name': role.name},
        )

    def perform_update(self, serializer):
        old_perm_ids = set(serializer.instance.permissions.values_list('id', flat=True))
        role = serializer.save()
        new_perm_ids = set(role.permissions.values_list('id', flat=True))
        log_audit(
            user_id=self.request.user.id, username=self.request.user.email,
            action_type='ROLE_UPDATED', module='roles',
            entity_type='Role', entity_id=str(role.id),
            after_values={'name': role.name, 'is_active': role.is_active},
        )
        if old_perm_ids != new_perm_ids:
            log_audit(
                user_id=self.request.user.id, username=self.request.user.email,
                action_type='ROLE_PERMISSIONS_CHANGED', module='roles',
                entity_type='Role', entity_id=str(role.id),
                before_values={'permission_ids': sorted(old_perm_ids)},
                after_values={'permission_ids': sorted(new_perm_ids)},
            )

    def _deactivate(self, request, role):
        if role.code == 'sysadmin':
            if Employee.objects.filter(roles__code='sysadmin', is_active=True).exists():
                # Deactivating the role would strip every current sysadmin's
                # access at once — same failure mode as removing the last
                # admin's individual role assignment, just via a side door.
                raise ValidationError(
                    "Cannot deactivate the System Administrator role while active users hold it."
                )
        affected_users = role.users.filter(is_active=True).count()
        role.is_active = False
        role.save(update_fields=['is_active'])
        log_audit(
            user_id=request.user.id, username=request.user.email,
            action_type='ROLE_DEACTIVATED', module='roles',
            entity_type='Role', entity_id=str(role.id),
            after_values={'is_active': False, 'affected_active_users': affected_users},
        )
        return affected_users

    def destroy(self, request, *args, **kwargs):
        role = self.get_object()
        self._deactivate(request, role)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        role = self.get_object()
        affected_users = self._deactivate(request, role)
        return Response({'status': 'deactivated', 'affected_active_users': affected_users})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        role = self.get_object()
        role.is_active = True
        role.save(update_fields=['is_active'])
        log_audit(
            user_id=request.user.id, username=request.user.email,
            action_type='ROLE_ACTIVATED', module='roles',
            entity_type='Role', entity_id=str(role.id),
            after_values={'is_active': True},
        )
        return Response({'status': 'activated'})


# ---------- Permission ViewSet (read-only) ----------
class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.filter(is_active=True)
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, permission_required('permissions.view')]
