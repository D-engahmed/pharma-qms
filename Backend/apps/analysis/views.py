from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.common.mixins import AuditMixin
from apps.users.permissions import permission_required
from .models import Analysis
from .serializers import AnalysisSerializer

class AnalysisViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Analysis.objects.all().order_by('-created_at')
    serializer_class = AnalysisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, permission_required('analysis.start')]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, permission_required('analysis.submit_results')]
        else:
            self.permission_classes = [IsAuthenticated, permission_required('analysis.view')]
        return super().get_permissions()