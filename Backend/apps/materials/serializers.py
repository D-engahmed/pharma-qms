from rest_framework import serializers
from .models import Material


class MaterialListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing materials"""
    class Meta:
        model = Material
        fields = [
            'id', 'receipt_id', 'material_name', 'category', 'supplier',
            'supplier_batch', 'receipt_date', 'total_qty', 'unit',
            'status', 'exp_date'
        ]


class MaterialDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail view"""
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.full_name', read_only=True)
    
    class Meta:
        model = Material
        fields = '__all__'
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'receipt_id',
            'qc_number', 'qc_sign', 'retest_date', 'released_date',
            'rejection_reason', 'rejected_by', 'rejected_at'
        ]


class MaterialCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating materials"""
    class Meta:
        model = Material
        fields = [
            'material_name', 'category', 'supplier', 'manufacturer',
            'country_origin', 'supplier_batch', 'mfg_date', 'exp_date',
            'batch_size', 'unit', 'package_type', 'num_packages',
            'package_size', 'total_qty', 'warehouse', 'location',
            'po_no', 'inv_no', 'receipt_date', 'received_by',
            'storage_condition'
        ]
    
    def create(self, validated_data):
        # Generate receipt_id
        import uuid
        receipt_id = f"RCP-{timezone.now().year}-{str(uuid.uuid4())[:8].upper()}"
        validated_data['receipt_id'] = receipt_id
        validated_data['status'] = Material.Status.QUARANTINE
        
        # Set created_by and updated_by
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        
        return super().create(validated_data)


class MaterialUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating materials (limited fields)"""
    class Meta:
        model = Material
        fields = [
            'material_name', 'category', 'manufacturer', 'country_origin',
            'warehouse', 'location', 'storage_condition'
        ]
    
    def update(self, instance, validated_data):
        # Check if material can be modified
        if instance.is_locked:
            raise serializers.ValidationError(
                "Cannot modify a locked material"
            )
        
        # Set updated_by
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['updated_by'] = request.user
        
        return super().update(instance, validated_data)


class SamplingRequestSerializer(serializers.Serializer):
    """Serializer for sampling request action"""
    pass  # No additional fields required


class ReleaseSerializer(serializers.Serializer):
    """Serializer for material release action"""
    qc_number = serializers.CharField(max_length=20)
    qc_sign = serializers.CharField(max_length=100)
    password = serializers.CharField(style={'input_type': 'password'})
    meaning = serializers.CharField(max_length=20, default='released')
    comment = serializers.CharField(required=False, allow_blank=True)


class RejectSerializer(serializers.Serializer):
    """Serializer for material rejection action"""
    reason = serializers.CharField(max_length=500)
    password = serializers.CharField(style={'input_type': 'password'})
    meaning = serializers.CharField(max_length=20, default='rejected')
    comment = serializers.CharField(required=False, allow_blank=True)