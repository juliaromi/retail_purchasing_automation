from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from .models import User, Shop, Category
from .serializers import UserSerializer, ShopSerializer, CategorySerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
