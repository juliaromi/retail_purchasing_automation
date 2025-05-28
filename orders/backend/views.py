from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import AllowAllUsersModelBackend
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from .filters import ProductListFilter
from .models import User, Shop, Category, Model, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Contact
from .serializers import UserSerializer, ShopSerializer, CategorySerializer, ModelSerializer, ProductInfoSerializer, \
    ParameterSerializer, ProductParameterSerializer, OrderSerializer, OrderItemSerializer, ContactSerializer, \
    ProductListSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegisterView(generics.CreateAPIView):
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


class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class ContactViewSet(ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


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
