from rest_framework.routers import DefaultRouter
from .views import  PackagingViewSet

router = DefaultRouter()
router.register(r'packaging', PackagingViewSet, basename='packaging')
urlpatterns = router.urls