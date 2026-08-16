# apps/materials/serializers.py
from rest_framework import serializers
from .models import Material

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'receipt_id']

class MaterialListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing materials."""
    class Meta:
        model = Material
        fields = [
            'id', 'receipt_id', 'material_name', 'category', 'supplier',
            'supplier_batch', 'receipt_date', 'total_qty', 'unit',
            'status', 'sampling_status', 'exp_date'
        ]

class MaterialDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail view."""
    class Meta:
        model = Material
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'receipt_id']