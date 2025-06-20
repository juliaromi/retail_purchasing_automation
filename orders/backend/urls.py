from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (UserViewSet, ShopViewSet, CategoryViewSet, ModelViewSet, ProductInfoViewSet,
                    ParameterViewSet, ProductParameterViewSet, OrderViewSet, OrderItemViewSet, ContactViewSet,
                    ProductViewSet, CartContainsViewSet, UserDeliveryDetailsViewSet, DeliveryAddressViewSet,
                    OrderConfirmationViewSet)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('shops', ShopViewSet)
router.register('categories', CategoryViewSet)
router.register('models', ModelViewSet)
router.register('products-info', ProductInfoViewSet)
router.register('parameter_names', ParameterViewSet)
router.register('product_parameters', ProductParameterViewSet)
router.register('orders', OrderViewSet, basename='orders')
router.register('order_items', OrderItemViewSet)
router.register('contacts', ContactViewSet, basename='contact')
router.register('product-list', ProductViewSet, basename='product-list')
router.register('cart-contains', CartContainsViewSet, basename='cart-contains')
router.register('user-delivery-details', UserDeliveryDetailsViewSet, basename='user-delivery-details')
router.register('delivery-address', DeliveryAddressViewSet, basename='delivery-address')
router.register('order-confirmation', OrderConfirmationViewSet, basename='order-confirmation')

urlpatterns = [
    path('', include(router.urls)),
]
