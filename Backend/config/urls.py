from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
    path('api/v1/', include('apps.materials.urls')),
    path('api/v1/', include('apps.packaging.urls')),
    path('api/v1/', include('apps.sampling.urls')),
    path('api/v1/', include('apps.products.urls')),
    path('api/v1/', include('apps.coa.urls')),
]