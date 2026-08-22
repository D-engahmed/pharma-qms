from .models import Notification

def create_notification(target_role, title, message):
    return Notification.objects.create(target_role=target_role, title=title, message=message)