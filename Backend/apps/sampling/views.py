from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.common.mixins import AuditMixin
from apps.users.permissions import HasPermission
from .models import Sample
from .serializers import SampleSerializer

class SampleViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Sample.objects.all().order_by('-created_at')
    serializer_class = SampleSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated, HasPermission('sampling.view')]
        elif self.action == 'create':
            self.permission_classes = [IsAuthenticated, HasPermission('sampling.create')]
        elif self.action == 'complete_sample':
            self.permission_classes = [IsAuthenticated, HasPermission('sampling.complete')]
        else:
            self.permission_classes = [IsAuthenticated, HasPermission('sampling.view')]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def complete_sample(self, request, pk=None):
        sample = self.get_object()
        sample.testing_status = 'Completed'
        sample.save()
        return Response({'status': 'Sample completed'})