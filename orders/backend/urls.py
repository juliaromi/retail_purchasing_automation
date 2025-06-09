from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (UserViewSet, ShopViewSet, CategoryViewSet, ModelViewSet, ProductInfoViewSet,
                    ParameterViewSet, ProductParameterViewSet, OrderViewSet, OrderItemViewSet, ContactViewSet,
                    ProductListViewSet, CartContainsViewSet, UserDeliveryDetailsViewSet)

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
router.register('product_list', ProductListViewSet)
router.register('cart_contains', CartContainsViewSet)
router.register('user-delivery-details', UserDeliveryDetailsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
