from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.common.mixins import AuditMixin
from apps.users.permissions import permission_required, SegregationOfDuties
from apps.esignature.services import create_signature, verify_password
from .models import COA
from .serializers import COASerializer
import uuid
from django.utils import timezone

class COAViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = COA.objects.all().order_by('-created_at')
    serializer_class = COASerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, permission_required('certificate.create')]
        elif self.action == 'submit_for_review':
            self.permission_classes = [IsAuthenticated, permission_required('certificate.submit_for_review')]
        elif self.action in ['approve', 'reject']:
            self.permission_classes = [IsAuthenticated, permission_required('certificate.approve'), SegregationOfDuties]
        elif self.action == 'lock':
            self.permission_classes = [IsAuthenticated, permission_required('certificate.lock')]
        else:
            self.permission_classes = [IsAuthenticated, permission_required('certificate.view')]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        coa_id = f"COA-{timezone.now().year}-{str(uuid.uuid4())[:8].upper()}"
        serializer.save(coa_id=coa_id)
    
    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        coa = self.get_object()
        if coa.status != 'DRAFT':
            return Response({'error': 'Only Draft COAs can be submitted'}, status=400)
        coa.status = 'IN_REVIEW'
        coa.save()
        return Response({'status': 'success'})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        coa = self.get_object()
        if not verify_password(request.user, request.data.get('password')):
            return Response({'error': 'Invalid password'}, status=401)
        coa.status = 'APPROVED'
        coa.approved_by = request.user
        coa.approved_at = timezone.now()
        coa.save()
        create_signature(signer=request.user, meaning='approved', record_type='COA', record_id=coa.coa_id)
        return Response({'status': 'success'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        coa = self.get_object()
        if not verify_password(request.user, request.data.get('password')):
            return Response({'error': 'Invalid password'}, status=401)
        coa.status = 'REJECTED'
        coa.rejection_reason = request.data.get('reason', '')
        coa.save()
        create_signature(signer=request.user, meaning='rejected', record_type='COA', record_id=coa.coa_id)
        return Response({'status': 'success'})
    
    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        coa = self.get_object()
        if coa.status != 'APPROVED':
            return Response({'error': 'Only Approved COAs can be locked'}, status=400)
        coa.status = 'LOCKED'
        coa.save()
        return Response({'status': 'success'})