from .models import AuditLog

def log_audit(user_id, username, action_type, module, entity_type='', entity_id='', before_values=None, after_values=None, ip_address=None, session_id='', description=''):
    return AuditLog.objects.create(
        user_id=user_id, username=username, action_type=action_type, module=module,
        entity_type=entity_type, entity_id=str(entity_id), before_values=before_values,
        after_values=after_values, ip_address=ip_address, session_id=session_id or '',
        description=description
    )

def log_event(user_id, username, action, record_type, record_id, ip_address=None, session_id='', field_changes=None, reason=''):
    verb_map = {'CREATE': 'CREATED', 'UPDATE': 'UPDATED', 'DELETE': 'DELETED'}
    verb = verb_map.get(action, action)
    before_values = None
    after_values = field_changes
    if field_changes and all(isinstance(v, (list, tuple)) and len(v) == 2 for v in field_changes.values()):
        before_values = {k: v[0] for k, v in field_changes.items()}
        after_values = {k: v[1] for k, v in field_changes.items()}
    return log_audit(
        user_id=user_id, username=username, action_type=f"{record_type.upper()}_{verb}",
        module=record_type.lower(), entity_type=record_type, entity_id=record_id,
        before_values=before_values, after_values=after_values, ip_address=ip_address,
        session_id=session_id, description=reason
    )