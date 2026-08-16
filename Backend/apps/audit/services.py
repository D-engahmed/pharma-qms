from .models import AuditLog

_ACTION_VERB_MAP = {'CREATE': 'CREATED', 'UPDATE': 'UPDATED', 'DELETE': 'DELETED'}

def log_event_sync(user_id, username_attempted, action, record_type, record_id,
                    ip_address, session_id, field_changes=None, reason=''):
    """Bridges AuditMixin's generic CRUD hook onto the real AuditLog schema."""
    verb = _ACTION_VERB_MAP.get(action, action)
    before_values, after_values = None, field_changes
    if field_changes and all(isinstance(v, (list, tuple)) and len(v) == 2 for v in field_changes.values()):
        # mixins.py sends {field: [old, new]} — split into the model's actual columns
        before_values = {k: v[0] for k, v in field_changes.items()}
        after_values = {k: v[1] for k, v in field_changes.items()}
    AuditLog.objects.create(
        user_id=user_id,
        username=username_attempted,
        action_type=f"{record_type.upper()}_{verb}",
        module=record_type,
        entity_type=record_type,
        entity_id=str(record_id),
        before_values=before_values,
        after_values=after_values,
        description=reason,
        ip_address=ip_address,
        session_id=session_id,
    )

log_event = log_event_sync

def log_audit(user_id, username, action_type, module, entity_type='', entity_id='',
              before_values=None, after_values=None, ip_address=None, session_id=None,
              description=''):
    AuditLog.objects.create(
        user_id=user_id, username=username, action_type=action_type, module=module,
        entity_type=entity_type, entity_id=entity_id, before_values=before_values,
        after_values=after_values, ip_address=ip_address, session_id=session_id,
        description=description,
    )