from django.utils.timezone import now
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
                user_session.last_activity_at = now()
                user_session.expires_at = now() + timedelta(seconds=settings.SESSION_COOKIE_AGE)
                user_session.save(update_fields=['last_activity_at', 'expires_at'])
            except UserSession.DoesNotExist:
                pass
        response = self.get_response(request)
        return response