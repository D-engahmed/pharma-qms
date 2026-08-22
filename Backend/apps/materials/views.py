from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from apps.common.mixins import AuditMixin
from apps.users.permissions import permission_required, SegregationOfDuties
from apps.audit.services import log_audit
from apps.esignature.services import create_signature, verify_password
from .models import Material
from .serializers import MaterialSerializer, MaterialCreateSerializer

class MaterialViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Material.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MaterialCreateSerializer
        return MaterialSerializer
    
    def get_permissions(self):
        action_map = {
            'list': 'receiving.view', 'retrieve': 'receiving.view', 'create': 'receiving.create',
            'update': 'receiving.edit', 'partial_update': 'receiving.edit', 'destroy': 'receiving.delete',
            'request_sampling': 'receiving.request_sampling', 'mark_sampled': 'sampling.complete',
            'start_analysis': 'analysis.start', 'submit_for_review': 'analysis.submit_results',
            'approve': 'review.approve', 'reject': 'review.reject', 'release': 'material.release'
        }
        perm = action_map.get(self.action, 'receiving.view')
        if self.action in ['approve', 'reject', 'release']:
            self.permission_classes = [IsAuthenticated, permission_required(perm), SegregationOfDuties]
        else:
            self.permission_classes = [IsAuthenticated, permission_required(perm)]
        return super().get_permissions()
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def request_sampling(self, request, pk=None):
        material = self.get_object()
        try:
            material.request_sampling(by_user=request.user)
            material.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)
        return Response({'status': 'success', 'material': MaterialSerializer(material).data})
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def mark_sampled(self, request, pk=None):
        material = self.get_object()
        try:
            material.mark_sampled(by_user=request.user)
            material.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)
        return Response({'status': 'success', 'material': MaterialSerializer(material).data})
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def start_analysis(self, request, pk=None):
        material = self.get_object()
        try:
            material.start_analysis(by_user=request.user)
            material.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)
        return Response({'status': 'success', 'material': MaterialSerializer(material).data})
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def submit_for_review(self, request, pk=None):
        material = self.get_object()
        try:
            material.submit_for_review(by_user=request.user)
            material.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)
        return Response({'status': 'success', 'material': MaterialSerializer(material).data})
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def approve(self, request, pk=None):
        material = self.get_object()
        password = request.data.get('password')
        if not verify_password(request.user, password):
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            material.approve(by_user=request.user)
            material.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)
        create_signature(signer=request.user, meaning='approved', record_type='Material', record_id=material.id)
        return Response({'status': 'success', 'material': MaterialSerializer(material).data})
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def reject(self, request, pk=None):
        material = self.get_object()
        password = request.data.get('password')
        if not verify_password(request.user, password):
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
        reason = request.data.get('reason', '')
        try:
            material.reject(by_user=request.user, reason=reason)
            material.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)
        create_signature(signer=request.user, meaning='rejected', record_type='Material', record_id=material.id, comment=reason)
        return Response({'status': 'success', 'material': MaterialSerializer(material).data})
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def release(self, request, pk=None):
        material = self.get_object()
        password = request.data.get('password')
        if not verify_password(request.user, password):
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
        qc_number = request.data.get('qc_number')
        qc_sign = request.data.get('qc_sign')
        try:
            material.release(by_user=request.user, qc_number=qc_number, qc_sign=qc_sign)
            material.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)
        create_signature(signer=request.user, meaning='released', record_type='Material', record_id=material.id)
        return Response({'status': 'success', 'material': MaterialSerializer(material).data})