from rest_framework import serializers

from .models import User, Shop, Category


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer
    """
    class Meta:
        model = User
        fields = ['name', 'lastname', 'login', 'password', 'is_staff', 'is_superuser', 'created_at']
        read_only_fields = ['created_at']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        user.set_password(password)
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
    shops = ShopSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['name', 'shops']
