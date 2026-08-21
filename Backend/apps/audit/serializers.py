from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    # SerializerMethodFields instead of source='user.email' / 'user.full_name':
    # AuditLog.user is nullable (e.g. LOGIN_FAILURE rows have no user), and
    # DRF's dotted-source traversal does getattr(None, 'email') in that case,
    # which raises AttributeError rather than resolving to None.
    user_email = serializers.SerializerMethodField()
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['id', 'timestamp', 'user', 'user_email', 'user_full_name']

    def get_user_email(self, obj):
        return obj.user.email if obj.user_id else None

    def get_user_full_name(self, obj):
        # `username` is the point-in-time snapshot taken when the log entry
        # was created, so it's a meaningful fallback even after the user
        # record changes or is deleted (see AuditLog.user's on_delete).
        if not obj.user_id:
            return None
        full_name = getattr(obj.user, 'full_name_prop', '') or obj.user.full_name
        return full_name or obj.username