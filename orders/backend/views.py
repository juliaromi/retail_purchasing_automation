from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import AllowAllUsersModelBackend
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from .filters import ProductListFilter
from .models import User, Shop, Category, Model, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Contact, \
    DeliveryAddress
from .serializers import UserSerializer, ShopSerializer, CategorySerializer, ModelSerializer, ProductInfoSerializer, \
    ParameterSerializer, ProductParameterSerializer, OrderSerializer, OrderItemSerializer, ContactSerializer, \
    ProductListSerializer, CartContainsSerializer, DeliveryAddressSerializer, UserDeliveryDetailsSerializer, \
    ConfirmOrderSerializer, OrderHistorySerializer


class UserViewSet(ModelViewSet):
    """
    CRUD API for user management.
    Requires admin privileges (IsAdminUser).
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class RegisterView(generics.CreateAPIView):
    """
    Implementation of an endpoint for user registration via POST request
    """

    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ModelViewSet(ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer


class ProductInfoViewSet(ModelViewSet):
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer


class ParameterViewSet(ModelViewSet):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer


class ProductParameterViewSet(ModelViewSet):
    queryset = ProductParameter.objects.all()
    serializer_class = ProductParameterSerializer


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'history':
            return OrderHistorySerializer
        return OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, status=Order.OrderStatus.CREATED)

    @action(detail=False, methods=['get'], url_path='user-cart')
    def user_cart(self, request):
        order = self.get_queryset().first()
        if not order:
            return Response({'detail': 'order is empty'}, status=404)
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='history')
    def history(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class ContactViewSet(ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied('No permission to edit contacts')

    def perform_destroy(self, instance):
        if instance.user == self.request.user:
            instance.delete()
        else:
            raise PermissionDenied('No permission to delete contacts')


class ProductListViewSet(ModelViewSet):
    queryset = ProductParameter.objects.select_related('product_info__model__category', 'parameter').values(
        'product_info__product_name',
        'product_info__quantity',
        'product_info__price',
        'product_info__shop__name',
        'product_info__model__name',
        'product_info__model__category__name',
        'parameter__name',
        'value'
    )
    serializer_class = ProductListSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductListFilter
    search_fields = [
        'product_info__product_name',
        'product_info__shop__name',
        'product_info__model__name',
        'product_info__model__category__name',
    ]


class CartContainsViewSet(ModelViewSet):
    serializer_class = CartContainsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        order = Order.objects.filter(user=self.request.user, status=Order.OrderStatus.CREATED).first()
        if order:
            return OrderItem.objects.filter(order=order)
        else:
            return OrderItem.objects.none()

    def create(self, request):
        user = request.user
        product_id = request.data.get('product')
        quantity_required = request.data.get('quantity', 1)

        if not product_id:
            return Response({'error': 'Product id is required'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(ProductInfo, id=product_id)

        if quantity_required > product.quantity:
            return Response({'error': f'Quantity bigger then available: {product.quantity}'},
                            status=status.HTTP_400_BAD_REQUEST)
        if quantity_required < 1:
            return Response({'error': f'Quantity must be bigger then 0'},
                            status=status.HTTP_400_BAD_REQUEST)

        order, _ = Order.objects.get_or_create(user=user, status=Order.OrderStatus.CREATED)

        order_item, created = OrderItem.objects.get_or_create(order=order, product=product, shop=product.shop,
                                                              defaults={'quantity': quantity_required})

        if not created:
            order_item.quantity += quantity_required
            if order_item.quantity > product.quantity:
                return Response({'error': f'Quantity bigger then available: {product.quantity}'},
                                status=status.HTTP_400_BAD_REQUEST)
            order_item.save()


        serializer = self.get_serializer(order_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'], url_path='decrease')
    def decrease_quantity(self, request, pk=None):
        instance = self.get_object()
        amount = request.data.get('amount', 1)

        if amount < 1:
            return Response({'error': 'Amount must be bigger then 0'}, status=status.HTTP_400_BAD_REQUEST)
        if instance.quantity <= amount:
            instance.delete()
            return Response({'detail': 'Product removed from cart'}, status=status.HTTP_204_NO_CONTENT)

        instance.quantity -= amount
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class DeliveryAddressViewSet(ModelViewSet):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied('No permission to edit delivery address')

    def perform_destroy(self, instance):
        if instance.user == self.request.user:
            instance.delete()
        else:
            raise PermissionDenied('No permission to delete delivery address')


class UserDeliveryDetailsViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDeliveryDetailsSerializer
    permission_classes = [IsAdminUser]


class OrderConfirmationViewSet(viewsets.ViewSet):
    """
    ViewSet for confirming an order
    """

    @action(detail=False, methods=['post'], url_path='confirm-order')
    def confirm_order(self, request):
        serializer = ConfirmOrderSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order = serializer.validated_data['order']
        contact = serializer.validated_data['contact']

        if contact.type == 'EMAIL':
            send_mail(
                'Order Confirmation',
                f'Order {order.id} has been confirmed.',
                'shop_account@gmail.com',
                [contact.value],
                fail_silently=False,
            )
        elif contact.type == 'PHONE':
            print(f'Send SMS to {contact.value}: Order {order.id} confirmed.')

        order.status = Order.OrderStatus.CONFIRMED
        order.save()

        return Response({'message': 'Order confirmed'}, status=200)
