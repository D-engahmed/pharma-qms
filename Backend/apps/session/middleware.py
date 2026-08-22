from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import UserSession

class SessionActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if request.user.is_authenticated and request.session.session_key:
            try:
                user_session = UserSession.objects.get(session_key=request.session.session_key)
                if not user_session.is_active:
                    logout(request)
                else:
                    user_session.last_activity_at = timezone.now()
                    user_session.expires_at = timezone.now() + timedelta(seconds=settings.SESSION_COOKIE_AGE)
                    user_session.save(update_fields=['last_activity_at', 'expires_at'])
            except UserSession.DoesNotExist:
                pass
        return self.get_response(request)