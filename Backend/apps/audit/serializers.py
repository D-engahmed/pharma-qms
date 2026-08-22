from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog with null-safe user fields"""
    user_email = serializers.SerializerMethodField()
    user_full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'timestamp', 'user', 'user_email', 'user_full_name',
            'username', 'action_type', 'module', 'entity_type', 'entity_id',
            'before_values', 'after_values', 'ip_address', 'session_id',
            'user_agent', 'description'
        ]
        read_only_fields = fields
    
    def get_user_email(self, obj):
        return obj.user.email if obj.user_id else None
    
    def get_user_full_name(self, obj):
        if not obj.user_id:
            return obj.username
        return obj.user.full_name if obj.user else obj.username