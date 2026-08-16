from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.common.mixins import AuditMixin
from apps.users.permissions import HasPermission
from .models import ProductSample
from .serializers import ProductSampleSerializer

class ProductSampleViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = ProductSample.objects.all().order_by('-created_at')
    serializer_class = ProductSampleSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated, HasPermission('sampling.view')]
        elif self.action == 'create':
            self.permission_classes = [IsAuthenticated, HasPermission('sampling.create')]
        else:
            self.permission_classes = [IsAuthenticated, HasPermission('sampling.view')]
        return super().get_permissions()