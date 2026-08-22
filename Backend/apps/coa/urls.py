from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import COAViewSet

router = DefaultRouter()
router.register(r'coa', COAViewSet)

urlpatterns = [
    path('', include(router.urls)),
]