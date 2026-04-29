from rest_framework.routers import DefaultRouter
from .views import DealViewSet

router = DefaultRouter()
router.register('', DealViewSet)

urlpatterns = router.urls