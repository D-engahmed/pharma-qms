from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.common.mixins import AuditMixin
from apps.users.permissions import permission_required
from .models import Sample
from .serializers import SampleSerializer

class SampleViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Sample.objects.all().order_by('-created_at')
    serializer_class = SampleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, permission_required('sampling.create')]
        else:
            self.permission_classes = [IsAuthenticated, permission_required('sampling.view')]
        return super().get_permissions()