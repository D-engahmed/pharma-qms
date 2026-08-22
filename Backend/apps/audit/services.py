from .models import AuditLog
from django.utils import timezone


def log_audit(
    user_id,
    username,
    action_type,
    module,
    entity_type='',
    entity_id='',
    before_values=None,
    after_values=None,
    ip_address=None,
    session_id='',
    description='',
    user_agent=''
):
    """
    Create an immutable audit log entry.
    
    Args:
        user_id: UUID of the user performing the action
        username: Email/username of the user (snapshot)
        action_type: Action type from ACTION_CHOICES
        module: Module/app name
        entity_type: Type of entity affected
        entity_id: ID of entity affected
        before_values: JSON of values before change
        after_values: JSON of values after change
        ip_address: IP address of the request
        session_id: Session ID
        description: Human-readable description
        user_agent: User agent string
    """
    return AuditLog.objects.create(
        user_id=user_id,
        username=username,
        action_type=action_type,
        module=module,
        entity_type=entity_type,
        entity_id=str(entity_id),
        before_values=before_values,
        after_values=after_values,
        ip_address=ip_address,
        session_id=session_id or '',
        description=description,
        user_agent=user_agent,
        timestamp=timezone.now()
    )


def log_event(
    user_id,
    username,
    action,
    record_type,
    record_id,
    ip_address=None,
    session_id='',
    field_changes=None,
    reason=''
):
    """Bridge function for AuditMixin compatibility"""
    verb_map = {'CREATE': 'CREATED', 'UPDATE': 'UPDATED', 'DELETE': 'DELETED'}
    verb = verb_map.get(action, action)
    
    before_values = None
    after_values = field_changes
    
    if field_changes and all(
        isinstance(v, (list, tuple)) and len(v) == 2 
        for v in field_changes.values()
    ):
        before_values = {k: v[0] for k, v in field_changes.items()}
        after_values = {k: v[1] for k, v in field_changes.items()}
    
    return log_audit(
        user_id=user_id,
        username=username,
        action_type=f"{record_type.upper()}_{verb}",
        module=record_type.lower(),
        entity_type=record_type,
        entity_id=record_id,
        before_values=before_values,
        after_values=after_values,
        ip_address=ip_address,
        session_id=session_id,
        description=reason
    )