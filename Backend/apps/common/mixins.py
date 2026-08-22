from django.utils import timezone
from apps.audit.services import log_audit


class AuditMixin:
    """Mixin to add audit logging to viewsets"""
    
    def perform_create(self, serializer):
        instance = serializer.save()
        self._log_audit('CREATE', instance)
    
    def perform_update(self, serializer):
        old = self.get_object()
        instance = serializer.save()
        self._log_audit('UPDATE', instance, old)
    
    def perform_destroy(self, instance):
        self._log_audit('DELETE', instance)
        instance.delete()
    
    def _log_audit(self, action, instance, old=None):
        user = self.request.user
        changes = None
        
        if old:
            changes = {}
            for field in old._meta.fields:
                old_val = getattr(old, field.name)
                new_val = getattr(instance, field.name)
                if old_val != new_val:
                    changes[field.name] = [str(old_val), str(new_val)]
        
        log_audit(
            user_id=user.id if user.is_authenticated else None,
            username=user.email if user.is_authenticated else 'anonymous',
            action_type=f"{instance.__class__.__name__.upper()}_{action}D",
            module=instance.__class__.__name__.lower(),
            entity_type=instance.__class__.__name__,
            entity_id=str(instance.id),
            before_values=changes if changes else None,
            after_values=self._get_instance_data(instance) if action != 'DELETE' else None,
            ip_address=getattr(self.request, 'audit_ip', None),
            session_id=getattr(self.request, 'audit_session', '') or '',
            description=f"{action} {instance.__class__.__name__}"
        )
    
    def _get_instance_data(self, instance):
        """Get instance data for audit logging"""
        data = {}
        for field in instance._meta.fields:
            val = getattr(instance, field.name)
            if val is not None:
                data[field.name] = str(val)
        return data