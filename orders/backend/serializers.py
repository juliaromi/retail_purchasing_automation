import re

from rest_framework import serializers

from .models import User, Shop, Category, Model, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Contact, \
    DeliveryAddress


class UserSerializer(serializers.ModelSerializer):
    """
    User model serializer with password handling and data validation.
    """

    class Meta:
        model = User
        fields = [
            'first_name',
            'middle_name',
            'last_name',
            'login',
            'password',
            'is_staff',
            'is_superuser',
            'created_at'
        ]
        read_only_fields = ['created_at', 'is_staff', 'is_superuser']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, value):
        if not value.get('first_name'):
            raise serializers.ValidationError('First name cannot be empty')
        if not value.get('last_name'):
            raise serializers.ValidationError('Last name cannot be empty')
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


class UserRegistrationResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration responses.
    Designed specifically for API responses after successful registration.
    Excludes sensitive fields and provides only safe user data.
    """

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'login', 'created_at']
        read_only_fields = fields


class ProductListSerializer(serializers.Serializer):
    """
    Serializes list of products data with grouped parameters
    """

    name = serializers.CharField(source='product_info__product_name')
    model = serializers.CharField(source='product_info__model__name')
    category = serializers.CharField(source='product_info__model__category__name')
    shop = serializers.CharField(source='product_info__shop__name')
    parameter = serializers.SerializerMethodField()
    price = serializers.DecimalField(max_digits=12, decimal_places=2, source='product_info__price')
    quantity = serializers.IntegerField(source='product_info__quantity')

    def get_parameter(self, obj):
        return self.context.get('parameter_dict', {}).get(obj['product_info__product_name'], {})


class CertainProductSerializer(serializers.Serializer):
    """
    Serializes certain product data with grouped parameters
    """

    product_name = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    shop = serializers.CharField()
    model = serializers.CharField()
    category = serializers.CharField()
    parameters = serializers.DictField()


class CartContainsSerializer(serializers.ModelSerializer):
    """
    Serializer for managing user's cart contains
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(source='product.product_name', read_only=True)
    shop = serializers.CharField(source='shop.name', read_only=True)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, source='product.price', read_only=True)
    quantity = serializers.IntegerField()
    total_sum = serializers.SerializerMethodField()

    def get_total_sum(self, obj):
        return obj.product.price * obj.quantity

    class Meta:
        model = OrderItem
        fields = ['id', 'name', 'shop', 'price', 'quantity', 'total_sum']


class DeliveryAddressSerializer(serializers.ModelSerializer):
    """
    Serializer for delivery addresses.
    Used to view, create, delete delivery address records associated with authenticated user.
    """

    class Meta:
        model = DeliveryAddress
        fields = ['id', 'city', 'street', 'building', 'block', 'structure', 'apartment']


class ContactSerializer(serializers.ModelSerializer):
    """
    Serializer for validating and representing user contact information (phone or email)
    """

    class Meta:
        model = Contact
        fields = ['id', 'type', 'value']

    def validate(self, attrs):
        contact_type = attrs.get('type')
        contact_value = attrs.get('value')

        if not contact_type:
            raise serializers.ValidationError("Contact type is required")
        if not contact_value:
            raise serializers.ValidationError("Contact value is required")

        existing = Contact.objects.filter(type=contact_type, value=contact_value)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError('The contact is already linked')

        if contact_type == 'PHONE':
            if not re.match(r'^[+8]\d{10,11}$', contact_value):
                raise serializers.ValidationError('Phone number is invalid')
        elif contact_type == 'EMAIL':
            if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$', contact_value):
                raise serializers.ValidationError('Email is invalid')
        return attrs


class UserDeliveryDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying user delivery-related information.
    Admin use and read-only.
    """

    user = serializers.SerializerMethodField()
    contacts = ContactSerializer(source='contact_set', many=True, read_only=True)
    delivery_address = DeliveryAddressSerializer(source='deliveryaddress_set', many=True, read_only=True)

    class Meta:
        model = User
        fields = ['user', 'contacts', 'delivery_address']

    def get_user(self, obj):
        user = [obj.first_name]
        if obj.middle_name:
            user.append(obj.middle_name)
        user.append(obj.last_name)

        return ' '.join(user)


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
    items = CartContainsSerializer(source='orderitem_set', many=True, read_only=True)
    order_total = serializers.SerializerMethodField()
    delivery_address = serializers.PrimaryKeyRelatedField(queryset=DeliveryAddress.objects.none())

    def get_order_total(self, obj):
        return obj.order_total

    class Meta:
        model = Order
        fields = ['user_login', 'user', 'created_at', 'status', 'items', 'order_total', 'delivery_address']
        read_only_fields = ['created_at', 'items', 'order_total']

    def validate(self, data):
        user = data.get('user') or self.instance.user
        delivery_address = data.get('delivery_address')
        if delivery_address and delivery_address.user != user:
            raise serializers.ValidationError('Delivery address must belong to user')
        return data


class OrderHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    order_total = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_order_total(self, obj):
        return obj.order_total

    def get_status(self, obj):
        return obj.OrderStatus(obj.status).name.capitalize()

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'order_total', 'status']
        read_only_fields = fields


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


class ConfirmOrderSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    contact_id = serializers.IntegerField()

    def validate(self, data):
        user = self.context.get('request').user
        order = Order.objects.filter(id=data.get('order_id'), user=user, status=Order.OrderStatus.CREATED).first()
        if not order:
            raise serializers.ValidationError('Order not found')

        if not order.delivery_address:
            raise serializers.ValidationError('Delivery address is required')

        contact = Contact.objects.filter(id=data.get('contact_id'), user=user).first()
        if not contact:
            raise serializers.ValidationError('Contact not found')

        data['order'] = order
        data['contact'] = contact
        return data
