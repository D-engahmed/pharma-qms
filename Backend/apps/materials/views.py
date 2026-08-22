from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from apps.common.mixins import AuditMixin
from apps.users.permissions import permission_required, SegregationOfDuties
from apps.audit.services import log_audit
from apps.esignature.services import create_signature, verify_password
from apps.notifications.services import create_notification
from .models import Material
from .serializers import (
    MaterialListSerializer, MaterialDetailSerializer,
    MaterialCreateSerializer, MaterialUpdateSerializer,
    ReleaseSerializer, RejectSerializer
)


class MaterialViewSet(AuditMixin, viewsets.ModelViewSet):
    """ViewSet for Material with state machine workflow"""
    queryset = Material.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MaterialListSerializer
        elif self.action == 'retrieve':
            return MaterialDetailSerializer
        elif self.action == 'create':
            return MaterialCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MaterialUpdateSerializer
        return MaterialDetailSerializer
    
    def get_permissions(self):
        action_permission_map = {
            'list': 'receiving.view',
            'retrieve': 'receiving.view',
            'create': 'receiving.create',
            'update': 'receiving.edit',
            'partial_update': 'receiving.edit',
            'destroy': 'receiving.delete',
            'request_sampling': 'receiving.request_sampling',
            'mark_sampled': 'sampling.complete',
            'start_analysis': 'analysis.start',
            'submit_for_review': 'analysis.submit_results',
            'approve': 'review.approve',
            'reject': 'review.reject',
            'release': 'material.release',
        }
        required_permission = action_permission_map.get(self.action, 'receiving.view')
        
        # Add segregation of duties for approval/rejection actions
        if self.action in ['approve', 'reject', 'release']:
            self.permission_classes = [
                IsAuthenticated,
                permission_required(required_permission),
                SegregationOfDuties
            ]
        else:
            self.permission_classes = [
                IsAuthenticated,
                permission_required(required_permission)
            ]
        
        return super().get_permissions()
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def request_sampling(self, request, pk=None):
        """Request sampling for material"""
        material = self.get_object()
        
        try:
            material.request_sampling(by_user=request.user)
            material.save()
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_409_CONFLICT
            )
        
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='MATERIAL_SAMPLING_REQUESTED',
            module='materials',
            entity_type='Material',
            entity_id=str(material.id),
            after_values={'status': material.status},
            ip_address=getattr(request, 'audit_ip', None),
            session_id=getattr(request, 'audit_session', ''),
            description=f"Sampling requested for {material.receipt_id}"
        )
        
        # Create notification for samplers
        create_notification(
            target_role='sampler',
            title=f'Sampling Requested: {material.material_name}',
            message=f'Receipt ID: {material.receipt_id} · Material: {material.material_name}'
        )
        
        return Response({
            'status': 'success',
            'message': 'Sampling requested',
            'material': MaterialDetailSerializer(material).data
        })
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def mark_sampled(self, request, pk=None):
        """Mark material as sampled"""
        material = self.get_object()
        
        try:
            material.mark_sampled(by_user=request.user)
            material.save()
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_409_CONFLICT
            )
        
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='MATERIAL_SAMPLED',
            module='materials',
            entity_type='Material',
            entity_id=str(material.id),
            after_values={'status': material.status},
            ip_address=getattr(request, 'audit_ip', None),
            session_id=getattr(request, 'audit_session', ''),
            description=f"Material {material.receipt_id} marked as sampled"
        )
        
        return Response({
            'status': 'success',
            'message': 'Material marked as sampled',
            'material': MaterialDetailSerializer(material).data
        })
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def start_analysis(self, request, pk=None):
        """Start analysis of material"""
        material = self.get_object()
        
        try:
            material.start_analysis(by_user=request.user)
            material.save()
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_409_CONFLICT
            )
        
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='MATERIAL_UNDER_ANALYSIS',
            module='materials',
            entity_type='Material',
            entity_id=str(material.id),
            after_values={'status': material.status},
            ip_address=getattr(request, 'audit_ip', None),
            session_id=getattr(request, 'audit_session', ''),
            description=f"Analysis started for {material.receipt_id}"
        )
        
        return Response({
            'status': 'success',
            'message': 'Analysis started',
            'material': MaterialDetailSerializer(material).data
        })
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def submit_for_review(self, request, pk=None):
        """Submit material for review"""
        material = self.get_object()
        
        try:
            material.submit_for_review(by_user=request.user)
            material.save()
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_409_CONFLICT
            )
        
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='MATERIAL_UNDER_REVIEW',
            module='materials',
            entity_type='Material',
            entity_id=str(material.id),
            after_values={'status': material.status},
            ip_address=getattr(request, 'audit_ip', None),
            session_id=getattr(request, 'audit_session', ''),
            description=f"Material {material.receipt_id} submitted for review"
        )
        
        # Create notification for supervisors
        create_notification(
            target_role='qc_supervisor',
            title=f'Review Required: {material.material_name}',
            message=f'Receipt ID: {material.receipt_id} · Material ready for review'
        )
        
        return Response({
            'status': 'success',
            'message': 'Material submitted for review',
            'material': MaterialDetailSerializer(material).data
        })
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def approve(self, request, pk=None):
        """Approve material after review (requires e-signature)"""
        material = self.get_object()
        
        # Verify e-signature
        password = request.data.get('password')
        if not password or not verify_password(request.user, password):
            log_audit(
                user_id=request.user.id,
                username=request.user.email,
                action_type='ESIGNATURE_FAILED',
                module='materials',
                entity_type='Material',
                entity_id=str(material.id),
                ip_address=getattr(request, 'audit_ip', None),
                session_id=getattr(request, 'audit_session', ''),
                description=f"E-signature failed for approval of {material.receipt_id}"
            )
            return Response(
                {'error': 'Invalid password for e-signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            material.approve(by_user=request.user)
            material.save()
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_409_CONFLICT
            )
        
        # Create e-signature record
        create_signature(
            signer=request.user,
            meaning='approved',
            record_type='Material',
            record_id=material.id,
            comment=request.data.get('comment', ''),
            record_data={
                'receipt_id': material.receipt_id,
                'material_name': material.material_name,
                'status': material.status
            }
        )
        
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='MATERIAL_APPROVED',
            module='materials',
            entity_type='Material',
            entity_id=str(material.id),
            after_values={'status': material.status},
            ip_address=getattr(request, 'audit_ip', None),
            session_id=getattr(request, 'audit_session', ''),
            description=f"Material {material.receipt_id} approved"
        )
        
        return Response({
            'status': 'success',
            'message': 'Material approved',
            'material': MaterialDetailSerializer(material).data
        })
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def reject(self, request, pk=None):
        """Reject material (requires e-signature)"""
        material = self.get_object()
        
        serializer = RejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verify e-signature
        password = serializer.validated_data['password']
        if not verify_password(request.user, password):
            log_audit(
                user_id=request.user.id,
                username=request.user.email,
                action_type='ESIGNATURE_FAILED',
                module='materials',
                entity_type='Material',
                entity_id=str(material.id),
                ip_address=getattr(request, 'audit_ip', None),
                session_id=getattr(request, 'audit_session', ''),
                description=f"E-signature failed for rejection of {material.receipt_id}"
            )
            return Response(
                {'error': 'Invalid password for e-signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            material.reject(
                by_user=request.user,
                reason=serializer.validated_data['reason']
            )
            material.save()
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_409_CONFLICT
            )
        
        # Create e-signature record
        create_signature(
            signer=request.user,
            meaning='rejected',
            record_type='Material',
            record_id=material.id,
            comment=serializer.validated_data.get('comment', ''),
            record_data={
                'receipt_id': material.receipt_id,
                'material_name': material.material_name,
                'status': material.status,
                'rejection_reason': material.rejection_reason
            }
        )
        
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='MATERIAL_REJECTED',
            module='materials',
            entity_type='Material',
            entity_id=str(material.id),
            after_values={
                'status': material.status,
                'rejection_reason': material.rejection_reason
            },
            ip_address=getattr(request, 'audit_ip', None),
            session_id=getattr(request, 'audit_session', ''),
            description=f"Material {material.receipt_id} rejected: {material.rejection_reason}"
        )
        
        # Create notification
        create_notification(
            target_role='storekeeper',
            title=f'Material Rejected: {material.material_name}',
            message=f'Receipt ID: {material.receipt_id} · Reason: {material.rejection_reason}'
        )
        
        return Response({
            'status': 'success',
            'message': 'Material rejected',
            'material': MaterialDetailSerializer(material).data
        })
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def release(self, request, pk=None):
        """Release material (requires e-signature)"""
        material = self.get_object()
        
        serializer = ReleaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verify e-signature
        password = serializer.validated_data['password']
        if not verify_password(request.user, password):
            log_audit(
                user_id=request.user.id,
                username=request.user.email,
                action_type='ESIGNATURE_FAILED',
                module='materials',
                entity_type='Material',
                entity_id=str(material.id),
                ip_address=getattr(request, 'audit_ip', None),
                session_id=getattr(request, 'audit_session', ''),
                description=f"E-signature failed for release of {material.receipt_id}"
            )
            return Response(
                {'error': 'Invalid password for e-signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            material.release(
                by_user=request.user,
                qc_number=serializer.validated_data['qc_number'],
                qc_sign=serializer.validated_data['qc_sign']
            )
            material.save()
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_409_CONFLICT
            )
        
        # Create e-signature record
        create_signature(
            signer=request.user,
            meaning='released',
            record_type='Material',
            record_id=material.id,
            comment=serializer.validated_data.get('comment', ''),
            record_data={
                'receipt_id': material.receipt_id,
                'material_name': material.material_name,
                'status': material.status,
                'qc_number': material.qc_number,
                'retest_date': material.retest_date.isoformat()
            }
        )
        
        log_audit(
            user_id=request.user.id,
            username=request.user.email,
            action_type='MATERIAL_RELEASED',
            module='materials',
            entity_type='Material',
            entity_id=str(material.id),
            after_values={
                'status': material.status,
                'qc_number': material.qc_number,
                'retest_date': material.retest_date.isoformat()
            },
            ip_address=getattr(request, 'audit_ip', None),
            session_id=getattr(request, 'audit_session', ''),
            description=f"Material {material.receipt_id} released with QC {material.qc_number}"
        )
        
        # Create notification for storekeepers
        create_notification(
            target_role='storekeeper',
            title=f'Material Released: {material.material_name}',
            message=f'Receipt ID: {material.receipt_id} · QC No: {material.qc_number} · Retest by: {material.retest_date.strftime("%d/%m/%Y")}'
        )
        
        return Response({
            'status': 'success',
            'message': 'Material released',
            'material': MaterialDetailSerializer(material).data
        })
    
    @action(detail=True, methods=['get'])
    def label(self, request, pk=None):
        """Get release label data for printing"""
        material = self.get_object()
        
        if material.status != Material.Status.RELEASED:
            return Response(
                {'error': 'Release label is only available for released materials.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        label_data = {
            'receipt_id': material.receipt_id,
            'material_name': material.material_name,
            'batch_no': material.supplier_batch,
            'batch_size': f"{material.batch_size or ''} {material.unit or ''}".strip(),
            'supplier': material.supplier,
            'mfg_date': material.mfg_date.strftime('%d/%m/%Y') if material.mfg_date else '—',
            'exp_date': material.exp_date.strftime('%d/%m/%Y') if material.exp_date else '—',
            'qc_number': material.qc_number or '—',
            'storage_condition': material.storage_condition or '—',
            'retest_date': material.retest_date.strftime('%d/%m/%Y') if material.retest_date else '—',
            'qc_sign': material.qc_sign or '—',
            'release_date': material.released_date.strftime('%d/%m/%Y') if material.released_date else '—',
        }
        
        return Response(label_data)