from rest_framework import serializers
from .models import Material

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'receipt_id', 'qc_number', 'qc_sign', 'retest_date', 'released_date', 'rejection_reason', 'rejected_by', 'rejected_at']

class MaterialCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['material_name', 'supplier', 'supplier_batch', 'exp_date', 'receipt_date', 'received_by']
    
    def create(self, validated_data):
        import uuid
        from django.utils import timezone
        receipt_id = f"RCP-{timezone.now().year}-{str(uuid.uuid4())[:8].upper()}"
        validated_data['receipt_id'] = receipt_id
        validated_data['status'] = Material.Status.QUARANTINE
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        return super().create(validated_data)