from collections import defaultdict

from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import AllowAllUsersModelBackend
from django.core.mail import send_mail
from django.http import HttpResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from .filters import ProductListFilter
from .models import User, Shop, Category, Model, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Contact, \
    DeliveryAddress
from .permissions import IsAdminOrReadOnly
from .serializers import UserSerializer, ShopSerializer, CategorySerializer, ModelSerializer, ProductInfoSerializer, \
    ParameterSerializer, ProductParameterSerializer, OrderSerializer, OrderItemSerializer, ContactSerializer, \
    ProductListSerializer, CartContainsSerializer, DeliveryAddressSerializer, UserDeliveryDetailsSerializer, \
    ConfirmOrderSerializer, OrderHistorySerializer, CertainProductSerializer


class UserViewSet(ModelViewSet):
    """
    CRUD API for user management.
    Requires admin privileges (IsAdminUser).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    #permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]


class RegisterView(generics.CreateAPIView):
    """
    Implementation of an endpoint for user registration via POST request
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class ProductViewSet(ReadOnlyModelViewSet):
    """
    The API endpoint provides certain product or list of products with details:
    name, quantity, price, shop, category, parameters.
    List of products supports filtering and search. Read-only.
    """
    queryset = ProductParameter.objects.select_related(
        'product_info__model__category',
        'product_info__shop',
        'parameter'
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
    lookup_field = 'product_info__id'
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.values(
            'product_info__product_name',
            'product_info__quantity',
            'product_info__price',
            'product_info__shop__name',
            'product_info__model__name',
            'product_info__model__category__name',
            'parameter__name',
            'value'
        )

    def list(self, request, *args, **kwargs):
        """
        Viewing list of products
        """
        queryset = self.filter_queryset(self.get_queryset())

        parameters_dict = defaultdict(dict)
        unique_products = []
        seen_products = set()

        for product in queryset:
            product_name = product.get('product_info__product_name')
            param_name = product.get('parameter__name')
            param_value = product.get('value')
            parameters_dict[product_name][param_name] = param_value

            if product_name not in seen_products:
                seen_products.add(product_name)
                unique_products.append(product)

        serializer = self.get_serializer(
            unique_products,
            many=True,
            context={'parameter_dict': parameters_dict}
        )

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Viewing certain product
        """
        product_info_id = self.kwargs.get(self.lookup_url_kwarg)

        queryset = ProductParameter.objects.select_related(
            'product_info__model__category',
            'product_info__shop',
            'parameter'
        ).filter(product_info__id=product_info_id)

        if not queryset.exists():
            return Response({'detail': 'Not found'}, status=404)

        first_item = queryset.first()

        param_dict = {}
        for param in queryset:
            param_dict[param.parameter.name] = param.value

        data = {
             'product_name': first_item.product_info.product_name,
            'quantity': first_item.product_info.quantity,
            'price': first_item.product_info.price,
            'shop': first_item.product_info.shop.name,
            'model': first_item.product_info.model.name,
            'category': first_item.product_info.model.category.name,
            'parameters': param_dict
        }

        serializer = CertainProductSerializer(data)
        return Response(serializer.data)


class CartContainsViewSet(ModelViewSet):
    """
    Manages the current user's cart items: adding, removing, and updating quantities.
    """
    serializer_class = CartContainsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve user's cart
        """
        order = Order.objects.filter(user=self.request.user, status=Order.OrderStatus.CREATED).first()
        if order:
            return OrderItem.objects.filter(order=order)
        else:
            return OrderItem.objects.none()

    def create(self, request):
        """
        Adding products to user's cart
        """
        user = request.user
        product_id = request.data.get('product')
        quantity_required = int(request.data.get('quantity', 1))

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
        """
        Deleting products from user's cart
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'], url_path='decrease')
    def decrease_quantity(self, request, pk=None):
        """
        Decreasing product's quantity in user's cart
        """
        instance = self.get_object()
        amount = int(request.data.get('amount', 1))

        if amount < 1:
            return Response({'error': 'Amount must be bigger then 0'}, status=status.HTTP_400_BAD_REQUEST)
        if instance.quantity <= amount:
            instance.delete()
            return Response({'detail': 'Product removed from cart'}, status=status.HTTP_204_NO_CONTENT)

        instance.quantity -= amount
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='increase')
    def increase_quantity(self, request, pk=None):
        """
        Increasing product's quantity in user's cart
        """
        instance = self.get_object()
        amount = int(request.data.get('amount', 1))

        if amount < 1:
            return Response({'error': 'Amount must be bigger then 0'}, status=status.HTTP_400_BAD_REQUEST)
        if instance.quantity + amount > instance.product.quantity:
            return Response({'error': f'Quantity bigger then available: {instance.product.quantity}'},
                            status=status.HTTP_400_BAD_REQUEST)

        instance.quantity += amount
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ContactViewSet(ModelViewSet):
    """
    API endpoint for creating, updating, and deleting contacts of the currently authenticated user
    """
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


class DeliveryAddressViewSet(ModelViewSet):
    """
    API endpoint for creating, updating, and deleting the delivery address of the currently authenticated user
    """
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
    """
    Admin endpoint for viewing users' delivery address information
    """
    queryset = User.objects.all()
    serializer_class = UserDeliveryDetailsSerializer
    permission_classes = [IsAdminUser]


class OrderViewSet(ModelViewSet):
    """
    ViewSet for managing user orders
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, status=Order.OrderStatus.CREATED)

    def get_serializer_class(self):
        if self.action == 'history':
            return OrderHistorySerializer
        return OrderSerializer

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


class OrderConfirmationViewSet(viewsets.ViewSet):
    """
    ViewSet for confirming user orders
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
                '',
                [contact.value],
                fail_silently=False,
            )
        elif contact.type == 'PHONE':
            print(f'Send SMS to {contact.value}: Order {order.id} confirmed.')

        admin_emails = User.objects.filter(is_staff=True).values_list('login', flat=True)
        send_mail(
            'Order Confirmation by User',
            f'User {request.user.login} has been confirmed order {order.id}.',
            '',
            list(admin_emails),
            fail_silently=False,
        )

        order.status = Order.OrderStatus.CONFIRMED
        order.save()

        return Response({'message': 'Order confirmed'}, status=200)


@swagger_auto_schema(auto_schema=None)
class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


@swagger_auto_schema(auto_schema=None)
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ModelViewSet(ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer

    @swagger_auto_schema(auto_schema=None)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ProductInfoViewSet(ModelViewSet):
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ParameterViewSet(ModelViewSet):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer

    @swagger_auto_schema(auto_schema=None)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ProductParameterViewSet(ModelViewSet):
    queryset = ProductParameter.objects.all()
    serializer_class = ProductParameterSerializer

    @swagger_auto_schema(auto_schema=None)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    @swagger_auto_schema(auto_schema=None)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
