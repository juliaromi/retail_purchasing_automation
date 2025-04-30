from rest_framework.routers import DefaultRouter

from .views import (UserViewSet, ShopViewSet, CategoryViewSet, ModelViewSet, ProductInfoViewSet,
                    ParameterViewSet, ProductParameterViewSet, OrderViewSet, OrderItemViewSet, ContactViewSet)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('shops', ShopViewSet)
router.register('categories', CategoryViewSet)
router.register('models', ModelViewSet)
router.register('products_info', ProductInfoViewSet)
router.register('parameter_names', ParameterViewSet)
router.register('product_parameters', ProductParameterViewSet)
router.register('orders', OrderViewSet)
router.register('order_items', OrderItemViewSet)
router.register('contacts', ContactViewSet)

urlpatterns = router.urls
