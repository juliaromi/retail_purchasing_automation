from rest_framework.routers import DefaultRouter

from .views import UserViewSet, ShopViewSet, CategoryViewSet

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('shops', ShopViewSet)
router.register('categories', CategoryViewSet)

urlpatterns = router.urls
