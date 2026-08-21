from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import AuditLog
from .serializers import AuditLogSerializer
from apps.users.permissions import permission_required

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    # permission_required(...) returns a class (DRF instantiates entries in
    # permission_classes itself via `permission()`). HasPermission('audit.view')
    # would already be an *instance*, which DRF then tries to call again and
    # raises TypeError: 'HasPermission' object is not callable.
    permission_classes = [IsAuthenticated, permission_required('audit.view')]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action_type', 'module', 'user_id']
    search_fields = ['username', 'entity_id']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']