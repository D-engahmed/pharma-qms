from celery import shared_task
from .services import log_event_sync

@shared_task
def log_event(user_id, username_attempted, action, record_type, record_id, ip_address, session_id, field_changes=None, reason=''):
    log_event_sync(user_id, username_attempted, action, record_type, record_id, ip_address, session_id, field_changes, reason)