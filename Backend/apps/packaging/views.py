from rest_framework import viewsets
from apps.common.mixins import AuditMixin
from apps.users.permissions import HasRolePermission
from .models import Packaging
from .serializers import PackagingSerializer

class PackagingViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Packaging.objects.all().order_by('-created_at')
    serializer_class = PackagingSerializer
    permission_classes = [HasRolePermission(['storekeeper', 'admin'])]