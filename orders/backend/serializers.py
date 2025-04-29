from rest_framework import serializers

from .models import User, Shop, Category


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
    shops = ShopSerializer(many=True, read_only=False)

    class Meta:
        model = Category
        fields = ['name', 'shops']
