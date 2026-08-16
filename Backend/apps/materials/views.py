from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils.timezone import now
from datetime import timedelta

from apps.common.mixins import AuditMixin
from apps.users.permissions import HasPermission
from apps.audit.services import log_audit
from apps.notifications.services import create_notification

from .models import Material
from .serializers import MaterialSerializer, MaterialListSerializer, MaterialDetailSerializer

class MaterialViewSet(AuditMixin, viewsets.ModelViewSet):
    """
    ViewSet for Material (Raw Material) CRUD and custom actions.
    Permissions are enforced per action using the new permission system.
    """
    queryset = Material.objects.all().order_by('-created_at')
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]  # Base permission; refined in get_permissions

    # ---------- Action-specific permissions ----------
    def get_permissions(self):
        """
        Assign different permissions based on the action.
        """
        if self.action == 'list':
            self.permission_classes = [IsAuthenticated, HasPermission('receiving.view')]
        elif self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated, HasPermission('receiving.view')]
        elif self.action == 'create':
            self.permission_classes = [IsAuthenticated, HasPermission('receiving.create')]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, HasPermission('receiving.edit')]
        elif self.action == 'destroy':
            # Usually we don't delete materials; we soft-deactivate or handle via status.
            # For now, allow only admin to delete (if needed)
            self.permission_classes = [IsAuthenticated, HasPermission('receiving.edit')]
        elif self.action == 'request_sampling':
            self.permission_classes = [IsAuthenticated, HasPermission('receiving.request_sampling')]
        elif self.action == 'release':
            self.permission_classes = [IsAuthenticated, HasPermission('material.release')]
        else:
            self.permission_classes = [IsAuthenticated, HasPermission('receiving.view')]
        return super().get_permissions()

    # ---------- Serializer selection ----------
    def get_serializer_class(self):
        if self.action == 'list':
            return MaterialListSerializer
        elif self.action == 'retrieve':
            return MaterialDetailSerializer
        return MaterialSerializer

    # ---------- AuditMixin overrides (for audit logging) ----------
    # The AuditMixin already logs CREATE, UPDATE, DELETE via signals.
    # We override perform_create/update/destroy to include additional fields.

    def perform_create(self, serializer):
        # Auto-generate receipt_id if not provided (should be generated in serializer)
        # The serializer handles receipt_id generation; we just ensure it's set.
        instance = serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
            status=Material.Status.QUARANTINE,
            sampling_status=Material.SamplingStatus.NOT_SAMPLED
        )
        # Audit log is automatically triggered by AuditMixin.
        # We can add extra logging if needed.
        # But AuditMixin's perform_create already calls _log_audit.
        # So we just call super to let the mixin handle it.
        super().perform_create(serializer)

    def perform_update(self, serializer):
        # Ensure updated_by is set
        serializer.save(updated_by=self.request.user)
        super().perform_update(serializer)

    # ---------- Custom Actions ----------

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def request_sampling(self, request, pk=None):
        """
        Request sampling for a material.
        Changes sampling_status to 'Sampling Requested'.
        """
        material = self.get_object()

        # Business rule: only allowed if currently 'Not Sampled'
        if material.sampling_status != Material.SamplingStatus.NOT_SAMPLED:
            return Response(
                {'error': f'Sampling already {material.sampling_status.lower()}'},
                status=status.HTTP_409_CONFLICT
            )

        # Update status
        material.sampling_status = Material.SamplingStatus.SAMPLING_REQUESTED
        material.updated_by = request.user
        material.save()

        # Audit log (AuditMixin will also log, but we want a specific entry)
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='RECEIVING_SAMPLING_REQUESTED',
            module='receiving',
            entity_type='Material',
            entity_id=str(material.id),
            after_values={'sampling_status': 'Sampling Requested'},
            description=f"Sampling requested for {material.receipt_id}"
        )

        return Response({
            'status': 'Sampling requested',
            'material': MaterialDetailSerializer(material).data
        })

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def release(self, request, pk=None):
        """
        Release a material (QC release). Requires qc_number and qc_sign.
        Sets status to Released, calculates retest_date, and notifies storekeeper.
        """
        material = self.get_object()

        # Business rule: only quarantine materials can be released
        if material.status != Material.Status.QUARANTINE:
            return Response(
                {'error': 'Material is not in quarantine; cannot release.'},
                status=status.HTTP_409_CONFLICT
            )

        # Validate required fields
        qc_number = request.data.get('qc_number')
        qc_sign = request.data.get('qc_sign')
        if not qc_number or not qc_sign:
            return Response(
                {'error': 'QC number and signature are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate retest date (release date + 1 year)
        release_date = now().date()
        retest_date = release_date + timedelta(days=365)

        # Update material
        material.status = Material.Status.RELEASED
        material.qc_number = qc_number
        material.qc_sign = qc_sign
        material.released_date = release_date
        material.retest_date = retest_date
        material.updated_by = request.user
        material.save()

        # Audit log
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='MATERIAL_RELEASED',
            module='material',
            entity_type='Material',
            entity_id=str(material.id),
            after_values={
                'status': 'Released',
                'qc_number': qc_number,
                'retest_date': retest_date.isoformat()
            },
            description=f"Material {material.receipt_id} released with QC {qc_number}"
        )

        # Create notification for storekeepers
        create_notification(
            target_role='storekeeper',
            title=f'Material Released: {material.material_name}',
            message=f'Receipt ID: {material.receipt_id} · QC No: {qc_number} · Retest by: {retest_date.strftime("%d/%m/%Y")}'
        )

        return Response({
            'status': 'Material released',
            'material': MaterialDetailSerializer(material).data
        })

    @action(detail=True, methods=['get'])
    def label(self, request, pk=None):
        """
        Get release label data for printing.
        Only available for Released materials.
        """
        material = self.get_object()

        if material.status != Material.Status.RELEASED:
            return Response(
                {'error': 'Release label is only available for released materials.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Find the associated sample (if any) to get container number and storage condition
        sample = material.samples.first()  # assuming a related_name 'samples' on Sample.material
        label_data = {
            'receipt_id': material.receipt_id,
            'material_name': material.material_name,
            'batch_no': material.supplier_batch,
            'batch_size': f"{material.batch_size or ''} {material.unit or ''}".strip(),
            'supplier': material.supplier,
            'mfg_date': material.mfg_date.strftime('%d/%m/%Y') if material.mfg_date else '—',
            'exp_date': material.exp_date.strftime('%d/%m/%Y') if material.exp_date else '—',
            'container_no': sample.containers if sample else '—',
            'qc_number': material.qc_number or '—',
            'storage_condition': sample.storage if sample else material.storage_condition or '—',
            'retest_date': material.retest_date.strftime('%d/%m/%Y') if material.retest_date else '—',
            'qc_sign': material.qc_sign or '—',
            'release_date': material.released_date.strftime('%d/%m/%Y') if material.released_date else '—',
        }
        return Response(label_data)