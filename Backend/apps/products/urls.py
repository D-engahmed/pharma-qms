from rest_framework.routers import DefaultRouter
from .views import ProductSampleViewSet

router = DefaultRouter()
router.register(r'product-samples', ProductSampleViewSet, basename='productsample')
urlpatterns = router.urls