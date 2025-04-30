import re

from rest_framework import serializers

from .models import User, Shop, Category, Model, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Contact


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer
    """
    class Meta:
        model = User
        fields = ['name', 'lastname', 'login', 'password', 'is_staff', 'is_superuser', 'created_at']
        read_only_fields = ['created_at', 'is_staff', 'is_superuser']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, value):
        if not value.get('name'):
            raise serializers.ValidationError('Name cannot be empty')
        if not value.get('lastname'):
            raise serializers.ValidationError('Lastname cannot be empty')
        if not value.get('login'):
            raise serializers.ValidationError('Login cannot be empty')
        if User.objects.filter(login=value.get('login')).exists():
            raise serializers.ValidationError('The login already exist')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create_user(password=password, **validated_data)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        instance.set_password(password)
        instance.save()
        return instance


class ShopSerializer(serializers.ModelSerializer):
    """
    Shop serializer
    """
    class Meta:
        model = Shop
        fields = ['name', 'site']


class CategorySerializer(serializers.ModelSerializer):
    """
    Category serializer
    """
    shops = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all(), many=True, write_only=True)
    shops_names = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['name', 'shops', 'shops_names']

    def get_shops_names(self, data):
        return [shop.name for shop in data.shops.all()]

    def create(self, validated_data):
        shops = validated_data.pop('shops', [])
        category = Category.objects.create(**validated_data)
        category.shops.set(shops)
        return category


class ModelSerializer(serializers.ModelSerializer):
    """
    Model serializer
    """
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Model
        fields = ['name', 'category', 'category_name']


class ProductInfoSerializer(serializers.ModelSerializer):
    """
    Product info serializer
    """
    model = serializers.PrimaryKeyRelatedField(queryset=Model.objects.all(), write_only=True)
    model_name = serializers.CharField(source='model.name', read_only=True)
    shop = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all(), write_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)

    class Meta:
        model = ProductInfo
        fields = ['product_name', 'model', 'model_name', 'shop', 'shop_name', 'quantity', 'price', 'rrp']

    def validate(self, value):
        if ProductInfo.objects.filter(product_name=value.get('product_name'), shop=value.get('shop')).exists():
            raise serializers.ValidationError('The product already exist')
        return value


class ParameterSerializer(serializers.ModelSerializer):
    """
    Parameter serializer
    """

    class Meta:
        model = Parameter
        fields = ['name', ]


class ProductParameterSerializer(serializers.ModelSerializer):
    """
    Product parameter serializer
    """
    product_info = serializers.PrimaryKeyRelatedField(queryset=ProductInfo.objects.all(), write_only=True)
    product_name = serializers.CharField(source='product_info.product_name', read_only=True)
    parameter = serializers.PrimaryKeyRelatedField(queryset=Parameter.objects.all(), write_only=True)
    parameter_name = serializers.CharField(source='parameter.name', read_only=True)

    class Meta:
        model = ProductParameter
        fields = ['product_info', 'product_name', 'parameter', 'parameter_name', 'value']

    def validate(self, value):
        if ProductParameter.objects.filter(
                product_info=value.get('product_info'),
                parameter=value.get('parameter'),
                value=value.get('value'),
        ).exists():
            raise serializers.ValidationError('The product parameter already exist')
        return value


class OrderSerializer(serializers.ModelSerializer):
    """
    Order serializer
    """
    user_login = serializers.EmailField(source='user.login', read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Order
        fields = ['user_login', 'user', 'created_at', 'status', 'order_total']
        read_only_fields = ['created_at', 'order_total']


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Order items serializer
    """
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    product = serializers.PrimaryKeyRelatedField(queryset=ProductInfo.objects.all(), write_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    shop = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all(), write_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'product_name', 'shop', 'shop_name', 'quantity']


class ContactSerializer(serializers.ModelSerializer):
    """
    Contacts serializer
    """
    user_login = serializers.EmailField(source='user.login', read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Contact
        fields = ['user_login', 'user', 'type', 'value']

    def validate(self, value):
        contact_type = value.get('type')
        contact_value = value.get('value')
        if Contact.objects.filter(type=contact_type,
                                  value=contact_value).exists():
            raise serializers.ValidationError('The contact is linked to another user’s account')
        if contact_type == 'PHONE':
            if not re.match(r'^[+8]\d{10,11}$', contact_value):
                raise serializers.ValidationError('Phone number is invalid')
        elif contact_type == 'EMAIL':
            if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$', contact_value):
                raise serializers.ValidationError('Email is invalid')
        return value
