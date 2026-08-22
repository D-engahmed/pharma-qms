from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
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

    # PROJECT_RULES.md #4/#18: decided COAs must stay immutable. There's no
    # separate "Locked" status yet (see note below), so Approved/Rejected
    # double as the locked states for now.
    FINALIZED_STATUSES = {'Approved', 'Rejected'}

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated, permission_required('certificate.view')]
        elif self.action == 'create':
            self.permission_classes = [IsAuthenticated, permission_required('certificate.create')]
        elif self.action in ['update', 'partial_update']:
            # Editing a draft is part of authoring it — reuse certificate.create
            # rather than inventing a certificate.edit code, since that's the
            # permission qc_analyst already holds (seed_initial_data.py) and no
            # role has ever been granted anything narrower.
            self.permission_classes = [IsAuthenticated, permission_required('certificate.create')]
        elif self.action == 'destroy':
            # NEW permission code — not yet in seed_initial_data.py's
            # permissions_data list or any role's permission list. Add
            # ('certificate.delete', 'Delete Certificate', 'certificate')
            # and grant it deliberately (probably sysadmin only) before this
            # action is reachable by anyone.
            self.permission_classes = [IsAuthenticated, permission_required('certificate.delete')]
        elif self.action == 'submit':
            self.permission_classes = [IsAuthenticated, permission_required('certificate.submit_for_review')]
        elif self.action == 'complete':
            self.permission_classes = [IsAuthenticated, permission_required('certificate.review')]
        elif self.action in ['approve', 'reject']:
            self.permission_classes = [IsAuthenticated, permission_required('certificate.approve')]
        else:
            self.permission_classes = [IsAuthenticated, permission_required('certificate.view')]
        return super().get_permissions()

    # ---------- Immutability guards ----------
    # get_permissions() above only checks *who* may call update/destroy.
    # These check *when* it's still allowed at all, regardless of who's
    # asking. Previously missing entirely: an Approved or Rejected COA could
    # be edited or deleted by anyone holding certificate.view, because
    # update/partial_update/destroy fell through to the view-only branch.

    def perform_update(self, serializer):
        if serializer.instance.status in self.FINALIZED_STATUSES:
            raise ValidationError(
                f"Cannot modify a COA that has been {serializer.instance.status.lower()}."
            )
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.status != 'Draft':
            raise ValidationError(
                "Only Draft COAs can be deleted. "
                f"'{instance.status}' certificates are quality records — reject them, don't remove them."
            )
        super().perform_destroy(instance)

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