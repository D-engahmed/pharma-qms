from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/', include('apps.materials.urls')),
    path('api/v1/', include('apps.sampling.urls')),
    path('api/v1/', include('apps.analysis.urls')),
    path('api/v1/', include('apps.coa.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)