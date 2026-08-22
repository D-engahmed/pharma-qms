from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialReleaseViewSet

router = DefaultRouter()
router.register(r'releases', MaterialReleaseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]