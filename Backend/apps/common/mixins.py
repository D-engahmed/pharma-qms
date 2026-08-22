from apps.audit.services import log_event

class AuditMixin:
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
                    changes[field.name] = [old_val, new_val]
        log_event(
            user_id=user.id if user.is_authenticated else None,
            username_attempted=user.email,
            action=action,
            record_type=instance.__class__.__name__,
            record_id=getattr(instance, 'id', str(instance)),
            ip_address=getattr(self.request, 'audit_ip', None),
            session_id=getattr(self.request, 'audit_session', None),
            field_changes=changes,
        )