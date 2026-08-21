from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from apps.common.mixins import AuditMixin
from apps.users.permissions import permission_required
from apps.audit.services import log_audit
from apps.esignature.models import ElectronicSignature
from apps.esignature.services import create_signature
from .models import COA
from .serializers import COASerializer

class COAViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = COA.objects.all().order_by('-created_at')
    serializer_class = COASerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated, permission_required('certificate.view')]
        elif self.action == 'create':
            self.permission_classes = [IsAuthenticated, permission_required('certificate.create')]
        elif self.action == 'submit':
            self.permission_classes = [IsAuthenticated, permission_required('certificate.submit_for_review')]
        elif self.action == 'complete':
            self.permission_classes = [IsAuthenticated, permission_required('certificate.review')]
        elif self.action in ['approve', 'reject']:
            self.permission_classes = [IsAuthenticated, permission_required('certificate.approve')]
        else:
            self.permission_classes = [IsAuthenticated, permission_required('certificate.view')]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        coa = self.get_object()
        if coa.status != 'Draft':
            return Response({'error': 'Only Draft COAs can be submitted'}, status=400)
        coa.status = 'In Progress'
        coa.updated_by = request.user
        coa.save()
        return Response({'status': 'Submitted'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        coa = self.get_object()
        if coa.status != 'In Progress':
            return Response({'error': 'Only In Progress COAs can be completed'}, status=400)
        coa.status = 'Completed'
        coa.updated_by = request.user
        coa.save()
        return Response({'status': 'Completed'})

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        coa = self.get_object()
        if coa.status != 'Completed':
            return Response({'error': 'Only Completed COAs can be approved'}, status=400)
        # Require electronic signature (password re-entry)
        password = request.data.get('password')
        if not password or not request.user.check_password(password):
            return Response({'error': 'Invalid password'}, status=401)
        coa.status = 'Approved'
        coa.qc_comment = request.data.get('comment', '')
        coa.updated_by = request.user
        coa.save()
        # Create signature record
        create_signature(
            signer=request.user,
            meaning='approved',
            record_type='COA',
            record_id=coa.id,
            comment=coa.qc_comment,
        )
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='CERTIFICATE_APPROVED',
            module='certificate',
            entity_type='COA',
            entity_id=coa.id,
            after_values={'status': 'Approved'}
        )
        return Response({'status': 'Approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        coa = self.get_object()
        if coa.status != 'Completed':
            return Response({'error': 'Only Completed COAs can be rejected'}, status=400)
        password = request.data.get('password')
        if not password or not request.user.check_password(password):
            return Response({'error': 'Invalid password'}, status=401)
        coa.status = 'Rejected'
        coa.qc_comment = request.data.get('comment', '')
        coa.updated_by = request.user
        coa.save()
        if coa.material:
            coa.material.status = 'Rejected'
            coa.material.updated_by = request.user
            coa.material.save()
        create_signature(
            signer=request.user,
            meaning='rejected',
            record_type='COA',
            record_id=coa.id,
            comment=coa.qc_comment,
        )
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='CERTIFICATE_REJECTED',
            module='certificate',
            entity_type='COA',
            entity_id=coa.id,
            after_values={'status': 'Rejected'}
        )
        return Response({'status': 'Rejected'})