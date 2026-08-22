from django.utils import timezone
from django.conf import settings
from django.contrib.auth import logout
from datetime import timedelta
from .models import UserSession


class SessionActivityMiddleware:
    """Middleware to track session activity and enforce timeout"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated and request.session.session_key:
            try:
                user_session = UserSession.objects.get(
                    session_key=request.session.session_key
                )
                
                # Check if session is still valid
                if not user_session.is_active:
                    logout(request)
                    return self.get_response(request)
                
                # Update last activity and expiry
                user_session.last_activity_at = timezone.now()
                user_session.expires_at = timezone.now() + timedelta(
                    seconds=settings.SESSION_COOKIE_AGE
                )
                user_session.save(update_fields=['last_activity_at', 'expires_at'])
                
            except UserSession.DoesNotExist:
                # Session not found in database, but exists in Django session
                # Create it
                UserSession.objects.create(
                    user=request.user,
                    session_key=request.session.session_key,
                    expires_at=timezone.now() + timedelta(
                        seconds=settings.SESSION_COOKIE_AGE
                    ),
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
        
        return self.get_response(request)