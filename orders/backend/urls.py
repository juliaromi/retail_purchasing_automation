from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (UserViewSet, OrderViewSet, ContactViewSet, ProductViewSet, CartContainsViewSet,
                    UserDeliveryDetailsViewSet, DeliveryAddressViewSet, OrderConfirmationViewSet)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('orders', OrderViewSet, basename='orders')
router.register('contacts', ContactViewSet, basename='contact')
router.register('product-list', ProductViewSet, basename='product-list')
router.register('cart-contains', CartContainsViewSet, basename='cart-contains')
router.register('user-delivery-details', UserDeliveryDetailsViewSet, basename='user-delivery-details')
router.register('delivery-address', DeliveryAddressViewSet, basename='delivery-address')
router.register('order-confirmation', OrderConfirmationViewSet, basename='order-confirmation')

urlpatterns = [
    path('', include(router.urls)),
]
