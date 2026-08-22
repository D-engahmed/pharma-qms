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
from .models import Employee, Department, Role, Permission
from .serializers import EmployeeSerializer, EmployeeCreateSerializer, LoginSerializer, DepartmentSerializer, RoleSerializer, PermissionSerializer
from .permissions import permission_required
from apps.audit.services import log_audit
from apps.session.models import UserSession

def get_client_ip(request):
    return request.META.get('REMOTE_ADDR')

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].lower()
        password = serializer.validated_data['password']
        
        try:
            user = Employee.objects.get(email__iexact=email)
        except Employee.DoesNotExist:
            log_audit(user_id=None, username=email, action_type='LOGIN_FAILURE', module='auth', ip_address=get_client_ip(request), description='Invalid credentials')
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.is_locked():
            return Response({'error': 'Account locked'}, status=status.HTTP_403_FORBIDDEN)
            
        if not user.is_active:
            return Response({'error': 'Account inactive'}, status=status.HTTP_403_FORBIDDEN)
            
        authenticated_user = authenticate(request, username=email, password=password)
        if authenticated_user is None:
            user.increment_failed_login()
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
        active_session = UserSession.objects.filter(user=authenticated_user, revoked_at__isnull=True, expires_at__gt=timezone.now()).first()
        if active_session:
            return Response({'error': 'Concurrent session detected'}, status=status.HTTP_403_FORBIDDEN)
            
        login(request, authenticated_user)
        user.reset_failed_login()
        user.last_login = timezone.now()
        user.save(update_fields=['failed_login_count', 'locked_until', 'last_login'])
        
        request.session.create()
        UserSession.objects.create(
            user=authenticated_user,
            session_key=request.session.session_key,
            expires_at=timezone.now() + timedelta(seconds=settings.SESSION_COOKIE_AGE),
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        log_audit(user_id=authenticated_user.id, username=authenticated_user.email, action_type='LOGIN_SUCCESS', module='auth', ip_address=get_client_ip(request), description='Login successful')
        
        return Response({
            'user': EmployeeSerializer(authenticated_user).data,
            'csrf_token': get_token(request),
            'redirect_url': '/dashboard/'
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            user_session = UserSession.objects.get(session_key=request.session.session_key)
            user_session.revoked_at = timezone.now()
            user_session.save()
        except UserSession.DoesNotExist:
            pass
        logout(request)
        return Response({'message': 'Logged out'})

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(EmployeeSerializer(request.user).data)

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('-created_at')
    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeCreateSerializer
        return EmployeeSerializer
    def get_permissions(self):
        action_map = {'create': 'users.create', 'update': 'users.edit', 'partial_update': 'users.edit', 'destroy': 'users.deactivate'}
        perm = action_map.get(self.action, 'users.view')
        self.permission_classes = [IsAuthenticated, permission_required(perm)]
        return super().get_permissions()

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    def get_permissions(self):
        action_map = {'create': 'departments.create', 'update': 'departments.edit', 'partial_update': 'departments.edit', 'destroy': 'departments.deactivate'}
        perm = action_map.get(self.action, 'departments.view')
        self.permission_classes = [IsAuthenticated, permission_required(perm)]
        return super().get_permissions()

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    def get_permissions(self):
        action_map = {'create': 'roles.create', 'update': 'roles.edit', 'partial_update': 'roles.edit', 'destroy': 'roles.deactivate'}
        perm = action_map.get(self.action, 'roles.view')
        self.permission_classes = [IsAuthenticated, permission_required(perm)]
        return super().get_permissions()

class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.filter(is_active=True)
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, permission_required('permissions.view')]